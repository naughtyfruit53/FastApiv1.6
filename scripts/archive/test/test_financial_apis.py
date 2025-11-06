"""
Test financial modeling and forecasting APIs
"""

import requests
import json
from datetime import date, datetime
from decimal import Decimal

# Test configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Sample test data
test_dcf_assumptions = {
    "base_revenue": 1000000,
    "revenue_growth_rates": [15.0, 12.0, 10.0, 8.0, 5.0],
    "gross_margin": 60.0,
    "operating_margin": 20.0,
    "tax_rate": 25.0,
    "depreciation_rate": 3.0,
    "capex_rate": 4.0,
    "working_capital_change": 2.0,
    "risk_free_rate": 2.5,
    "market_risk_premium": 6.0,
    "beta": 1.2,
    "debt_ratio": 0.3,
    "cost_of_debt": 4.0,
    "terminal_growth_rate": 3.0
}

test_financial_model = {
    "model_name": "Test Tech Company Valuation",
    "model_type": "dcf",
    "model_version": "1.0",
    "analysis_start_date": "2024-01-01",
    "analysis_end_date": "2028-12-31",
    "forecast_years": 5,
    "assumptions": test_dcf_assumptions,
    "template_category": "technology"
}

test_forecast_data = {
    "forecast_name": "Revenue Forecast 2024-2029",
    "forecast_type": "revenue",
    "forecast_method": "linear_regression",
    "base_period_start": "2020-01-01",
    "base_period_end": "2023-12-31",
    "forecast_start": "2024-01-01",
    "forecast_end": "2029-12-31",
    "frequency": "monthly",
    "model_parameters": {
        "target_variable": "revenue",
        "features": ["trend", "seasonality"],
        "hyperparameters": {
            "fit_intercept": True
        }
    },
    "business_drivers": {
        "customer_growth": {
            "growth_rate": 20.0,
            "elasticity": 0.8
        },
        "pricing_power": {
            "growth_rate": 5.0,
            "elasticity": 0.6
        }
    },
    "historical_data": {
        "dates": ["2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01"],
        "values": [100000, 105000, 110000, 108000]
    }
}

