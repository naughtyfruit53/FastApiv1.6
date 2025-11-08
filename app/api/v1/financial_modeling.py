"""
Financial Modeling API - DCF, WACC, valuation, and scenario analysis endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
import logging

from app.core.database import get_db
from app.core.enforcement import require_access


from app.models.user_models import User
from app.models.financial_modeling_models import (
    FinancialModel, DCFModel, ScenarioAnalysis, TradingComparables,
    TransactionComparables, FinancialModelTemplate, ModelAuditTrail
)
from app.schemas.financial_modeling import (
    FinancialModelCreate, FinancialModelUpdate, FinancialModelResponse,
    DCFModelCreate, DCFModelResponse, DCFAssumptions,
    ScenarioAnalysisCreate, ScenarioAnalysisResponse,
    TradingComparablesCreate, TradingComparablesUpdate, TradingComparablesResponse,
    TransactionComparablesCreate, TransactionComparablesUpdate, TransactionComparablesResponse,
    FinancialModelTemplateCreate, FinancialModelTemplateResponse,
    ComprehensiveValuationRequest, ValuationSummary, RatioAnalysis,
    ModelAuditTrailResponse
)
from app.services.financial_modeling_service import FinancialModelingService
from app.models.erp_models import GeneralLedger, ChartOfAccounts
from app.utils.financial_export import FinancialExportService
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/models", response_model=FinancialModelResponse)
async def create_financial_model(
    model_data: FinancialModelCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "create")),
    request: Request = None
):
    """Create a new financial model"""
    current_user, org_id = auth
    
    try:
        service = FinancialModelingService(db)
        
        # Create the financial model
        financial_model = FinancialModel(
            organization_id=org_id,
            model_name=model_data.model_name,
            model_type=model_data.model_type,
            model_version=model_data.model_version,
            analysis_start_date=model_data.analysis_start_date,
            analysis_end_date=model_data.analysis_end_date,
            forecast_years=model_data.forecast_years,
            assumptions=model_data.assumptions,
            projections={},  # Will be calculated
            valuation_results={},  # Will be calculated
            template_category=model_data.template_category,
            created_by_id=current_user.id
        )
        
        db.add(financial_model)
        db.commit()
        db.refresh(financial_model)
        
        # Create audit trail
        service.create_audit_trail(
            financial_model_id=financial_model.id,
            organization_id=org_id,
            action_type="create",
            user_id=current_user.id,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        return financial_model
        
    except Exception as e:
        logger.error(f"Error creating financial model: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/models", response_model=List[FinancialModelResponse])
async def get_financial_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    model_type: Optional[str] = Query(None),
    is_template: Optional[bool] = Query(None),
    is_approved: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Get financial models with filtering"""
    current_user, org_id = auth
    
    try:
        query = db.query(FinancialModel).filter(
            FinancialModel.organization_id == org_id
        )
        
        if model_type:
            query = query.filter(FinancialModel.model_type == model_type)
        if is_template is not None:
            query = query.filter(FinancialModel.is_template == is_template)
        if is_approved is not None:
            query = query.filter(FinancialModel.is_approved == is_approved)
        
        models = query.order_by(desc(FinancialModel.updated_at)).offset(skip).limit(limit).all()
        return models
        
    except Exception as e:
        logger.error(f"Error fetching financial models: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/models/{model_id}", response_model=FinancialModelResponse)
