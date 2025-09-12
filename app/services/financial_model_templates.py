"""
Sample financial model templates for different industries and use cases
"""

SAMPLE_TEMPLATES = {
    "startup_saas_dcf": {
        "template_name": "SaaS Startup DCF Model",
        "template_category": "startup_valuation",
        "industry": "technology",
        "description": "Comprehensive DCF model tailored for SaaS startups with subscription revenue",
        "model_type": "dcf",
        "complexity_level": "intermediate",
        "default_assumptions": {
            "base_revenue": 1000000,
            "revenue_growth_rates": [50.0, 40.0, 30.0, 25.0, 20.0],
            "gross_margin": 80.0,
            "operating_margin": 15.0,
            "tax_rate": 25.0,
            "depreciation_rate": 2.0,
            "capex_rate": 3.0,
            "working_capital_change": 2.0,
            "risk_free_rate": 2.5,
            "market_risk_premium": 6.0,
            "beta": 1.5,
            "debt_ratio": 0.2,
            "terminal_growth_rate": 3.0,
            "customer_acquisition_cost": 500,
            "customer_lifetime_value": 5000,
            "monthly_churn_rate": 2.0,
            "annual_contract_value": 1200
        },
        "projection_structure": {
            "revenue_drivers": ["new_customers", "expansion_revenue", "churn"],
            "cost_structure": ["cost_of_goods_sold", "sales_marketing", "rd", "general_admin"],
            "key_metrics": ["arr", "customers", "arpu", "ltv_cac_ratio", "rule_of_40"]
        }
    },
    
    "manufacturing_dcf": {
        "template_name": "Manufacturing Company DCF",
        "template_category": "industrial_valuation",
        "industry": "manufacturing",
        "description": "DCF model for manufacturing companies with inventory and working capital focus",
        "model_type": "dcf",
        "complexity_level": "advanced",
        "default_assumptions": {
            "base_revenue": 50000000,
            "revenue_growth_rates": [8.0, 6.0, 5.0, 4.0, 3.0],
            "gross_margin": 35.0,
            "operating_margin": 12.0,
            "tax_rate": 30.0,
            "depreciation_rate": 8.0,
            "capex_rate": 6.0,
            "working_capital_change": 3.0,
            "risk_free_rate": 2.5,
            "market_risk_premium": 6.0,
            "beta": 1.2,
            "debt_ratio": 0.4,
            "terminal_growth_rate": 2.5,
            "inventory_days": 60,
            "receivables_days": 45,
            "payables_days": 30,
            "capacity_utilization": 85.0
        },
        "projection_structure": {
            "revenue_drivers": ["volume_growth", "price_increases", "new_products"],
            "cost_structure": ["raw_materials", "labor", "overhead", "selling_admin"],
            "key_metrics": ["ebitda_margin", "asset_turnover", "roic", "debt_to_ebitda"]
        }
    },
    
    "retail_trading_comps": {
        "template_name": "Retail Trading Comparables",
        "template_category": "retail_valuation",
        "industry": "retail",
        "description": "Trading comparables analysis for retail companies",
        "model_type": "trading_comps",
        "complexity_level": "basic",
        "default_assumptions": {
            "ev_revenue_multiple": 1.5,
            "ev_ebitda_multiple": 8.0,
            "pe_ratio": 15.0,
            "revenue_growth": 5.0,
            "ebitda_margin": 12.0,
            "comparable_selection_criteria": {
                "min_market_cap": 100000000,
                "max_market_cap": 10000000000,
                "geographic_focus": "north_america",
                "business_model": "brick_and_mortar"
            }
        },
        "projection_structure": {
            "multiples": ["ev_revenue", "ev_ebitda", "pe", "pb", "ps"],
            "adjustments": ["size_premium", "liquidity_discount", "control_premium"],
            "key_metrics": ["same_store_sales", "revenue_per_sqft", "inventory_turns"]
        }
    },
    
    "real_estate_dcf": {
        "template_name": "Real Estate Investment DCF",
        "template_category": "real_estate_valuation",
        "industry": "real_estate",
        "description": "DCF model for real estate investments and REITs",
        "model_type": "dcf",
        "complexity_level": "intermediate",
        "default_assumptions": {
            "base_revenue": 10000000,
            "revenue_growth_rates": [4.0, 3.5, 3.0, 3.0, 2.5],
            "gross_margin": 65.0,
            "operating_margin": 35.0,
            "tax_rate": 20.0,
            "depreciation_rate": 3.0,
            "capex_rate": 2.0,
            "working_capital_change": 0.5,
            "risk_free_rate": 2.5,
            "market_risk_premium": 5.5,
            "beta": 0.8,
            "debt_ratio": 0.6,
            "terminal_growth_rate": 2.0,
            "occupancy_rate": 92.0,
            "rent_per_sqft": 25.0,
            "expense_ratio": 35.0
        },
        "projection_structure": {
            "revenue_drivers": ["rental_income", "occupancy_rates", "rent_escalations"],
            "cost_structure": ["property_taxes", "maintenance", "management_fees", "utilities"],
            "key_metrics": ["noi", "cap_rate", "dscr", "ltv", "irr"]
        }
    },
    
    "biotech_scenario": {
        "template_name": "Biotech Risk-Adjusted Valuation",
        "template_category": "biotech_valuation",
        "industry": "biotechnology",
        "description": "Risk-adjusted DCF with scenario analysis for biotech companies",
        "model_type": "dcf",
        "complexity_level": "advanced",
        "default_assumptions": {
            "base_revenue": 0,  # Pre-revenue
            "peak_sales": 2000000000,
            "probability_of_success": {
                "phase_1": 0.7,
                "phase_2": 0.4,
                "phase_3": 0.6,
                "approval": 0.8
            },
            "development_costs": {
                "phase_1": 50000000,
                "phase_2": 150000000,
                "phase_3": 300000000,
                "regulatory": 100000000
            },
            "time_to_market": 8,  # years
            "patent_expiry": 15,  # years from now
            "tax_rate": 25.0,
            "discount_rate": 12.0,
            "terminal_growth_rate": 0.0
        },
        "projection_structure": {
            "scenarios": ["success", "partial_success", "failure"],
            "risk_adjustments": ["clinical_risk", "regulatory_risk", "commercial_risk"],
            "key_metrics": ["npv", "probability_adjusted_npv", "peak_sales", "time_to_peak"]
        }
    }
}

def get_template_by_category(category: str):
    """Get all templates by category"""
    return {k: v for k, v in SAMPLE_TEMPLATES.items() if v["template_category"] == category}

def get_template_by_industry(industry: str):
    """Get all templates by industry"""
    return {k: v for k, v in SAMPLE_TEMPLATES.items() if v["industry"] == industry}

def get_templates_by_complexity(complexity: str):
    """Get templates by complexity level"""
    return {k: v for k, v in SAMPLE_TEMPLATES.items() if v["complexity_level"] == complexity}