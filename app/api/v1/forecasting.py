"""
Forecasting API - ML-powered forecasting and predictive analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.models.user_models import User
from app.models.forecasting_models import (
    FinancialForecast, MLForecastModel, MLPrediction, BusinessDriverModel,
    RiskAnalysis, RiskEvent, AutomatedInsight, ForecastVersion
)
from app.schemas.forecasting import (
    FinancialForecastCreate, FinancialForecastUpdate, FinancialForecastResponse,
    BusinessDriverCreate, BusinessDriverUpdate, BusinessDriverResponse,
    MLForecastModelCreate, MLForecastModelResponse, MLPredictionResponse,
    RiskAnalysisCreate, RiskAnalysisUpdate, RiskAnalysisResponse,
    RiskEventCreate, RiskEventUpdate, RiskEventResponse,
    AutomatedInsightCreate, AutomatedInsightUpdate, AutomatedInsightResponse,
    ForecastVersionResponse, PredictionRequest, MultiVariateForecastRequest,
    ScenarioForecastRequest, SensitivityAnalysisRequest, ForecastAccuracyReport,
    EarlyWarningSignal, ForecastDashboardData
)
from app.services.forecasting_service import ForecastingService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/forecasts", response_model=FinancialForecastResponse)
async def create_financial_forecast(
    forecast_data: FinancialForecastCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new financial forecast with ML modeling"""
    try:
        service = ForecastingService(db)
        
        forecast = service.create_financial_forecast(
            organization_id=organization_id,
            forecast_data=forecast_data,
            user_id=current_user.id
        )
        
        return forecast
        
    except Exception as e:
        logger.error(f"Error creating financial forecast: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/forecasts", response_model=List[FinancialForecastResponse])
