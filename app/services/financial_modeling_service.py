"""
Financial Modeling Service - Core calculations for DCF, WACC, and valuation
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.financial_modeling_models import (
    FinancialModel, DCFModel, ScenarioAnalysis, TradingComparables, 
    TransactionComparables, ModelAuditTrail
)
from app.models.erp_models import GeneralLedger, ChartOfAccounts
from app.schemas.financial_modeling import DCFAssumptions, ComprehensiveValuationRequest

logger = logging.getLogger(__name__)


class FinancialModelingService:
    """Core financial modeling calculations and analysis"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_wacc(
        self,
        cost_of_equity: Decimal,
        cost_of_debt: Decimal,
        tax_rate: Decimal,
        debt_ratio: Decimal,
        equity_ratio: Optional[Decimal] = None
    ) -> Decimal:
        """
        Calculate Weighted Average Cost of Capital (WACC)
        WACC = (E/V * Re) + ((D/V * Rd) * (1 - Tc))
        """
        try:
            if equity_ratio is None:
                equity_ratio = Decimal('1.0') - debt_ratio
            
            # Convert percentages to decimals if they appear to be percentages
            if cost_of_equity > 1:
                cost_of_equity = cost_of_equity / 100
            if cost_of_debt > 1:
                cost_of_debt = cost_of_debt / 100
            if tax_rate > 1:
                tax_rate = tax_rate / 100
            
            # WACC calculation
            equity_component = equity_ratio * cost_of_equity
            debt_component = debt_ratio * cost_of_debt * (Decimal('1.0') - tax_rate)
            
            wacc = equity_component + debt_component
            
            # Convert back to percentage
            return wacc * 100 if wacc < 1 else wacc
            
        except Exception as e:
            logger.error(f"Error calculating WACC: {str(e)}")
            raise ValueError(f"WACC calculation failed: {str(e)}")
    
    def calculate_cost_of_equity(
        self,
        risk_free_rate: Decimal,
        beta: Decimal,
        market_risk_premium: Decimal
    ) -> Decimal:
        """
        Calculate Cost of Equity using CAPM
        Re = Rf + β(Rm - Rf)
        """
        try:
            # Convert percentages to decimals if needed
            if risk_free_rate > 1:
                risk_free_rate = risk_free_rate / 100
            if market_risk_premium > 1:
                market_risk_premium = market_risk_premium / 100
            
            cost_of_equity = risk_free_rate + (beta * market_risk_premium)
            
            # Convert back to percentage
            return cost_of_equity * 100 if cost_of_equity < 1 else cost_of_equity
            
        except Exception as e:
            logger.error(f"Error calculating cost of equity: {str(e)}")
            raise ValueError(f"Cost of equity calculation failed: {str(e)}")
    
    def build_cash_flow_projections(
        self,
        assumptions: DCFAssumptions,
        forecast_years: int = 5
    ) -> Dict[str, Any]:
        """Build detailed cash flow projections"""
        try:
            projections = {
                'years': list(range(1, forecast_years + 1)),
                'revenue': [],
                'gross_profit': [],
                'operating_profit': [],
                'ebit': [],
                'taxes': [],
                'nopat': [],
                'depreciation': [],
                'capex': [],
                'working_capital_change': [],
                'free_cash_flow': []
            }
            
            current_revenue = assumptions.base_revenue
            
            for year in range(forecast_years):
                # Get growth rate for this year
                if year < len(assumptions.revenue_growth_rates):
                    growth_rate = assumptions.revenue_growth_rates[year] / 100
                else:
                    # Use last available growth rate
                    growth_rate = assumptions.revenue_growth_rates[-1] / 100
                
                # Calculate revenue
                if year == 0:
                    revenue = current_revenue * (1 + growth_rate)
                else:
                    revenue = projections['revenue'][-1] * (1 + growth_rate)
                
                projections['revenue'].append(float(revenue))
                
                # Calculate other financial metrics
                gross_profit = revenue * (assumptions.gross_margin / 100)
                projections['gross_profit'].append(float(gross_profit))
                
                operating_profit = revenue * (assumptions.operating_margin / 100)
                projections['operating_profit'].append(float(operating_profit))
                
                ebit = operating_profit  # Simplified - could add more detail
                projections['ebit'].append(float(ebit))
                
                taxes = ebit * (assumptions.tax_rate / 100)
                projections['taxes'].append(float(taxes))
                
                nopat = ebit - taxes
                projections['nopat'].append(float(nopat))
                
                depreciation = revenue * (assumptions.depreciation_rate / 100)
                projections['depreciation'].append(float(depreciation))
                
                capex = revenue * (assumptions.capex_rate / 100)
                projections['capex'].append(float(capex))
                
                wc_change = revenue * (assumptions.working_capital_change / 100)
                projections['working_capital_change'].append(float(wc_change))
                
                # Free Cash Flow = NOPAT + Depreciation - Capex - WC Change
                fcf = nopat + depreciation - capex - wc_change
                projections['free_cash_flow'].append(float(fcf))
            
            return projections
            
        except Exception as e:
            logger.error(f"Error building cash flow projections: {str(e)}")
            raise ValueError(f"Cash flow projection failed: {str(e)}")
    
    def calculate_terminal_value(
        self,
        final_year_fcf: Decimal,
        terminal_growth_rate: Decimal,
        wacc: Decimal,
        terminal_multiple: Optional[Decimal] = None,
        final_year_ebitda: Optional[Decimal] = None
    ) -> Decimal:
        """Calculate terminal value using growth method or multiple method"""
        try:
            # Convert percentages to decimals
            if terminal_growth_rate > 1:
                terminal_growth_rate = terminal_growth_rate / 100
            if wacc > 1:
                wacc = wacc / 100
            
            if terminal_multiple and final_year_ebitda:
                # Multiple method: Terminal Value = EBITDA × Multiple
                terminal_value = final_year_ebitda * terminal_multiple
            else:
                # Growth method: Terminal Value = FCF × (1 + g) / (WACC - g)
                if wacc <= terminal_growth_rate:
                    raise ValueError("WACC must be greater than terminal growth rate")
                
                terminal_value = (final_year_fcf * (Decimal('1.0') + terminal_growth_rate)) / (wacc - terminal_growth_rate)
            
            return terminal_value
            
        except Exception as e:
            logger.error(f"Error calculating terminal value: {str(e)}")
            raise ValueError(f"Terminal value calculation failed: {str(e)}")
    
    def calculate_dcf_valuation(
        self,
        cash_flow_projections: Dict[str, Any],
        wacc: Decimal,
        terminal_value: Decimal,
        net_debt: Decimal = Decimal('0'),
        cash_and_equivalents: Decimal = Decimal('0')
    ) -> Dict[str, Decimal]:
        """Calculate DCF valuation"""
        try:
            # Convert WACC to decimal
            if wacc > 1:
                wacc = wacc / 100
            
            free_cash_flows = [Decimal(str(fcf)) for fcf in cash_flow_projections['free_cash_flow']]
            
            # Calculate present value of cash flows
            pv_of_fcf = Decimal('0')
            pv_details = []
            
            for year, fcf in enumerate(free_cash_flows, 1):
                discount_factor = Decimal('1') / ((Decimal('1') + wacc) ** year)
                pv = fcf * discount_factor
                pv_of_fcf += pv
                pv_details.append({
                    'year': year,
                    'fcf': float(fcf),
                    'discount_factor': float(discount_factor),
                    'present_value': float(pv)
                })
            
            # Calculate present value of terminal value
            terminal_year = len(free_cash_flows)
            terminal_discount_factor = Decimal('1') / ((Decimal('1') + wacc) ** terminal_year)
            pv_of_terminal_value = terminal_value * terminal_discount_factor
            
            # Calculate enterprise value
            enterprise_value = pv_of_fcf + pv_of_terminal_value
            
            # Calculate equity value
            equity_value = enterprise_value - net_debt + cash_and_equivalents
            
            return {
                'pv_of_fcf': pv_of_fcf.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'pv_of_terminal_value': pv_of_terminal_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'enterprise_value': enterprise_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'equity_value': equity_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'terminal_value': terminal_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'pv_details': pv_details
            }
            
        except Exception as e:
            logger.error(f"Error calculating DCF valuation: {str(e)}")
            raise ValueError(f"DCF valuation calculation failed: {str(e)}")
    
    def perform_sensitivity_analysis(
        self,
        base_assumptions: DCFAssumptions,
        sensitivity_variables: List[str],
        variation_ranges: Dict[str, float],
        steps: int = 5
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on DCF model"""
        try:
            results = {}
            base_valuation = self._calculate_base_dcf(base_assumptions)
            
            for variable in sensitivity_variables:
                if variable not in variation_ranges:
                    continue
                
                variable_results = {
                    'variable': variable,
                    'base_value': getattr(base_assumptions, variable, None),
                    'variations': []
                }
                
                variation_range = variation_ranges[variable]
                step_size = (2 * variation_range) / (steps - 1)
                
                for i in range(steps):
                    # Calculate variation percentage
                    variation_pct = -variation_range + (i * step_size)
                    
                    # Create modified assumptions
                    modified_assumptions = base_assumptions.copy()
                    original_value = getattr(modified_assumptions, variable)
                    new_value = original_value * (1 + variation_pct / 100)
                    setattr(modified_assumptions, variable, new_value)
                    
                    # Calculate valuation with modified assumptions
                    modified_valuation = self._calculate_base_dcf(modified_assumptions)
                    
                    # Calculate impact
                    valuation_change = (modified_valuation['equity_value'] - base_valuation['equity_value']) / base_valuation['equity_value'] * 100
                    
                    variable_results['variations'].append({
                        'variation_pct': variation_pct,
                        'new_value': float(new_value),
                        'equity_value': float(modified_valuation['equity_value']),
                        'valuation_change_pct': float(valuation_change)
                    })
                
                results[variable] = variable_results
            
            return {
                'base_valuation': base_valuation,
                'sensitivity_results': results
            }
            
        except Exception as e:
            logger.error(f"Error performing sensitivity analysis: {str(e)}")
            raise ValueError(f"Sensitivity analysis failed: {str(e)}")
    
    def _calculate_base_dcf(self, assumptions: DCFAssumptions) -> Dict[str, Decimal]:
        """Helper method to calculate base DCF valuation"""
        # Calculate cost of equity and WACC
        cost_of_equity = self.calculate_cost_of_equity(
            assumptions.risk_free_rate,
            assumptions.beta,
            assumptions.market_risk_premium
        )
        
        wacc = self.calculate_wacc(
            cost_of_equity,
            assumptions.cost_of_debt,
            assumptions.tax_rate,
            assumptions.debt_ratio
        )
        
        # Build projections
        projections = self.build_cash_flow_projections(assumptions)
        
        # Calculate terminal value
        final_year_fcf = Decimal(str(projections['free_cash_flow'][-1]))
        terminal_value = self.calculate_terminal_value(
            final_year_fcf,
            assumptions.terminal_growth_rate,
            wacc
        )
        
        # Calculate DCF valuation
        return self.calculate_dcf_valuation(projections, wacc, terminal_value)
    
    def calculate_trading_multiples_valuation(
        self,
        organization_id: int,
        company_metrics: Dict[str, Decimal],
        industry_filter: Optional[str] = None
    ) -> Dict[str, Decimal]:
        """Calculate valuation using trading comparables"""
        try:
            # Get trading comparables
            query = self.db.query(TradingComparables).filter(
                TradingComparables.organization_id == organization_id,
                TradingComparables.is_active == True
            )
            
            if industry_filter:
                query = query.filter(TradingComparables.industry == industry_filter)
            
            comparables = query.all()
            
            if not comparables:
                raise ValueError("No trading comparables found")
            
            # Calculate median multiples
            ev_revenue_multiples = [comp.ev_revenue_multiple for comp in comparables if comp.ev_revenue_multiple]
            ev_ebitda_multiples = [comp.ev_ebitda_multiple for comp in comparables if comp.ev_ebitda_multiple]
            pe_ratios = [comp.pe_ratio for comp in comparables if comp.pe_ratio]
            
            median_ev_revenue = np.median(ev_revenue_multiples) if ev_revenue_multiples else None
            median_ev_ebitda = np.median(ev_ebitda_multiples) if ev_ebitda_multiples else None
            median_pe = np.median(pe_ratios) if pe_ratios else None
            
            # Apply multiples to company metrics
            valuations = {}
            
            if median_ev_revenue and 'revenue' in company_metrics:
                valuations['ev_revenue_valuation'] = company_metrics['revenue'] * Decimal(str(median_ev_revenue))
            
            if median_ev_ebitda and 'ebitda' in company_metrics:
                valuations['ev_ebitda_valuation'] = company_metrics['ebitda'] * Decimal(str(median_ev_ebitda))
            
            if median_pe and 'net_income' in company_metrics:
                valuations['pe_valuation'] = company_metrics['net_income'] * Decimal(str(median_pe))
            
            # Calculate average valuation
            if valuations:
                avg_valuation = sum(valuations.values()) / len(valuations)
                valuations['average_trading_comps_valuation'] = avg_valuation
            
            return valuations
            
        except Exception as e:
            logger.error(f"Error calculating trading multiples valuation: {str(e)}")
            raise ValueError(f"Trading multiples valuation failed: {str(e)}")
    
    def calculate_transaction_multiples_valuation(
        self,
        organization_id: int,
        company_metrics: Dict[str, Decimal],
        industry_filter: Optional[str] = None,
        lookback_years: int = 5
    ) -> Dict[str, Decimal]:
        """Calculate valuation using transaction comparables"""
        try:
            # Get transaction comparables from last N years
            cutoff_date = date.today().replace(year=date.today().year - lookback_years)
            
            query = self.db.query(TransactionComparables).filter(
                TransactionComparables.organization_id == organization_id,
                TransactionComparables.is_active == True,
                TransactionComparables.transaction_date >= cutoff_date
            )
            
            if industry_filter:
                query = query.filter(TransactionComparables.industry == industry_filter)
            
            comparables = query.all()
            
            if not comparables:
                raise ValueError("No transaction comparables found")
            
            # Calculate median multiples
            ev_revenue_multiples = [comp.ev_revenue_multiple for comp in comparables if comp.ev_revenue_multiple]
            ev_ebitda_multiples = [comp.ev_ebitda_multiple for comp in comparables if comp.ev_ebitda_multiple]
            
            median_ev_revenue = np.median(ev_revenue_multiples) if ev_revenue_multiples else None
            median_ev_ebitda = np.median(ev_ebitda_multiples) if ev_ebitda_multiples else None
            
            # Calculate average control premium
            control_premiums = [comp.control_premium for comp in comparables if comp.control_premium]
            avg_control_premium = np.mean(control_premiums) if control_premiums else Decimal('20.0')  # Default 20%
            
            # Apply multiples to company metrics
            valuations = {}
            
            if median_ev_revenue and 'revenue' in company_metrics:
                base_valuation = company_metrics['revenue'] * Decimal(str(median_ev_revenue))
                control_adjusted = base_valuation * (1 + avg_control_premium / 100)
                valuations['transaction_ev_revenue_valuation'] = control_adjusted
            
            if median_ev_ebitda and 'ebitda' in company_metrics:
                base_valuation = company_metrics['ebitda'] * Decimal(str(median_ev_ebitda))
                control_adjusted = base_valuation * (1 + avg_control_premium / 100)
                valuations['transaction_ev_ebitda_valuation'] = control_adjusted
            
            # Calculate average valuation
            if valuations:
                avg_valuation = sum(valuations.values()) / len(valuations)
                valuations['average_transaction_comps_valuation'] = avg_valuation
            
            valuations['control_premium_applied'] = avg_control_premium
            
            return valuations
            
        except Exception as e:
            logger.error(f"Error calculating transaction multiples valuation: {str(e)}")
            raise ValueError(f"Transaction multiples valuation failed: {str(e)}")
    
    def perform_comprehensive_valuation(
        self,
        organization_id: int,
        request: ComprehensiveValuationRequest
    ) -> Dict[str, Any]:
        """Perform comprehensive valuation using multiple methods"""
        try:
            results = {
                'company_name': request.company_name,
                'analysis_date': date.today(),
                'valuations': {},
                'weights': {
                    'dcf': float(request.dcf_weight),
                    'trading_comps': float(request.trading_comps_weight),
                    'transaction_comps': float(request.transaction_comps_weight)
                }
            }
            
            # DCF Valuation
            if request.dcf_assumptions:
                dcf_result = self._calculate_base_dcf(request.dcf_assumptions)
                results['valuations']['dcf'] = {
                    'equity_value': float(dcf_result['equity_value']),
                    'enterprise_value': float(dcf_result['enterprise_value']),
                    'method': 'dcf'
                }
            
            # Trading Comparables
            if request.trading_comps_weight > 0:
                # Extract company metrics from DCF assumptions if available
                company_metrics = {}
                if request.dcf_assumptions:
                    company_metrics['revenue'] = request.dcf_assumptions.base_revenue
                    # Add other metrics as needed
                
                if company_metrics:
                    trading_result = self.calculate_trading_multiples_valuation(
                        organization_id,
                        company_metrics,
                        request.industry_filter
                    )
                    results['valuations']['trading_comps'] = trading_result
            
            # Transaction Comparables
            if request.transaction_comps_weight > 0 and company_metrics:
                transaction_result = self.calculate_transaction_multiples_valuation(
                    organization_id,
                    company_metrics,
                    request.industry_filter
                )
                results['valuations']['transaction_comps'] = transaction_result
            
            # Calculate weighted average valuation
            weighted_valuation = self._calculate_weighted_average_valuation(results)
            results['weighted_average_valuation'] = weighted_valuation
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing comprehensive valuation: {str(e)}")
            raise ValueError(f"Comprehensive valuation failed: {str(e)}")
    
    def _calculate_weighted_average_valuation(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate weighted average valuation from multiple methods"""
        try:
            valuations = results['valuations']
            weights = results['weights']
            
            total_weight = 0
            weighted_sum = 0
            
            # DCF
            if 'dcf' in valuations and weights['dcf'] > 0:
                weighted_sum += valuations['dcf']['equity_value'] * weights['dcf']
                total_weight += weights['dcf']
            
            # Trading Comps
            if 'trading_comps' in valuations and weights['trading_comps'] > 0:
                if 'average_trading_comps_valuation' in valuations['trading_comps']:
                    weighted_sum += float(valuations['trading_comps']['average_trading_comps_valuation']) * weights['trading_comps']
                    total_weight += weights['trading_comps']
            
            # Transaction Comps
            if 'transaction_comps' in valuations and weights['transaction_comps'] > 0:
                if 'average_transaction_comps_valuation' in valuations['transaction_comps']:
                    weighted_sum += float(valuations['transaction_comps']['average_transaction_comps_valuation']) * weights['transaction_comps']
                    total_weight += weights['transaction_comps']
            
            if total_weight > 0:
                weighted_average = weighted_sum / total_weight
                return {
                    'weighted_average_value': weighted_average,
                    'total_weight_used': total_weight
                }
            else:
                return {'error': 'No valid valuations to weight'}
                
        except Exception as e:
            logger.error(f"Error calculating weighted average valuation: {str(e)}")
            return {'error': f'Weighted average calculation failed: {str(e)}'}
    
    def create_audit_trail(
        self,
        financial_model_id: int,
        organization_id: int,
        action_type: str,
        user_id: int,
        field_changed: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        change_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ModelAuditTrail:
        """Create an audit trail entry"""
        try:
            audit_entry = ModelAuditTrail(
                financial_model_id=financial_model_id,
                organization_id=organization_id,
                action_type=action_type,
                field_changed=field_changed,
                old_value=old_value,
                new_value=new_value,
                change_reason=change_reason,
                changed_by_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(audit_entry)
            self.db.commit()
            self.db.refresh(audit_entry)
            
            return audit_entry
            
        except Exception as e:
            logger.error(f"Error creating audit trail: {str(e)}")
            self.db.rollback()
            raise ValueError(f"Audit trail creation failed: {str(e)}")