def test_financial_modeling_apis():
    """Test financial modeling APIs"""
    print("=== Testing Financial Modeling APIs ===\n")
    
    # Test 1: Get model templates
    print("1. Testing model templates endpoint...")
    response = requests.get(f"{BASE_URL}{API_PREFIX}/financial-modeling/templates")
    if response.status_code == 200:
        print(f"✓ Templates retrieved successfully")
        templates = response.json()
        print(f"   Found {len(templates)} templates")
    else:
        print(f"✗ Templates request failed: {response.status_code}")
    
    # Test 2: Create financial model
    print("\n2. Testing financial model creation...")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/financial-modeling/models",
        json=test_financial_model
    )
    if response.status_code == 200:
        print(f"✓ Financial model created successfully")
        model = response.json()
        model_id = model["id"]
        print(f"   Model ID: {model_id}")
    else:
        print(f"✗ Model creation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # Test 3: Create DCF model
    print("\n3. Testing DCF model creation...")
    dcf_data = {
        "financial_model_id": model_id,
        "cost_of_equity": 12.0,
        "cost_of_debt": 4.0,
        "tax_rate": 25.0,
        "debt_to_equity_ratio": 0.4,
        "terminal_growth_rate": 3.0,
        "shares_outstanding": 1000000
    }
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/financial-modeling/models/{model_id}/dcf",
        json=dcf_data
    )
    if response.status_code == 200:
        print(f"✓ DCF model created successfully")
        dcf_model = response.json()
        print(f"   Enterprise Value: ${dcf_model['enterprise_value']:,.2f}")
        print(f"   Equity Value: ${dcf_model['equity_value']:,.2f}")
        print(f"   Value per Share: ${dcf_model['value_per_share']:,.2f}")
    else:
        print(f"✗ DCF model creation failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 4: Create scenario analysis
    print("\n4. Testing scenario analysis...")
    scenario_data = {
        "financial_model_id": model_id,
        "scenario_name": "Optimistic Growth",
        "scenario_type": "best_case",
        "scenario_description": "Assuming 20% higher growth rates",
        "assumption_changes": {
            "revenue_growth_rates": [18.0, 15.0, 12.0, 10.0, 6.0]
        },
        "probability": 30.0
    }
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/financial-modeling/models/{model_id}/scenarios",
        json=scenario_data
    )
    if response.status_code == 200:
        print(f"✓ Scenario analysis created successfully")
        scenario = response.json()
        print(f"   Scenario: {scenario['scenario_name']}")
    else:
        print(f"✗ Scenario analysis failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_forecasting_apis():
    """Test forecasting APIs"""
    print("\n=== Testing Forecasting APIs ===\n")
    
    # Test 1: Create financial forecast
    print("1. Testing financial forecast creation...")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/forecasting/forecasts",
        json=test_forecast_data
    )
    if response.status_code == 200:
        print(f"✓ Financial forecast created successfully")
        forecast = response.json()
        forecast_id = forecast["id"]
        print(f"   Forecast ID: {forecast_id}")
        print(f"   Method: {forecast['forecast_method']}")
    else:
        print(f"✗ Forecast creation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # Test 2: Get forecast dashboard
    print("\n2. Testing forecast dashboard...")
    response = requests.get(f"{BASE_URL}{API_PREFIX}/forecasting/dashboard")
    if response.status_code == 200:
        print(f"✓ Forecast dashboard retrieved successfully")
        dashboard = response.json()
        print(f"   Active Forecasts: {dashboard['active_forecasts']}")
        print(f"   Accuracy Average: {dashboard['forecast_accuracy_avg']:.1f}%")
    else:
        print(f"✗ Dashboard request failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 3: Generate automated insights
    print("\n3. Testing automated insights generation...")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/forecasting/insights/generate",
        params={
            "data_sources": ["financial_forecasts", "general_ledger"],
            "analysis_period_days": 30
        }
    )
    if response.status_code == 200:
        print(f"✓ Automated insights generated successfully")
        result = response.json()
        print(f"   Insights Generated: {result['insights_generated']}")
    else:
        print(f"✗ Insights generation failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_comprehensive_valuation():
    """Test comprehensive valuation API"""
    print("\n=== Testing Comprehensive Valuation ===\n")
    
    valuation_request = {
        "company_name": "Test Technology Company",
        "dcf_assumptions": test_dcf_assumptions,
        "industry_filter": "technology",
        "dcf_weight": 0.5,
        "trading_comps_weight": 0.3,
        "transaction_comps_weight": 0.2
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/financial-modeling/comprehensive-valuation",
        json=valuation_request
    )
    if response.status_code == 200:
        print(f"✓ Comprehensive valuation completed successfully")
        valuation = response.json()
        print(f"   Company: {valuation['company_name']}")
        if 'weighted_average_valuation' in valuation:
            print(f"   Weighted Average Valuation: ${valuation['weighted_average_valuation']['weighted_average_value']:,.2f}")
    else:
        print(f"✗ Comprehensive valuation failed: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    print("Financial Modeling & Forecasting API Test Suite")
    print("=" * 50)
    
    try:
        # Test financial modeling APIs
        test_financial_modeling_apis()
        
        # Test forecasting APIs
        test_forecasting_apis()
        
        # Test comprehensive valuation
        test_comprehensive_valuation()
        
        print("\n" + "=" * 50)
        print("Test suite completed!")
        print("\nNote: These tests require:")
        print("1. FastAPI server running on localhost:8000")
        print("2. Valid authentication token")
        print("3. Database with proper organization setup")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to FastAPI server")
        print("Please ensure the server is running on localhost:8000")
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")