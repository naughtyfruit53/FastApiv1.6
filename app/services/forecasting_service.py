"""
Forecasting Service - ML-powered forecasting and predictive analytics
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
import joblib
import json

from app.models.forecasting_models import (
    FinancialForecast, MLForecastModel, MLPrediction, BusinessDriverModel,
    RiskAnalysis, RiskEvent, AutomatedInsight, ForecastVersion
)
from app.models.erp_models import GeneralLedger, ChartOfAccounts
from app.schemas.forecasting import (
    FinancialForecastCreate, MLModelConfiguration, 
    MultiVariateForecastRequest, ScenarioForecastRequest
)

logger = logging.getLogger(__name__)


class ForecastingService:
    """ML-powered forecasting and predictive analytics service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.models = {
            'linear_regression': LinearRegression,
            'random_forest': RandomForestRegressor
        }
    
    def create_financial_forecast(
        self,
        organization_id: int,
        forecast_data: FinancialForecastCreate,
        user_id: Optional[int] = None
    ) -> FinancialForecast:
        """Create a new financial forecast with ML modeling"""
        try:
            # Process historical data and generate forecast
            forecast_results = self._generate_ml_forecast(
                historical_data=forecast_data.historical_data,
                method=forecast_data.forecast_method,
                parameters=forecast_data.model_parameters,
                forecast_start=forecast_data.forecast_start,
                forecast_end=forecast_data.forecast_end,
                frequency=forecast_data.frequency
            )
            
            # Create forecast record
            forecast = FinancialForecast(
                organization_id=organization_id,
                forecast_name=forecast_data.forecast_name,
                forecast_type=forecast_data.forecast_type,
                forecast_method=forecast_data.forecast_method,
                base_period_start=forecast_data.base_period_start,
                base_period_end=forecast_data.base_period_end,
                forecast_start=forecast_data.forecast_start,
                forecast_end=forecast_data.forecast_end,
                frequency=forecast_data.frequency,
                model_parameters=forecast_data.model_parameters,
                business_drivers=forecast_data.business_drivers,
                historical_data=forecast_data.historical_data,
                forecast_data=forecast_results['forecast_data'],
                confidence_intervals=forecast_results.get('confidence_intervals'),
                accuracy_metrics=forecast_results.get('accuracy_metrics'),
                created_by_id=user_id
            )
            
            self.db.add(forecast)
            self.db.commit()
            self.db.refresh(forecast)
            
            # Create initial version
            self._create_forecast_version(forecast.id, "1.0", "Initial forecast creation", user_id)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error creating financial forecast: {str(e)}")
            self.db.rollback()
            raise ValueError(f"Forecast creation failed: {str(e)}")
    
    def _generate_ml_forecast(
        self,
        historical_data: Dict[str, Any],
        method: str,
        parameters: Dict[str, Any],
        forecast_start: date,
        forecast_end: date,
        frequency: str
    ) -> Dict[str, Any]:
        """Generate ML-based forecast"""
        try:
            # Convert historical data to DataFrame
            df = pd.DataFrame(historical_data)
            
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            
            # Determine target variable
            target_col = parameters.get('target_variable', 'value')
            if target_col not in df.columns:
                raise ValueError(f"Target variable '{target_col}' not found in historical data")
            
            # Generate forecast based on method
            if method.value == 'linear_regression':
                return self._linear_regression_forecast(df, target_col, parameters, forecast_start, forecast_end, frequency)
            elif method.value == 'random_forest':
                return self._random_forest_forecast(df, target_col, parameters, forecast_start, forecast_end, frequency)
            elif method.value == 'time_series':
                return self._time_series_forecast(df, target_col, parameters, forecast_start, forecast_end, frequency)
            elif method.value == 'driver_based':
                return self._driver_based_forecast(df, target_col, parameters, forecast_start, forecast_end, frequency)
            else:
                return self._simple_trend_forecast(df, target_col, parameters, forecast_start, forecast_end, frequency)
                
        except Exception as e:
            logger.error(f"Error generating ML forecast: {str(e)}")
            raise ValueError(f"ML forecast generation failed: {str(e)}")
    
    def _linear_regression_forecast(
        self,
        df: pd.DataFrame,
        target_col: str,
        parameters: Dict[str, Any],
        forecast_start: date,
        forecast_end: date,
        frequency: str
    ) -> Dict[str, Any]:
        """Generate forecast using linear regression"""
        try:
            # Prepare features
            df = df.copy()
            df['trend'] = range(len(df))
            df['month'] = df.index.month
            df['quarter'] = df.index.quarter
            
            # Features for regression
            feature_cols = ['trend', 'month', 'quarter']
            if 'features' in parameters:
                feature_cols.extend([col for col in parameters['features'] if col in df.columns])
            
            X = df[feature_cols].fillna(0)
            y = df[target_col].fillna(method='ffill')
            
            # Split data for validation
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Validate model
            y_pred_test = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            mape = mean_absolute_percentage_error(y_test, y_pred_test) * 100
            
            # Generate forecast dates
            forecast_dates = self._generate_forecast_dates(forecast_start, forecast_end, frequency)
            
            # Prepare forecast features
            last_trend = len(df)
            forecast_features = []
            
            for i, forecast_date in enumerate(forecast_dates):
                feature_row = {
                    'trend': last_trend + i + 1,
                    'month': forecast_date.month,
                    'quarter': (forecast_date.month - 1) // 3 + 1
                }
                
                # Add other features with forward-filled values or defaults
                for col in feature_cols:
                    if col not in feature_row:
                        if col in df.columns:
                            feature_row[col] = df[col].iloc[-1]  # Use last known value
                        else:
                            feature_row[col] = 0
                
                forecast_features.append(feature_row)
            
            forecast_X = pd.DataFrame(forecast_features)[feature_cols]
            forecast_values = model.predict(forecast_X)
            
            # Calculate confidence intervals (simple approach)
            residuals = y_test - y_pred_test
            std_residual = np.std(residuals)
            
            lower_bound = forecast_values - 1.96 * std_residual
            upper_bound = forecast_values + 1.96 * std_residual
            
            # Prepare results
            forecast_data = {
                'dates': [d.isoformat() for d in forecast_dates],
                'values': forecast_values.tolist(),
                'method': 'linear_regression'
            }
            
            confidence_intervals = {
                'lower_bound': lower_bound.tolist(),
                'upper_bound': upper_bound.tolist(),
                'confidence_level': 0.95
            }
            
            accuracy_metrics = {
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'feature_importance': dict(zip(feature_cols, model.coef_))
            }
            
            return {
                'forecast_data': forecast_data,
                'confidence_intervals': confidence_intervals,
                'accuracy_metrics': accuracy_metrics,
                'model_object': model
            }
            
        except Exception as e:
            logger.error(f"Error in linear regression forecast: {str(e)}")
            raise ValueError(f"Linear regression forecast failed: {str(e)}")
    
    def _random_forest_forecast(
        self,
        df: pd.DataFrame,
        target_col: str,
        parameters: Dict[str, Any],
        forecast_start: date,
        forecast_end: date,
        frequency: str
    ) -> Dict[str, Any]:
        """Generate forecast using random forest"""
        try:
            # Prepare features
            df = df.copy()
            df['trend'] = range(len(df))
            df['month'] = df.index.month
            df['quarter'] = df.index.quarter
            df['day_of_year'] = df.index.dayofyear
            
            # Lag features
            for lag in [1, 3, 6, 12]:
                if len(df) > lag:
                    df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
            
            # Rolling averages
            for window in [3, 6, 12]:
                if len(df) > window:
                    df[f'{target_col}_ma_{window}'] = df[target_col].rolling(window=window).mean()
            
            # Features for regression
            feature_cols = ['trend', 'month', 'quarter', 'day_of_year']
            feature_cols.extend([col for col in df.columns if 'lag_' in col or 'ma_' in col])
            
            if 'features' in parameters:
                feature_cols.extend([col for col in parameters['features'] if col in df.columns])
            
            # Remove duplicates and filter existing columns
            feature_cols = list(set([col for col in feature_cols if col in df.columns]))
            
            X = df[feature_cols].fillna(method='ffill').fillna(0)
            y = df[target_col].fillna(method='ffill')
            
            # Split data for validation
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            rf_params = parameters.get('hyperparameters', {})
            model = RandomForestRegressor(
                n_estimators=rf_params.get('n_estimators', 100),
                max_depth=rf_params.get('max_depth', None),
                random_state=42
            )
            model.fit(X_train, y_train)
            
            # Validate model
            y_pred_test = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            mape = mean_absolute_percentage_error(y_test, y_pred_test) * 100
            
            # Generate forecast
            forecast_dates = self._generate_forecast_dates(forecast_start, forecast_end, frequency)
            forecast_values = []
            
            # For iterative forecasting (using previous predictions as features)
            last_data = df.iloc[-1:].copy()
            
            for i, forecast_date in enumerate(forecast_dates):
                # Prepare features for this forecast step
                feature_row = last_data.copy()
                feature_row.index = [forecast_date]
                feature_row['trend'] = len(df) + i + 1
                feature_row['month'] = forecast_date.month
                feature_row['quarter'] = (forecast_date.month - 1) // 3 + 1
                feature_row['day_of_year'] = forecast_date.timetuple().tm_yday
                
                # Update lag features with recent predictions
                if i > 0:
                    for lag in [1, 3, 6, 12]:
                        if f'{target_col}_lag_{lag}' in feature_cols and i >= lag:
                            feature_row[f'{target_col}_lag_{lag}'] = forecast_values[i - lag]
                
                # Make prediction
                X_forecast = feature_row[feature_cols].fillna(method='ffill').fillna(0)
                prediction = model.predict(X_forecast)[0]
                forecast_values.append(prediction)
                
                # Update last_data for next iteration
                feature_row[target_col] = prediction
                last_data = feature_row
            
            # Calculate confidence intervals using prediction intervals from trees
            predictions_all_trees = np.array([tree.predict(X_test) for tree in model.estimators_])
            std_predictions = np.std(predictions_all_trees, axis=0)
            mean_std = np.mean(std_predictions)
            
            lower_bound = np.array(forecast_values) - 1.96 * mean_std
            upper_bound = np.array(forecast_values) + 1.96 * mean_std
            
            # Prepare results
            forecast_data = {
                'dates': [d.isoformat() for d in forecast_dates],
                'values': forecast_values,
                'method': 'random_forest'
            }
            
            confidence_intervals = {
                'lower_bound': lower_bound.tolist(),
                'upper_bound': upper_bound.tolist(),
                'confidence_level': 0.95
            }
            
            accuracy_metrics = {
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'feature_importance': dict(zip(feature_cols, model.feature_importances_))
            }
            
            return {
                'forecast_data': forecast_data,
                'confidence_intervals': confidence_intervals,
                'accuracy_metrics': accuracy_metrics,
                'model_object': model
            }
            
        except Exception as e:
            logger.error(f"Error in random forest forecast: {str(e)}")
            raise ValueError(f"Random forest forecast failed: {str(e)}")
    
    def _time_series_forecast(
        self,
        df: pd.DataFrame,
        target_col: str,
        parameters: Dict[str, Any],
        forecast_start: date,
        forecast_end: date,
        frequency: str
    ) -> Dict[str, Any]:
        """Generate forecast using time series analysis (simple exponential smoothing)"""
        try:
            # Simple exponential smoothing implementation
            values = df[target_col].fillna(method='ffill').values
            
            # Calculate smoothing parameter (alpha)
            alpha = parameters.get('alpha', 0.3)
            
            # Apply exponential smoothing
            smoothed = [values[0]]
            for i in range(1, len(values)):
                smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[i-1])
            
            # Calculate trend
            if len(smoothed) > 1:
                trend = (smoothed[-1] - smoothed[0]) / (len(smoothed) - 1)
            else:
                trend = 0
            
            # Generate forecast
            forecast_dates = self._generate_forecast_dates(forecast_start, forecast_end, frequency)
            forecast_values = []
            
            last_value = smoothed[-1]
            for i, _ in enumerate(forecast_dates):
                forecast_value = last_value + trend * (i + 1)
                forecast_values.append(forecast_value)
            
            # Simple confidence intervals based on historical volatility
            residuals = np.diff(values)
            std_residual = np.std(residuals) if len(residuals) > 0 else 0
            
            lower_bound = np.array(forecast_values) - 1.96 * std_residual
            upper_bound = np.array(forecast_values) + 1.96 * std_residual
            
            # Calculate simple accuracy metrics
            mae = np.mean(np.abs(residuals)) if len(residuals) > 0 else 0
            rmse = np.sqrt(np.mean(residuals**2)) if len(residuals) > 0 else 0
            
            forecast_data = {
                'dates': [d.isoformat() for d in forecast_dates],
                'values': forecast_values,
                'method': 'time_series'
            }
            
            confidence_intervals = {
                'lower_bound': lower_bound.tolist(),
                'upper_bound': upper_bound.tolist(),
                'confidence_level': 0.95
            }
            
            accuracy_metrics = {
                'mae': mae,
                'rmse': rmse,
                'trend': trend,
                'alpha': alpha
            }
            
            return {
                'forecast_data': forecast_data,
                'confidence_intervals': confidence_intervals,
                'accuracy_metrics': accuracy_metrics
            }
            
        except Exception as e:
            logger.error(f"Error in time series forecast: {str(e)}")
            raise ValueError(f"Time series forecast failed: {str(e)}")
    
    def _driver_based_forecast(
        self,
        df: pd.DataFrame,
        target_col: str,
        parameters: Dict[str, Any],
        forecast_start: date,
        forecast_end: date,
        frequency: str
    ) -> Dict[str, Any]:
        """Generate forecast using business drivers"""
        try:
            drivers = parameters.get('drivers', {})
            if not drivers:
                raise ValueError("No business drivers specified for driver-based forecast")
            
            # Generate forecast dates
            forecast_dates = self._generate_forecast_dates(forecast_start, forecast_end, frequency)
            forecast_values = []
            
            # Base value (last known value)
            base_value = df[target_col].iloc[-1]
            
            for i, forecast_date in enumerate(forecast_dates):
                # Start with base value
                forecast_value = base_value
                
                # Apply driver impacts
                for driver_name, driver_config in drivers.items():
                    if driver_name in df.columns:
                        # Get driver growth rate or projected value
                        growth_rate = driver_config.get('growth_rate', 0)
                        elasticity = driver_config.get('elasticity', 1)
                        
                        # Apply driver impact
                        driver_impact = (growth_rate / 100) * elasticity
                        forecast_value *= (1 + driver_impact) ** (i + 1)
                
                forecast_values.append(forecast_value)
            
            # Simple confidence intervals based on driver uncertainty
            uncertainty = parameters.get('driver_uncertainty', 0.1)
            lower_bound = np.array(forecast_values) * (1 - uncertainty)
            upper_bound = np.array(forecast_values) * (1 + uncertainty)
            
            forecast_data = {
                'dates': [d.isoformat() for d in forecast_dates],
                'values': forecast_values,
                'method': 'driver_based'
            }
            
            confidence_intervals = {
                'lower_bound': lower_bound.tolist(),
                'upper_bound': upper_bound.tolist(),
                'confidence_level': 0.80  # Lower confidence due to driver uncertainty
            }
            
            accuracy_metrics = {
                'drivers_used': list(drivers.keys()),
                'base_value': base_value,
                'driver_uncertainty': uncertainty
            }
            
            return {
                'forecast_data': forecast_data,
                'confidence_intervals': confidence_intervals,
                'accuracy_metrics': accuracy_metrics
            }
            
        except Exception as e:
            logger.error(f"Error in driver-based forecast: {str(e)}")
            raise ValueError(f"Driver-based forecast failed: {str(e)}")
    
    def _simple_trend_forecast(
        self,
        df: pd.DataFrame,
        target_col: str,
        parameters: Dict[str, Any],
        forecast_start: date,
        forecast_end: date,
        frequency: str
    ) -> Dict[str, Any]:
        """Generate simple trend-based forecast"""
        try:
            values = df[target_col].fillna(method='ffill').values
            
            # Calculate linear trend
            x = np.arange(len(values))
            coeffs = np.polyfit(x, values, 1)
            trend_slope = coeffs[0]
            trend_intercept = coeffs[1]
            
            # Generate forecast
            forecast_dates = self._generate_forecast_dates(forecast_start, forecast_end, frequency)
            forecast_values = []
            
            last_x = len(values) - 1
            for i, _ in enumerate(forecast_dates):
                forecast_x = last_x + i + 1
                forecast_value = trend_slope * forecast_x + trend_intercept
                forecast_values.append(forecast_value)
            
            # Confidence intervals based on residuals
            trend_line = trend_slope * x + trend_intercept
            residuals = values - trend_line
            std_residual = np.std(residuals)
            
            lower_bound = np.array(forecast_values) - 1.96 * std_residual
            upper_bound = np.array(forecast_values) + 1.96 * std_residual
            
            # Accuracy metrics
            mae = np.mean(np.abs(residuals))
            rmse = np.sqrt(np.mean(residuals**2))
            
            forecast_data = {
                'dates': [d.isoformat() for d in forecast_dates],
                'values': forecast_values,
                'method': 'simple_trend'
            }
            
            confidence_intervals = {
                'lower_bound': lower_bound.tolist(),
                'upper_bound': upper_bound.tolist(),
                'confidence_level': 0.95
            }
            
            accuracy_metrics = {
                'mae': mae,
                'rmse': rmse,
                'trend_slope': trend_slope,
                'r_squared': np.corrcoef(values, trend_line)[0, 1]**2
            }
            
            return {
                'forecast_data': forecast_data,
                'confidence_intervals': confidence_intervals,
                'accuracy_metrics': accuracy_metrics
            }
            
        except Exception as e:
            logger.error(f"Error in simple trend forecast: {str(e)}")
            raise ValueError(f"Simple trend forecast failed: {str(e)}")
    
    def _generate_forecast_dates(
        self,
        start_date: date,
        end_date: date,
        frequency: str
    ) -> List[date]:
        """Generate forecast dates based on frequency"""
        dates = []
        current_date = start_date
        
        if frequency == 'monthly':
            while current_date <= end_date:
                dates.append(current_date)
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
                    
        elif frequency == 'quarterly':
            while current_date <= end_date:
                dates.append(current_date)
                # Move to next quarter
                new_month = current_date.month + 3
                if new_month > 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=new_month - 12)
                else:
                    current_date = current_date.replace(month=new_month)
                    
        elif frequency == 'annually':
            while current_date <= end_date:
                dates.append(current_date)
                current_date = current_date.replace(year=current_date.year + 1)
        
        return dates
    
    def _create_forecast_version(
        self,
        forecast_id: int,
        version_number: str,
        change_description: str,
        user_id: Optional[int] = None
    ) -> ForecastVersion:
        """Create a new forecast version"""
        try:
            # Get current forecast data
            forecast = self.db.query(FinancialForecast).filter(
                FinancialForecast.id == forecast_id
            ).first()
            
            if not forecast:
                raise ValueError("Forecast not found")
            
            # Mark previous versions as not current
            self.db.query(ForecastVersion).filter(
                ForecastVersion.financial_forecast_id == forecast_id,
                ForecastVersion.is_current == True
            ).update({'is_current': False})
            
            # Create new version
            version = ForecastVersion(
                financial_forecast_id=forecast_id,
                organization_id=forecast.organization_id,
                version_number=version_number,
                change_description=change_description,
                forecast_snapshot=forecast.forecast_data,
                model_parameters_snapshot=forecast.model_parameters,
                is_current=True,
                created_by_id=user_id
            )
            
            self.db.add(version)
            self.db.commit()
            self.db.refresh(version)
            
            return version
            
        except Exception as e:
            logger.error(f"Error creating forecast version: {str(e)}")
            self.db.rollback()
            raise ValueError(f"Forecast version creation failed: {str(e)}")
    
    def analyze_forecast_accuracy(
        self,
        forecast_id: int,
        actual_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze forecast accuracy against actual data"""
        try:
            forecast = self.db.query(FinancialForecast).filter(
                FinancialForecast.id == forecast_id
            ).first()
            
            if not forecast:
                raise ValueError("Forecast not found")
            
            # Convert forecast and actual data to comparable format
            forecast_df = pd.DataFrame(forecast.forecast_data)
            actual_df = pd.DataFrame(actual_data)
            
            # Align dates and values
            forecast_df['date'] = pd.to_datetime(forecast_df['dates'])
            actual_df['date'] = pd.to_datetime(actual_df['dates'])
            
            # Merge on dates
            merged = forecast_df.merge(actual_df, on='date', suffixes=('_forecast', '_actual'))
            
            if len(merged) == 0:
                raise ValueError("No matching dates between forecast and actual data")
            
            # Calculate accuracy metrics
            forecast_values = merged['values_forecast'].values
            actual_values = merged['values_actual'].values
            
            mae = mean_absolute_error(actual_values, forecast_values)
            rmse = np.sqrt(mean_squared_error(actual_values, forecast_values))
            mape = mean_absolute_percentage_error(actual_values, forecast_values) * 100
            
            # Calculate directional accuracy
            forecast_direction = np.diff(forecast_values) > 0
            actual_direction = np.diff(actual_values) > 0
            directional_accuracy = np.mean(forecast_direction == actual_direction) * 100 if len(forecast_direction) > 0 else 0
            
            # Update forecast with accuracy metrics
            accuracy_metrics = {
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'directional_accuracy': directional_accuracy,
                'data_points_compared': len(merged),
                'last_validation_date': datetime.now().isoformat()
            }
            
            forecast.accuracy_metrics = accuracy_metrics
            forecast.validation_period_accuracy = Decimal(str(100 - mape))  # Simple accuracy measure
            forecast.last_validation_date = date.today()
            
            self.db.commit()
            
            return {
                'forecast_id': forecast_id,
                'accuracy_metrics': accuracy_metrics,
                'comparison_data': merged.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing forecast accuracy: {str(e)}")
            raise ValueError(f"Forecast accuracy analysis failed: {str(e)}")
    
    def generate_automated_insights(
        self,
        organization_id: int,
        data_sources: List[str],
        analysis_period_days: int = 30
    ) -> List[AutomatedInsight]:
        """Generate automated business insights using AI/ML analysis"""
        try:
            insights = []
            end_date = date.today()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            # Analyze financial trends
            financial_insights = self._analyze_financial_trends(organization_id, start_date, end_date)
            insights.extend(financial_insights)
            
            # Analyze forecast accuracy trends
            forecast_insights = self._analyze_forecast_trends(organization_id, start_date, end_date)
            insights.extend(forecast_insights)
            
            # Analyze risk patterns
            risk_insights = self._analyze_risk_patterns(organization_id, start_date, end_date)
            insights.extend(risk_insights)
            
            # Save insights to database
            for insight_data in insights:
                insight = AutomatedInsight(
                    organization_id=organization_id,
                    **insight_data
                )
                self.db.add(insight)
            
            self.db.commit()
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating automated insights: {str(e)}")
            self.db.rollback()
            raise ValueError(f"Automated insights generation failed: {str(e)}")
    
    def _analyze_financial_trends(
        self,
        organization_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Analyze financial trends for insights"""
        insights = []
        
        try:
            # Query recent financial data
            financial_data = self.db.query(GeneralLedger).filter(
                GeneralLedger.organization_id == organization_id,
                GeneralLedger.transaction_date.between(start_date, end_date)
            ).all()
            
            if not financial_data:
                return insights
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame([{
                'date': record.transaction_date,
                'debit': float(record.debit_amount),
                'credit': float(record.credit_amount),
                'account_id': record.account_id
            } for record in financial_data])
            
            # Analyze trends
            df['net_flow'] = df['credit'] - df['debit']
            daily_flows = df.groupby('date')['net_flow'].sum()
            
            # Detect significant changes
            if len(daily_flows) > 7:  # Need enough data points
                recent_avg = daily_flows.tail(7).mean()
                historical_avg = daily_flows.head(-7).mean() if len(daily_flows) > 14 else daily_flows.mean()
                
                change_pct = ((recent_avg - historical_avg) / abs(historical_avg)) * 100 if historical_avg != 0 else 0
                
                if abs(change_pct) > 20:  # Significant change threshold
                    insight_type = "trend"
                    if change_pct > 0:
                        title = "Significant Increase in Cash Flow Detected"
                        description = f"Cash flow has increased by {change_pct:.1f}% over the past week compared to historical average."
                    else:
                        title = "Significant Decrease in Cash Flow Detected"
                        description = f"Cash flow has decreased by {abs(change_pct):.1f}% over the past week compared to historical average."
                    
                    insights.append({
                        'insight_type': insight_type,
                        'insight_category': 'financial',
                        'title': title,
                        'description': description,
                        'data_sources': ['general_ledger'],
                        'analysis_method': 'trend_analysis',
                        'confidence_score': Decimal('85.0'),
                        'importance_score': Decimal('7.5'),
                        'supporting_metrics': {
                            'recent_average': recent_avg,
                            'historical_average': historical_avg,
                            'change_percentage': change_pct
                        },
                        'recommended_actions': f"Review recent transactions and investigate the cause of this {'positive' if change_pct > 0 else 'negative'} trend."
                    })
            
        except Exception as e:
            logger.error(f"Error analyzing financial trends: {str(e)}")
        
        return insights
    
    def _analyze_forecast_trends(
        self,
        organization_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Analyze forecast accuracy trends"""
        insights = []
        
        try:
            # Get recent forecasts with accuracy data
            forecasts = self.db.query(FinancialForecast).filter(
                FinancialForecast.organization_id == organization_id,
                FinancialForecast.last_validation_date.isnot(None),
                FinancialForecast.last_validation_date.between(start_date, end_date)
            ).all()
            
            if len(forecasts) < 2:
                return insights
            
            # Analyze accuracy trends
            accuracy_scores = [float(f.validation_period_accuracy) for f in forecasts if f.validation_period_accuracy]
            
            if len(accuracy_scores) >= 2:
                recent_accuracy = np.mean(accuracy_scores[-2:])
                overall_accuracy = np.mean(accuracy_scores)
                
                if recent_accuracy < overall_accuracy - 10:  # Significant deterioration
                    insights.append({
                        'insight_type': 'risk',
                        'insight_category': 'operational',
                        'title': 'Forecasting Accuracy Declining',
                        'description': f'Recent forecast accuracy ({recent_accuracy:.1f}%) is significantly below average ({overall_accuracy:.1f}%).',
                        'data_sources': ['financial_forecasts'],
                        'analysis_method': 'accuracy_trend_analysis',
                        'confidence_score': Decimal('75.0'),
                        'importance_score': Decimal('6.0'),
                        'supporting_metrics': {
                            'recent_accuracy': recent_accuracy,
                            'overall_accuracy': overall_accuracy,
                            'accuracy_decline': overall_accuracy - recent_accuracy
                        },
                        'recommended_actions': 'Review forecast models and update parameters. Consider retraining ML models with recent data.'
                    })
                
        except Exception as e:
            logger.error(f"Error analyzing forecast trends: {str(e)}")
        
        return insights
    
    def _analyze_risk_patterns(
        self,
        organization_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Analyze risk patterns for early warning signals"""
        insights = []
        
        try:
            # Get risk events in the period
            risk_events = self.db.query(RiskEvent).filter(
                RiskEvent.organization_id == organization_id,
                RiskEvent.event_date.between(start_date, end_date)
            ).all()
            
            if len(risk_events) > 0:
                # Analyze risk event frequency
                high_severity_events = [e for e in risk_events if e.severity_level in ['high', 'critical']]
                
                if len(high_severity_events) > 2:  # Multiple high-severity events
                    insights.append({
                        'insight_type': 'risk',
                        'insight_category': 'risk_management',
                        'title': 'Increased High-Severity Risk Events',
                        'description': f'Detected {len(high_severity_events)} high-severity risk events in the past {(end_date - start_date).days} days.',
                        'data_sources': ['risk_events'],
                        'analysis_method': 'risk_pattern_analysis',
                        'confidence_score': Decimal('90.0'),
                        'importance_score': Decimal('9.0'),
                        'supporting_metrics': {
                            'high_severity_count': len(high_severity_events),
                            'total_risk_events': len(risk_events),
                            'analysis_period_days': (end_date - start_date).days
                        },
                        'recommended_actions': 'Review risk management processes and consider implementing additional preventive measures.'
                    })
                
        except Exception as e:
            logger.error(f"Error analyzing risk patterns: {str(e)}")
        
        return insights