async def get_financial_model(
    model_id: int,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Get a specific financial model"""
    current_user, org_id = auth
    
    try:
        model = db.query(FinancialModel).filter(
            FinancialModel.id == model_id,
            FinancialModel.organization_id == org_id
        ).first()
        
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial model not found")
        
        return model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching financial model: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/models/{model_id}", response_model=FinancialModelResponse)
async def update_financial_model(
    model_id: int,
    model_data: FinancialModelUpdate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "update")),
    request: Request = None
):
    """Update a financial model"""
    current_user, org_id = auth
    
    try:
        service = FinancialModelingService(db)
        
        model = db.query(FinancialModel).filter(
            FinancialModel.id == model_id,
            FinancialModel.organization_id == org_id
        ).first()
        
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial model not found")
        
        # Track changes for audit trail
        changes = []
        if model_data.model_name and model_data.model_name != model.model_name:
            changes.append(("model_name", model.model_name, model_data.model_name))
            model.model_name = model_data.model_name
        
        if model_data.assumptions:
            changes.append(("assumptions", str(model.assumptions), str(model_data.assumptions)))
            model.assumptions = model_data.assumptions
        
        if model_data.projections:
            changes.append(("projections", str(model.projections), str(model_data.projections)))
            model.projections = model_data.projections
        
        if model_data.is_approved is not None:
            changes.append(("is_approved", str(model.is_approved), str(model_data.is_approved)))
            model.is_approved = model_data.is_approved
            if model_data.is_approved:
                model.approved_by_id = current_user.id
        
        model.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(model)
        
        # Create audit trail for each change
        for field, old_val, new_val in changes:
            service.create_audit_trail(
                financial_model_id=model.id,
                organization_id=org_id,
                action_type="update",
                user_id=current_user.id,
                field_changed=field,
                old_value=old_val,
                new_value=new_val,
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
        
        return model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating financial model: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/models/{model_id}")
async def delete_financial_model(
    model_id: int,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "delete")),
):
    """Delete a financial model"""
    current_user, org_id = auth
    
    try:
        model = db.query(FinancialModel).filter(
            FinancialModel.id == model_id,
            FinancialModel.organization_id == org_id
        ).first()
        
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial model not found")
        
        db.delete(model)
        db.commit()
        
        return {"message": "Financial model deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting financial model: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# DCF Model Endpoints
@router.post("/models/{model_id}/dcf", response_model=DCFModelResponse)
async def create_dcf_model(
    model_id: int,
    dcf_data: DCFModelCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "create")),
):
    """Create a DCF model for a financial model"""
    current_user, org_id = auth
    
    try:
        service = FinancialModelingService(db)
        
        # Verify the financial model exists
        financial_model = db.query(FinancialModel).filter(
            FinancialModel.id == model_id,
            FinancialModel.organization_id == org_id
        ).first()
        
        if not financial_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial model not found")
        
        # Calculate WACC
        wacc = service.calculate_wacc(
            dcf_data.cost_of_equity,
            dcf_data.cost_of_debt,
            dcf_data.tax_rate,
            dcf_data.debt_to_equity_ratio / (1 + dcf_data.debt_to_equity_ratio)  # Convert to debt ratio
        )
        
        # Get assumptions from financial model for cash flow projections
        assumptions_dict = financial_model.assumptions
        
        # Create DCF assumptions object for calculation
        if 'base_revenue' in assumptions_dict:
            dcf_assumptions = DCFAssumptions(
                base_revenue=Decimal(str(assumptions_dict.get('base_revenue', 1000000))),
                revenue_growth_rates=[Decimal(str(x)) for x in assumptions_dict.get('revenue_growth_rates', [5.0, 4.0, 3.0, 3.0, 2.0])],
                gross_margin=Decimal(str(assumptions_dict.get('gross_margin', 40.0))),
                operating_margin=Decimal(str(assumptions_dict.get('operating_margin', 15.0))),
                tax_rate=dcf_data.tax_rate,
                depreciation_rate=Decimal(str(assumptions_dict.get('depreciation_rate', 3.0))),
                capex_rate=Decimal(str(assumptions_dict.get('capex_rate', 2.0))),
                working_capital_change=Decimal(str(assumptions_dict.get('working_capital_change', 1.0))),
                risk_free_rate=Decimal(str(assumptions_dict.get('risk_free_rate', 2.0))),
                market_risk_premium=Decimal(str(assumptions_dict.get('market_risk_premium', 6.0))),
                beta=Decimal(str(assumptions_dict.get('beta', 1.2))),
                debt_ratio=dcf_data.debt_to_equity_ratio / (1 + dcf_data.debt_to_equity_ratio),
                cost_of_debt=dcf_data.cost_of_debt,
                terminal_growth_rate=dcf_data.terminal_growth_rate
            )
            
            # Build cash flow projections
            projections = service.build_cash_flow_projections(dcf_assumptions, financial_model.forecast_years)
            
            # Calculate terminal value
            final_year_fcf = Decimal(str(projections['free_cash_flow'][-1]))
            terminal_value = service.calculate_terminal_value(
                final_year_fcf,
                dcf_data.terminal_growth_rate,
                wacc,
                dcf_data.terminal_value_multiple
            )
            
            # Calculate DCF valuation
            valuation_results = service.calculate_dcf_valuation(
                projections,
                wacc,
                terminal_value
            )
            
            # Calculate value per share if shares outstanding provided
            value_per_share = None
            if dcf_data.shares_outstanding and dcf_data.shares_outstanding > 0:
                value_per_share = valuation_results['equity_value'] / dcf_data.shares_outstanding
        else:
            # Default calculation without detailed assumptions
            projections = {'free_cash_flow': [100000] * financial_model.forecast_years}
            terminal_value = Decimal('1000000')
            valuation_results = {
                'pv_of_fcf': Decimal('400000'),
                'pv_of_terminal_value': Decimal('600000'),
                'enterprise_value': Decimal('1000000'),
                'equity_value': Decimal('1000000')
            }
            value_per_share = None
        
        # Create DCF model
        dcf_model = DCFModel(
            financial_model_id=model_id,
            organization_id=org_id,
            cost_of_equity=dcf_data.cost_of_equity,
            cost_of_debt=dcf_data.cost_of_debt,
            tax_rate=dcf_data.tax_rate,
            debt_to_equity_ratio=dcf_data.debt_to_equity_ratio,
            wacc=wacc,
            terminal_growth_rate=dcf_data.terminal_growth_rate,
            terminal_value_multiple=dcf_data.terminal_value_multiple,
            terminal_value=terminal_value,
            pv_of_fcf=valuation_results['pv_of_fcf'],
            pv_of_terminal_value=valuation_results['pv_of_terminal_value'],
            enterprise_value=valuation_results['enterprise_value'],
            equity_value=valuation_results['equity_value'],
            shares_outstanding=dcf_data.shares_outstanding,
            value_per_share=value_per_share,
            cash_flow_projections=projections
        )
        
        db.add(dcf_model)
        db.commit()
        db.refresh(dcf_model)
        
        return dcf_model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating DCF model: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/models/{model_id}/dcf", response_model=DCFModelResponse)
async def get_dcf_model(
    model_id: int,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Get DCF model for a financial model"""
    current_user, org_id = auth
    
    try:
        dcf_model = db.query(DCFModel).filter(
            DCFModel.financial_model_id == model_id,
            DCFModel.organization_id == org_id
        ).first()
        
        if not dcf_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DCF model not found")
        
        return dcf_model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching DCF model: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Scenario Analysis Endpoints
@router.post("/models/{model_id}/scenarios", response_model=ScenarioAnalysisResponse)
async def create_scenario_analysis(
    model_id: int,
    scenario_data: ScenarioAnalysisCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "create")),
):
    """Create scenario analysis for a financial model"""
    current_user, org_id = auth
    
    try:
        service = FinancialModelingService(db)
        
        # Verify the financial model exists
        financial_model = db.query(FinancialModel).filter(
            FinancialModel.id == model_id,
            FinancialModel.organization_id == org_id
        ).first()
        
        if not financial_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial model not found")
        
        # Get base case assumptions from the financial model
        base_assumptions = financial_model.assumptions.copy()
        
        # Apply scenario changes
        scenario_assumptions = base_assumptions.copy()
        scenario_assumptions.update(scenario_data.assumption_changes)
        
        # Calculate scenario results (simplified - would need full DCF calculation)
        scenario_results = {
            'modified_assumptions': scenario_assumptions,
            'scenario_type': scenario_data.scenario_type.value,
            'calculation_date': datetime.utcnow().isoformat()
        }
        
        # Calculate variance from base case (simplified)
        variance_from_base = {}
        for key, value in scenario_data.assumption_changes.items():
            if key in base_assumptions:
                try:
                    base_val = float(base_assumptions[key])
                    scenario_val = float(value)
                    variance_pct = ((scenario_val - base_val) / abs(base_val)) * 100 if base_val != 0 else 0
                    variance_from_base[key] = variance_pct
                except (ValueError, TypeError):
                    variance_from_base[key] = "non_numeric"
        
        # Calculate risk-adjusted value if probability provided
        risk_adjusted_value = None
        if scenario_data.probability:
            # This is a simplified calculation - in practice, would use proper option pricing models
            base_value = 1000000  # Would get from base case DCF
            scenario_impact = sum([abs(v) for v in variance_from_base.values() if isinstance(v, (int, float))]) / 100
            risk_adjusted_value = Decimal(str(base_value * (1 + scenario_impact * (scenario_data.probability / 100))))
        
        # Create scenario analysis
        scenario = ScenarioAnalysis(
            financial_model_id=model_id,
            organization_id=org_id,
            scenario_name=scenario_data.scenario_name,
            scenario_type=scenario_data.scenario_type,
            scenario_description=scenario_data.scenario_description,
            assumption_changes=scenario_data.assumption_changes,
            scenario_results=scenario_results,
            variance_from_base=variance_from_base,
            probability=scenario_data.probability,
            risk_adjusted_value=risk_adjusted_value,
            created_by_id=current_user.id
        )
        
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        
        return scenario
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating scenario analysis: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/models/{model_id}/scenarios", response_model=List[ScenarioAnalysisResponse])
async def get_scenario_analyses(
    model_id: int,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Get scenario analyses for a financial model"""
    current_user, org_id = auth
    
    try:
        scenarios = db.query(ScenarioAnalysis).filter(
            ScenarioAnalysis.financial_model_id == model_id,
            ScenarioAnalysis.organization_id == org_id
        ).order_by(desc(ScenarioAnalysis.created_at)).all()
        
        return scenarios
        
    except Exception as e:
        logger.error(f"Error fetching scenario analyses: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Trading Comparables Endpoints
@router.post("/trading-comparables", response_model=TradingComparablesResponse)
async def create_trading_comparable(
    comparable_data: TradingComparablesCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "create")),
):
    """Create a trading comparable"""
    current_user, org_id = auth
    
    try:
        comparable = TradingComparables(
            organization_id=org_id,
            **comparable_data.dict(),
            created_by_id=current_user.id
        )
        
        db.add(comparable)
        db.commit()
        db.refresh(comparable)
        
        return comparable
        
    except Exception as e:
        logger.error(f"Error creating trading comparable: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/trading-comparables", response_model=List[TradingComparablesResponse])
async def get_trading_comparables(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    industry: Optional[str] = Query(None),
    is_active: bool = Query(True),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Get trading comparables with filtering"""
    current_user, org_id = auth
    
    try:
        query = db.query(TradingComparables).filter(
            TradingComparables.organization_id == org_id,
            TradingComparables.is_active == is_active
        )
        
        if industry:
            query = query.filter(TradingComparables.industry == industry)
        
        comparables = query.order_by(desc(TradingComparables.as_of_date)).offset(skip).limit(limit).all()
        return comparables
        
    except Exception as e:
        logger.error(f"Error fetching trading comparables: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Transaction Comparables Endpoints
@router.post("/transaction-comparables", response_model=TransactionComparablesResponse)
async def create_transaction_comparable(
    comparable_data: TransactionComparablesCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "create")),
):
    """Create a transaction comparable"""
    current_user, org_id = auth
    
    try:
        comparable = TransactionComparables(
            organization_id=org_id,
            **comparable_data.dict(),
            created_by_id=current_user.id
        )
        
        db.add(comparable)
        db.commit()
        db.refresh(comparable)
        
        return comparable
        
    except Exception as e:
        logger.error(f"Error creating transaction comparable: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/transaction-comparables", response_model=List[TransactionComparablesResponse])