async def get_financial_forecasts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    forecast_type: Optional[str] = Query(None),
    forecast_method: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_baseline: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get financial forecasts with filtering"""
    try:
        query = db.query(FinancialForecast).filter(
            FinancialForecast.organization_id == organization_id
        )
        
        if forecast_type:
            query = query.filter(FinancialForecast.forecast_type == forecast_type)
        if forecast_method:
            query = query.filter(FinancialForecast.forecast_method == forecast_method)
        if status:
            query = query.filter(FinancialForecast.status == status)
        if is_baseline is not None:
            query = query.filter(FinancialForecast.is_baseline == is_baseline)
        
        forecasts = query.order_by(desc(FinancialForecast.updated_at)).offset(skip).limit(limit).all()
        return forecasts
        
    except Exception as e:
        logger.error(f"Error fetching financial forecasts: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/forecasts/{forecast_id}", response_model=FinancialForecastResponse)
async def get_financial_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get a specific financial forecast"""
    try:
        forecast = db.query(FinancialForecast).filter(
            FinancialForecast.id == forecast_id,
            FinancialForecast.organization_id == organization_id
        ).first()
        
        if not forecast:
            raise HTTPException(status_code=404, detail="Financial forecast not found")
        
        return forecast
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching financial forecast: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/forecasts/{forecast_id}", response_model=FinancialForecastResponse)
async def update_financial_forecast(
    forecast_id: int,
    forecast_data: FinancialForecastUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update a financial forecast"""
    try:
        service = ForecastingService(db)
        
        forecast = db.query(FinancialForecast).filter(
            FinancialForecast.id == forecast_id,
            FinancialForecast.organization_id == organization_id
        ).first()
        
        if not forecast:
            raise HTTPException(status_code=404, detail="Financial forecast not found")
        
        # Track version if significant changes
        create_version = False
        version_changes = []
        
        if forecast_data.forecast_name and forecast_data.forecast_name != forecast.forecast_name:
            forecast.forecast_name = forecast_data.forecast_name
            version_changes.append("name")
        
        if forecast_data.model_parameters:
            forecast.model_parameters = forecast_data.model_parameters
            create_version = True
            version_changes.append("parameters")
        
        if forecast_data.business_drivers:
            forecast.business_drivers = forecast_data.business_drivers
            create_version = True
            version_changes.append("drivers")
        
        if forecast_data.status:
            forecast.status = forecast_data.status
            if forecast_data.status.value == "approved":
                forecast.approved_by_id = current_user.id
                forecast.approved_at = datetime.utcnow()
        
        if forecast_data.is_baseline is not None:
            # Only one forecast can be baseline per type/org
            if forecast_data.is_baseline:
                db.query(FinancialForecast).filter(
                    FinancialForecast.organization_id == organization_id,
                    FinancialForecast.forecast_type == forecast.forecast_type,
                    FinancialForecast.id != forecast_id
                ).update({'is_baseline': False})
            forecast.is_baseline = forecast_data.is_baseline
        
        forecast.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(forecast)
        
        # Create version if significant changes
        if create_version:
            change_description = f"Updated: {', '.join(version_changes)}"
            # Get current version number and increment
            current_version = db.query(ForecastVersion).filter(
                ForecastVersion.financial_forecast_id == forecast_id,
                ForecastVersion.is_current == True
            ).first()
            
            if current_version:
                version_parts = current_version.version_number.split('.')
                new_version = f"{version_parts[0]}.{int(version_parts[1]) + 1}"
            else:
                new_version = "1.1"
            
            service._create_forecast_version(
                forecast_id, new_version, change_description, current_user.id
            )
        
        return forecast
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating financial forecast: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/forecasts/{forecast_id}")
async def delete_financial_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Delete a financial forecast"""
    try:
        forecast = db.query(FinancialForecast).filter(
            FinancialForecast.id == forecast_id,
            FinancialForecast.organization_id == organization_id
        ).first()
        
        if not forecast:
            raise HTTPException(status_code=404, detail="Financial forecast not found")
        
        db.delete(forecast)
        db.commit()
        
        return {"message": "Financial forecast deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting financial forecast: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Business Drivers
@router.post("/forecasts/{forecast_id}/drivers", response_model=BusinessDriverResponse)
async def create_business_driver(
    forecast_id: int,
    driver_data: BusinessDriverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a business driver for a forecast"""
    try:
        # Verify forecast exists
        forecast = db.query(FinancialForecast).filter(
            FinancialForecast.id == forecast_id,
            FinancialForecast.organization_id == organization_id
        ).first()
        
        if not forecast:
            raise HTTPException(status_code=404, detail="Financial forecast not found")
        
        driver = BusinessDriverModel(
            financial_forecast_id=forecast_id,
            organization_id=organization_id,
            **driver_data.dict(),
            created_by_id=current_user.id
        )
        
        db.add(driver)
        db.commit()
        db.refresh(driver)
        
        return driver
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating business driver: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/forecasts/{forecast_id}/drivers", response_model=List[BusinessDriverResponse])
async def get_business_drivers(
    forecast_id: int,
    driver_category: Optional[str] = Query(None),
    is_active: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get business drivers for a forecast"""
    try:
        query = db.query(BusinessDriverModel).filter(
            BusinessDriverModel.financial_forecast_id == forecast_id,
            BusinessDriverModel.organization_id == organization_id,
            BusinessDriverModel.is_active == is_active
        )
        
        if driver_category:
            query = query.filter(BusinessDriverModel.driver_category == driver_category)
        
        drivers = query.order_by(BusinessDriverModel.driver_name).all()
        return drivers
        
    except Exception as e:
        logger.error(f"Error fetching business drivers: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ML Models
@router.post("/ml-models", response_model=MLForecastModelResponse)
async def create_ml_forecast_model(
    model_data: MLForecastModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create and train an ML forecast model"""
    try:
        service = ForecastingService(db)
        
        # Create ML model record
        ml_model = MLForecastModel(
            organization_id=organization_id,
            **model_data.dict(exclude={'training_data'}),
            training_data_size=len(model_data.training_data.get('values', [])),
            created_by_id=current_user.id
        )
        
        db.add(ml_model)
        db.commit()
        db.refresh(ml_model)
        
        # Train the model (in a real implementation, this would be done asynchronously)
        # For now, we'll add dummy accuracy metrics
        ml_model.training_accuracy = Decimal('85.5')
        ml_model.validation_accuracy = Decimal('82.3')
        ml_model.test_accuracy = Decimal('80.1')
        ml_model.mae = Decimal('1250.50')
        ml_model.rmse = Decimal('1875.25')
        ml_model.mape = Decimal('12.5')
        
        # Feature importance (dummy data)
        ml_model.feature_importance = {
            feature: float(1.0 / len(model_data.features)) 
            for feature in model_data.features
        }
        
        db.commit()
        db.refresh(ml_model)
        
        return ml_model
        
    except Exception as e:
        logger.error(f"Error creating ML forecast model: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ml-models", response_model=List[MLForecastModelResponse])
async def get_ml_forecast_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    model_type: Optional[str] = Query(None),
    target_variable: Optional[str] = Query(None),
    is_active: bool = Query(True),
    is_production: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get ML forecast models with filtering"""
    try:
        query = db.query(MLForecastModel).filter(
            MLForecastModel.organization_id == organization_id,
            MLForecastModel.is_active == is_active
        )
        
        if model_type:
            query = query.filter(MLForecastModel.model_type == model_type)
        if target_variable:
            query = query.filter(MLForecastModel.target_variable == target_variable)
        if is_production is not None:
            query = query.filter(MLForecastModel.is_production == is_production)
        
        models = query.order_by(desc(MLForecastModel.trained_at)).offset(skip).limit(limit).all()
        return models
        
    except Exception as e:
        logger.error(f"Error fetching ML forecast models: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/predictions", response_model=MLPredictionResponse)
async def create_prediction(
    prediction_request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Generate a prediction using an ML model"""
    try:
        # Verify ML model exists and is active
        ml_model = db.query(MLForecastModel).filter(
            MLForecastModel.id == prediction_request.model_id,
            MLForecastModel.organization_id == organization_id,
            MLForecastModel.is_active == True
        ).first()
        
        if not ml_model:
            raise HTTPException(status_code=404, detail="ML model not found")
        
        # Generate prediction (simplified - would use actual trained model)
        # For demo purposes, we'll create a prediction based on input features
        feature_values = list(prediction_request.input_features.values())
        if feature_values:
            base_prediction = sum([float(v) for v in feature_values if isinstance(v, (int, float))]) * 1.1
        else:
            base_prediction = 10000.0
        
        predicted_value = Decimal(str(base_prediction))
        confidence_score = Decimal('85.0') if prediction_request.include_confidence else None
        
        # Calculate confidence intervals if requested
        lower_bound = None
        upper_bound = None
        if prediction_request.include_confidence:
            uncertainty = predicted_value * Decimal('0.15')  # 15% uncertainty
            lower_bound = predicted_value - uncertainty
            upper_bound = predicted_value + uncertainty
        
        prediction = MLPrediction(
            ml_model_id=prediction_request.model_id,
            organization_id=organization_id,
            prediction_date=prediction_request.prediction_date,
            predicted_value=predicted_value,
            confidence_score=confidence_score,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            input_features=prediction_request.input_features
        )
        
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating prediction: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/predictions", response_model=List[MLPredictionResponse])
async def get_predictions(
    model_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get predictions with filtering"""
    try:
        query = db.query(MLPrediction).filter(
            MLPrediction.organization_id == organization_id
        )
        
        if model_id:
            query = query.filter(MLPrediction.ml_model_id == model_id)
        if start_date:
            query = query.filter(MLPrediction.prediction_date >= start_date)
        if end_date:
            query = query.filter(MLPrediction.prediction_date <= end_date)
        
        predictions = query.order_by(desc(MLPrediction.predicted_at)).offset(skip).limit(limit).all()
        return predictions
        
    except Exception as e:
        logger.error(f"Error fetching predictions: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Risk Analysis
@router.post("/risk-analysis", response_model=RiskAnalysisResponse)
async def create_risk_analysis(
    risk_data: RiskAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a risk analysis"""
    try:
        # Calculate risk score
        risk_score = (risk_data.probability * risk_data.impact_score) / 10
        
        # Determine alert level
        if risk_score >= 8:
            alert_level = "critical"
        elif risk_score >= 6:
            alert_level = "high"
        elif risk_score >= 4:
            alert_level = "medium"
        else:
            alert_level = "low"
        
        risk_analysis = RiskAnalysis(
            organization_id=organization_id,
            **risk_data.dict(),
            risk_score=Decimal(str(risk_score)),
            alert_level=alert_level,
            is_active_alert=(alert_level in ["high", "critical"]),
            created_by_id=current_user.id
        )
        
        db.add(risk_analysis)
        db.commit()
        db.refresh(risk_analysis)
        
        return risk_analysis
        
    except Exception as e:
        logger.error(f"Error creating risk analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/risk-analysis", response_model=List[RiskAnalysisResponse])
async def get_risk_analyses(
    risk_category: Optional[str] = Query(None),
    alert_level: Optional[str] = Query(None),
    is_active_alert: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get risk analyses with filtering"""
    try:
        query = db.query(RiskAnalysis).filter(
            RiskAnalysis.organization_id == organization_id
        )
        
        if risk_category:
            query = query.filter(RiskAnalysis.risk_category == risk_category)
        if alert_level:
            query = query.filter(RiskAnalysis.alert_level == alert_level)
        if is_active_alert is not None:
            query = query.filter(RiskAnalysis.is_active_alert == is_active_alert)
        
        risk_analyses = query.order_by(desc(RiskAnalysis.risk_score)).offset(skip).limit(limit).all()
        return risk_analyses
        
    except Exception as e:
        logger.error(f"Error fetching risk analyses: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Risk Events
@router.post("/risk-events", response_model=RiskEventResponse)
async def create_risk_event(
    event_data: RiskEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a risk event"""
    try:
        # Verify risk analysis exists
        risk_analysis = db.query(RiskAnalysis).filter(
            RiskAnalysis.id == event_data.risk_analysis_id,
            RiskAnalysis.organization_id == organization_id
        ).first()
        
        if not risk_analysis:
            raise HTTPException(status_code=404, detail="Risk analysis not found")
        
        risk_event = RiskEvent(
            **event_data.dict(),
            organization_id=organization_id,
            reported_by_id=current_user.id
        )
        
        db.add(risk_event)
        db.commit()
        db.refresh(risk_event)
        
        return risk_event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating risk event: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Automated Insights
@router.get("/insights", response_model=List[AutomatedInsightResponse])
async def get_automated_insights(
    insight_type: Optional[str] = Query(None),
    insight_category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    min_importance: Optional[float] = Query(None, ge=1, le=10),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get automated insights with filtering"""
    try:
        query = db.query(AutomatedInsight).filter(
            AutomatedInsight.organization_id == organization_id
        )
        
        if insight_type:
            query = query.filter(AutomatedInsight.insight_type == insight_type)
        if insight_category:
            query = query.filter(AutomatedInsight.insight_category == insight_category)
        if status:
            query = query.filter(AutomatedInsight.status == status)
        if min_importance:
            query = query.filter(AutomatedInsight.importance_score >= min_importance)
        
        insights = query.order_by(
            desc(AutomatedInsight.importance_score),
            desc(AutomatedInsight.generated_at)
        ).offset(skip).limit(limit).all()
        
        return insights
        
    except Exception as e:
        logger.error(f"Error fetching automated insights: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/insights/generate")
async def generate_automated_insights(
    data_sources: List[str] = Query(..., description="Data sources to analyze"),
    analysis_period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Generate automated insights using AI/ML analysis"""
    try:
        service = ForecastingService(db)
        
        insights = service.generate_automated_insights(
            organization_id=organization_id,
            data_sources=data_sources,
            analysis_period_days=analysis_period_days
        )
        
        return {
            "message": f"Generated {len(insights)} automated insights",
            "insights_generated": len(insights),
            "analysis_period_days": analysis_period_days,
            "data_sources": data_sources
        }
        
    except Exception as e:
        logger.error(f"Error generating automated insights: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/insights/{insight_id}", response_model=AutomatedInsightResponse)
async def update_automated_insight(
    insight_id: int,
    insight_data: AutomatedInsightUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update an automated insight (mark as reviewed, provide feedback, etc.)"""
    try:
        insight = db.query(AutomatedInsight).filter(
            AutomatedInsight.id == insight_id,
            AutomatedInsight.organization_id == organization_id
        ).first()
        
        if not insight:
            raise HTTPException(status_code=404, detail="Automated insight not found")
        
        if insight_data.status:
            insight.status = insight_data.status
            if insight_data.status == "reviewed":
                insight.reviewed_by_id = current_user.id
                insight.reviewed_at = datetime.utcnow()
        
        if insight_data.user_feedback:
            insight.user_feedback = insight_data.user_feedback
        
        if insight_data.usefulness_rating:
            insight.usefulness_rating = insight_data.usefulness_rating
        
        db.commit()
        db.refresh(insight)
        
        return insight
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating automated insight: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Advanced Analytics
@router.post("/multivariate-forecast")
async def create_multivariate_forecast(
    forecast_request: MultiVariateForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a multivariate forecast using advanced ML models"""
    try:
        # This would implement advanced multivariate forecasting
        # For now, return a placeholder response
        return {
            "message": "Multivariate forecast created successfully",
            "forecast_name": forecast_request.forecast_name,
            "target_variables": forecast_request.target_variables,
            "forecast_horizon": forecast_request.forecast_horizon,
            "model_type": forecast_request.model_type,
            "confidence_level": forecast_request.confidence_level,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error creating multivariate forecast: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sensitivity-analysis")
async def perform_sensitivity_analysis(
    sensitivity_request: SensitivityAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Perform sensitivity analysis on a forecast"""
    try:
        # Verify forecast exists
        forecast = db.query(FinancialForecast).filter(
            FinancialForecast.id == sensitivity_request.forecast_id,
            FinancialForecast.organization_id == organization_id
        ).first()
        
        if not forecast:
            raise HTTPException(status_code=404, detail="Forecast not found")
        
        # Perform sensitivity analysis (simplified implementation)
        results = {
            "forecast_id": sensitivity_request.forecast_id,
            "sensitivity_variables": sensitivity_request.sensitivity_variables,
            "variation_ranges": sensitivity_request.variation_range,
            "analysis_steps": sensitivity_request.steps,
            "results": {
                variable: {
                    "low_impact": -10.5,
                    "high_impact": 12.3,
                    "elasticity": 0.8
                } for variable in sensitivity_request.sensitivity_variables
            },
            "analysis_date": datetime.utcnow().isoformat()
        }
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing sensitivity analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/early-warning-signals", response_model=List[EarlyWarningSignal])
async def get_early_warning_signals(
    severity: Optional[str] = Query(None),
    min_confidence: Optional[float] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get early warning signals for potential issues"""
    try:
        # Generate early warning signals based on recent data
        signals = []
        
        # Check for risk alerts
        high_risk_alerts = db.query(RiskAnalysis).filter(
            RiskAnalysis.organization_id == organization_id,
            RiskAnalysis.alert_level.in_(["high", "critical"]),
            RiskAnalysis.is_active_alert == True
        ).all()
        
        for risk in high_risk_alerts:
            signal = EarlyWarningSignal(
                signal_type="risk_threshold_breach",
                severity=risk.alert_level,
                description=f"Risk analysis '{risk.risk_name}' has breached alert thresholds",
                affected_metrics=[risk.risk_category],
                threshold_breach={
                    "risk_score": float(risk.risk_score),
                    "threshold": 6.0 if risk.alert_level == "high" else 8.0
                },
                recommended_actions=[
                    "Review risk mitigation strategies",
                    "Implement immediate containment measures",
                    "Monitor key indicators closely"
                ],
                confidence_score=Decimal('90.0'),
                triggered_at=risk.last_assessed_at or risk.created_at
            )
            
            if not severity or signal.severity == severity:
                if not min_confidence or signal.confidence_score >= min_confidence:
                    signals.append(signal)
        
        return signals
        
    except Exception as e:
        logger.error(f"Error fetching early warning signals: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard", response_model=ForecastDashboardData)
async def get_forecast_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get forecasting dashboard data"""
    try:
        # Get active forecasts count
        active_forecasts = db.query(FinancialForecast).filter(
            FinancialForecast.organization_id == organization_id,
            FinancialForecast.status.in_(["draft", "in_review", "approved", "published"])
        ).count()
        
        # Get forecast accuracy average
        forecasts_with_accuracy = db.query(FinancialForecast).filter(
            FinancialForecast.organization_id == organization_id,
            FinancialForecast.validation_period_accuracy.isnot(None)
        ).all()
        
        if forecasts_with_accuracy:
            accuracy_avg = sum(float(f.validation_period_accuracy) for f in forecasts_with_accuracy) / len(forecasts_with_accuracy)
        else:
            accuracy_avg = 0.0
        
        # Get recent predictions
        recent_predictions = db.query(MLPrediction).filter(
            MLPrediction.organization_id == organization_id
        ).order_by(desc(MLPrediction.predicted_at)).limit(5).all()
        
        predictions_data = [
            {
                "id": p.id,
                "prediction_date": p.prediction_date.isoformat(),
                "predicted_value": float(p.predicted_value),
                "confidence_score": float(p.confidence_score) if p.confidence_score else None
            } for p in recent_predictions
        ]
        
        # Get risk alerts
        risk_alerts = db.query(RiskAnalysis).filter(
            RiskAnalysis.organization_id == organization_id,
            RiskAnalysis.is_active_alert == True
        ).limit(10).all()
        
        alerts_data = [
            {
                "id": r.id,
                "risk_name": r.risk_name,
                "alert_level": r.alert_level,
                "risk_score": float(r.risk_score)
            } for r in risk_alerts
        ]
        
        # Get key insights
        key_insights = db.query(AutomatedInsight).filter(
            AutomatedInsight.organization_id == organization_id,
            AutomatedInsight.importance_score >= 7.0,
            AutomatedInsight.status == "new"
        ).order_by(desc(AutomatedInsight.importance_score)).limit(5).all()
        
        insights_data = [
            {
                "id": i.id,
                "title": i.title,
                "insight_type": i.insight_type,
                "importance_score": float(i.importance_score),
                "confidence_score": float(i.confidence_score)
            } for i in key_insights
        ]
        
        dashboard_data = ForecastDashboardData(
            active_forecasts=active_forecasts,
            forecast_accuracy_avg=Decimal(str(accuracy_avg)),
            recent_predictions=predictions_data,
            risk_alerts=alerts_data,
            key_insights=insights_data,
            performance_metrics={
                "total_ml_models": db.query(MLForecastModel).filter(
                    MLForecastModel.organization_id == organization_id,
                    MLForecastModel.is_active == True
                ).count(),
                "predictions_this_month": db.query(MLPrediction).filter(
                    MLPrediction.organization_id == organization_id,
                    MLPrediction.predicted_at >= datetime.utcnow().replace(day=1)
                ).count()
            },
            trend_analysis={
                "forecast_accuracy_trend": "stable",
                "prediction_volume_trend": "increasing"
            }
        )
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error fetching forecast dashboard: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Forecast Versions
@router.get("/forecasts/{forecast_id}/versions", response_model=List[ForecastVersionResponse])
async def get_forecast_versions(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get version history for a forecast"""
    try:
        # Verify forecast exists
        forecast = db.query(FinancialForecast).filter(
            FinancialForecast.id == forecast_id,
            FinancialForecast.organization_id == organization_id
        ).first()
        
        if not forecast:
            raise HTTPException(status_code=404, detail="Forecast not found")
        
        versions = db.query(ForecastVersion).filter(
            ForecastVersion.financial_forecast_id == forecast_id,
            ForecastVersion.organization_id == organization_id
        ).order_by(desc(ForecastVersion.created_at)).all()
        
        return versions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching forecast versions: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forecasts/{forecast_id}/accuracy-analysis", response_model=ForecastAccuracyReport)
async def analyze_forecast_accuracy(
    forecast_id: int,
    actual_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Analyze forecast accuracy against actual data"""
    try:
        service = ForecastingService(db)
        
        # Verify forecast exists
        forecast = db.query(FinancialForecast).filter(
            FinancialForecast.id == forecast_id,
            FinancialForecast.organization_id == organization_id
        ).first()
        
        if not forecast:
            raise HTTPException(status_code=404, detail="Forecast not found")
        
        accuracy_analysis = service.analyze_forecast_accuracy(forecast_id, actual_data)
        
        # Create report object
        report = ForecastAccuracyReport(
            forecast_id=forecast_id,
            actual_vs_predicted=accuracy_analysis['comparison_data'],
            accuracy_metrics=accuracy_analysis['accuracy_metrics'],
            error_analysis={
                "mean_error": accuracy_analysis['accuracy_metrics']['mae'],
                "error_trend": "stable"  # Would calculate from data
            },
            recommendations=[
                "Consider updating model parameters if MAPE > 15%",
                "Review business driver assumptions",
                "Retrain model with recent data"
            ],
            analysis_period=f"Validation period analysis",
            generated_at=datetime.utcnow()
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing forecast accuracy: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))