async def get_transaction_comparables(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    industry: Optional[str] = Query(None),
    is_active: bool = Query(True),
    lookback_years: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Get transaction comparables with filtering"""
    current_user, org_id = auth
    
    try:
        cutoff_date = date.today().replace(year=date.today().year - lookback_years)
        
        query = db.query(TransactionComparables).filter(
            TransactionComparables.organization_id == org_id,
            TransactionComparables.is_active == is_active,
            TransactionComparables.transaction_date >= cutoff_date
        )
        
        if industry:
            query = query.filter(TransactionComparables.industry == industry)
        
        comparables = query.order_by(desc(TransactionComparables.transaction_date)).offset(skip).limit(limit).all()
        return comparables
        
    except Exception as e:
        logger.error(f"Error fetching transaction comparables: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Comprehensive Valuation
@router.post("/comprehensive-valuation", response_model=Dict[str, Any])
async def perform_comprehensive_valuation(
    valuation_request: ComprehensiveValuationRequest,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "create")),
):
    """Perform comprehensive valuation using multiple methods"""
    current_user, org_id = auth
    
    try:
        service = FinancialModelingService(db)
        
        # Validate weights sum to 1
        total_weight = valuation_request.dcf_weight + valuation_request.trading_comps_weight + valuation_request.transaction_comps_weight
        if abs(total_weight - 1.0) > 0.01:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Valuation method weights must sum to 1.0")
        
        results = service.perform_comprehensive_valuation(organization_id, valuation_request)
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing comprehensive valuation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Ratio Analysis
@router.get("/ratio-analysis", response_model=RatioAnalysis)
async def get_ratio_analysis(
    as_of_date: Optional[date] = Query(None, description="Analysis date (defaults to today)"),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Get financial ratio analysis"""
    current_user, org_id = auth
    
    try:
        service = FinancialModelingService(db)
        
        if not as_of_date:
            as_of_date = date.today()
        
        # Calculate financial ratios
        ratios = service.calculate_financial_ratios(db, organization_id, as_of_date)
        
        # Create ratio analysis response
        ratio_analysis = RatioAnalysis(
            current_ratio=ratios.get('current_ratio'),
            quick_ratio=ratios.get('quick_ratio'),
            cash_ratio=ratios.get('cash_ratio'),
            gross_margin=ratios.get('gross_margin'),
            operating_margin=ratios.get('operating_margin'),
            net_margin=ratios.get('net_margin'),
            roa=ratios.get('roa'),
            roe=ratios.get('roe'),
            debt_to_equity=ratios.get('debt_to_equity'),
            debt_to_assets=ratios.get('debt_to_assets'),
            interest_coverage=ratios.get('interest_coverage'),
            asset_turnover=ratios.get('asset_turnover'),
            inventory_turnover=ratios.get('inventory_turnover'),
            receivables_turnover=ratios.get('receivables_turnover'),
            analysis_period=f"As of {as_of_date}",
            benchmark_comparison=None  # Would add industry benchmarks
        )
        
        return ratio_analysis
        
    except Exception as e:
        logger.error(f"Error calculating ratio analysis: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Model Templates
@router.get("/templates", response_model=List[FinancialModelTemplateResponse])
async def get_model_templates(
    template_category: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    complexity_level: Optional[str] = Query(None),
    is_public: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get financial model templates"""
    current_user, org_id = auth
    
    try:
        query = db.query(FinancialModelTemplate).filter(
            FinancialModelTemplate.is_active == True
        )
        
        if is_public:
            query = query.filter(FinancialModelTemplate.is_public == True)
        
        if template_category:
            query = query.filter(FinancialModelTemplate.template_category == template_category)
        
        if industry:
            query = query.filter(FinancialModelTemplate.industry == industry)
        
        if complexity_level:
            query = query.filter(FinancialModelTemplate.complexity_level == complexity_level)
        
        templates = query.order_by(desc(FinancialModelTemplate.usage_count)).all()
        return templates
        
    except Exception as e:
        logger.error(f"Error fetching model templates: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/models/from-template/{template_id}", response_model=FinancialModelResponse)
async def create_model_from_template(
    template_id: int,
    model_name: str = Query(..., description="Name for the new model"),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "create")),
):
    """Create a financial model from a template"""
    try:
        template = db.query(FinancialModelTemplate).filter(
            FinancialModelTemplate.id == template_id,
            FinancialModelTemplate.is_active == True,
            FinancialModelTemplate.is_public == True
        ).first()
        
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        
        # Create financial model from template
        financial_model = FinancialModel(
            organization_id=org_id,
            model_name=model_name,
            model_type=template.model_type,
            model_version="1.0",
            analysis_start_date=date.today(),
            analysis_end_date=date.today().replace(year=date.today().year + 5),
            forecast_years=5,
            assumptions=template.default_assumptions,
            projections=template.projection_structure,
            valuation_results={},
            template_category=template.template_category,
            created_by_id=current_user.id
        )
        
        db.add(financial_model)
        
        # Update template usage count
        template.usage_count += 1
        
        db.commit()
        db.refresh(financial_model)
        
        return financial_model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating model from template: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Audit Trail
@router.get("/models/{model_id}/audit-trail", response_model=List[ModelAuditTrailResponse])
async def get_model_audit_trail(
    model_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Get audit trail for a financial model"""
    current_user, org_id = auth
    
    try:
        # Verify model exists and user has access
        model = db.query(FinancialModel).filter(
            FinancialModel.id == model_id,
            FinancialModel.organization_id == org_id
        ).first()
        
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial model not found")
        
        audit_entries = db.query(ModelAuditTrail).filter(
            ModelAuditTrail.financial_model_id == model_id,
            ModelAuditTrail.organization_id == org_id
        ).order_by(desc(ModelAuditTrail.changed_at)).offset(skip).limit(limit).all()
        
        return audit_entries
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching audit trail: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Export Endpoints
@router.get("/models/{model_id}/export/excel")
async def export_financial_model_excel(
    model_id: int,
    include_scenarios: bool = Query(True, description="Include scenario analysis"),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Export financial model to Excel format"""
    current_user, org_id = auth
    
    try:
        # Get financial model
        model = db.query(FinancialModel).filter(
            FinancialModel.id == model_id,
            FinancialModel.organization_id == org_id
        ).first()
        
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial model not found")
        
        # Get DCF model if exists
        dcf_model = db.query(DCFModel).filter(
            DCFModel.financial_model_id == model_id,
            DCFModel.organization_id == org_id
        ).first()
        
        if not dcf_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DCF model not found for this financial model")
        
        # Get scenarios if requested
        scenarios = []
        if include_scenarios:
            scenarios = db.query(ScenarioAnalysis).filter(
                ScenarioAnalysis.financial_model_id == model_id,
                ScenarioAnalysis.organization_id == org_id
            ).all()
        
        # Convert to dictionaries
        model_dict = {
            'id': model.id,
            'model_name': model.model_name,
            'model_type': model.model_type.value,
            'model_version': model.model_version,
            'analysis_start_date': model.analysis_start_date.isoformat(),
            'analysis_end_date': model.analysis_end_date.isoformat(),
            'forecast_years': model.forecast_years,
            'assumptions': model.assumptions,
            'projections': model.projections,
            'valuation_results': model.valuation_results,
            'created_at': model.created_at.isoformat(),
            'is_approved': model.is_approved
        }
        
        dcf_dict = {
            'cost_of_equity': float(dcf_model.cost_of_equity),
            'cost_of_debt': float(dcf_model.cost_of_debt),
            'tax_rate': float(dcf_model.tax_rate),
            'debt_to_equity_ratio': float(dcf_model.debt_to_equity_ratio),
            'wacc': float(dcf_model.wacc),
            'terminal_growth_rate': float(dcf_model.terminal_growth_rate),
            'terminal_value': float(dcf_model.terminal_value),
            'pv_of_fcf': float(dcf_model.pv_of_fcf),
            'pv_of_terminal_value': float(dcf_model.pv_of_terminal_value),
            'enterprise_value': float(dcf_model.enterprise_value),
            'equity_value': float(dcf_model.equity_value),
            'shares_outstanding': float(dcf_model.shares_outstanding) if dcf_model.shares_outstanding else None,
            'value_per_share': float(dcf_model.value_per_share) if dcf_model.value_per_share else None,
            'cash_flow_projections': dcf_model.cash_flow_projections
        }
        
        scenarios_dict = []
        for scenario in scenarios:
            scenarios_dict.append({
                'scenario_name': scenario.scenario_name,
                'scenario_type': scenario.scenario_type.value,
                'scenario_description': scenario.scenario_description,
                'assumption_changes': scenario.assumption_changes,
                'scenario_results': scenario.scenario_results,
                'variance_from_base': scenario.variance_from_base,
                'probability': float(scenario.probability) if scenario.probability else None,
                'risk_adjusted_value': float(scenario.risk_adjusted_value) if scenario.risk_adjusted_value else None
            })
        
        # Generate Excel file
        export_service = FinancialExportService()
        excel_file = export_service.export_dcf_model_to_excel(
            model_dict, 
            dcf_dict, 
            scenarios_dict if scenarios_dict else None
        )
        
        # Return as streaming response
        filename = f"{model.model_name.replace(' ', '_')}_DCF_Model.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting financial model to Excel: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/trading-comparables/export/csv")
async def export_trading_comparables_csv(
    industry: Optional[str] = Query(None),
    is_active: bool = Query(True),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("financial_modeling", "read")),
):
    """Export trading comparables to CSV format"""
    current_user, org_id = auth
    
    try:
        query = db.query(TradingComparables).filter(
            TradingComparables.organization_id == org_id,
            TradingComparables.is_active == is_active
        )
        
        if industry:
            query = query.filter(TradingComparables.industry == industry)
        
        comparables = query.all()
        
        # Convert to list of dictionaries
        data = []
        for comp in comparables:
            data.append({
                'company_name': comp.company_name,
                'ticker_symbol': comp.ticker_symbol,
                'industry': comp.industry,
                'market_cap': float(comp.market_cap) if comp.market_cap else None,
                'revenue_ttm': float(comp.revenue_ttm) if comp.revenue_ttm else None,
                'ebitda_ttm': float(comp.ebitda_ttm) if comp.ebitda_ttm else None,
                'net_income_ttm': float(comp.net_income_ttm) if comp.net_income_ttm else None,
                'ev_revenue_multiple': float(comp.ev_revenue_multiple) if comp.ev_revenue_multiple else None,
                'ev_ebitda_multiple': float(comp.ev_ebitda_multiple) if comp.ev_ebitda_multiple else None,
                'pe_ratio': float(comp.pe_ratio) if comp.pe_ratio else None,
                'data_source': comp.data_source,
                'as_of_date': comp.as_of_date.isoformat(),
                'created_at': comp.created_at.isoformat()
            })
        
        # Generate CSV file
        export_service = FinancialExportService()
        csv_file = export_service.export_to_csv(data, "trading_comparables")
        
        filename = f"trading_comparables_{industry or 'all'}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            csv_file,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting trading comparables to CSV: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    current_user, org_id = auth
    