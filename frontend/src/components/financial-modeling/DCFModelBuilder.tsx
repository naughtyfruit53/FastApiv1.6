/**
 * DCF Model Builder - Interactive DCF model creation and analysis
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { Calculator, Save, Play, FileDown, AlertCircle } from 'lucide-react';
import { financialModelingApi } from '@/services/api/financial-modeling';

interface DCFAssumptions {
  base_revenue: number;
  revenue_growth_rates: number[];
  gross_margin: number;
  operating_margin: number;
  tax_rate: number;
  depreciation_rate: number;
  capex_rate: number;
  working_capital_change: number;
  risk_free_rate: number;
  market_risk_premium: number;
  beta: number;
  debt_ratio: number;
  cost_of_debt: number;
  terminal_growth_rate: number;
}

interface DCFResults {
  wacc: number;
  enterprise_value: number;
  equity_value: number;
  value_per_share?: number;
  pv_of_fcf: number;
  pv_of_terminal_value: number;
  cash_flow_projections: any;
}

const defaultAssumptions: DCFAssumptions = {
  base_revenue: 10000000,
  revenue_growth_rates: [15, 12, 10, 8, 5],
  gross_margin: 60,
  operating_margin: 20,
  tax_rate: 25,
  depreciation_rate: 3,
  capex_rate: 4,
  working_capital_change: 2,
  risk_free_rate: 2.5,
  market_risk_premium: 6,
  beta: 1.2,
  debt_ratio: 30,
  cost_of_debt: 4,
  terminal_growth_rate: 3,
};

export const DCFModelBuilder: React.FC = () => {
  const [assumptions, setAssumptions] = useState<DCFAssumptions>(defaultAssumptions);
  const [results, setResults] = useState<DCFResults | null>(null);
  const [modelName, setModelName] = useState('');
  const [sharesOutstanding, setSharesOutstanding] = useState<number>(1000000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateAssumption = (key: keyof DCFAssumptions, value: number | number[]) => {
    setAssumptions(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const updateGrowthRate = (index: number, value: number) => {
    const newRates = [...assumptions.revenue_growth_rates];
    newRates[index] = value;
    updateAssumption('revenue_growth_rates', newRates);
  };

  const calculateDCF = async () => {
    if (!modelName.trim()) {
      setError('Please enter a model name');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Create financial model
      const modelData = {
        model_name: modelName,
        model_type: 'dcf',
        model_version: '1.0',
        analysis_start_date: new Date().toISOString().split('T')[0],
        analysis_end_date: new Date(Date.now() + 5 * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        forecast_years: 5,
        assumptions: assumptions,
      };

      const model = await financialModelingApi.createFinancialModel(modelData);

      // Calculate cost of equity using CAPM
      const costOfEquity = assumptions.risk_free_rate + 
        (assumptions.beta * assumptions.market_risk_premium);

      // Create DCF model
      const dcfData = {
        financial_model_id: model.id,
        cost_of_equity: costOfEquity,
        cost_of_debt: assumptions.cost_of_debt,
        tax_rate: assumptions.tax_rate,
        debt_to_equity_ratio: assumptions.debt_ratio / (100 - assumptions.debt_ratio),
        terminal_growth_rate: assumptions.terminal_growth_rate,
        shares_outstanding: sharesOutstanding,
      };

      const dcfResults = await financialModelingApi.createDCFModel(model.id, dcfData);
      setResults(dcfResults);

    } catch (err) {
      console.error('DCF calculation failed:', err);
      setError('Failed to calculate DCF model');
    } finally {
      setLoading(false);
    }
  };

  const generateProjections = () => {
    const projections = [];
    let revenue = assumptions.base_revenue;

    for (let year = 1; year <= 5; year++) {
      const growthRate = assumptions.revenue_growth_rates[year - 1] || 
        assumptions.revenue_growth_rates[assumptions.revenue_growth_rates.length - 1];
      
      revenue = revenue * (1 + growthRate / 100);
      const grossProfit = revenue * (assumptions.gross_margin / 100);
      const operatingProfit = revenue * (assumptions.operating_margin / 100);
      const depreciation = revenue * (assumptions.depreciation_rate / 100);
      const capex = revenue * (assumptions.capex_rate / 100);
      const wcChange = revenue * (assumptions.working_capital_change / 100);
      const taxes = operatingProfit * (assumptions.tax_rate / 100);
      const nopat = operatingProfit - taxes;
      const fcf = nopat + depreciation - capex - wcChange;

      projections.push({
        year: `Year ${year}`,
        revenue: revenue / 1000000, // Convert to millions
        grossProfit: grossProfit / 1000000,
        operatingProfit: operatingProfit / 1000000,
        fcf: fcf / 1000000,
      });
    }

    return projections;
  };

  const projectionData = generateProjections();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">DCF Model Builder</h1>
          <p className="text-gray-600">Build and analyze discounted cash flow models</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" disabled={!results}>
            <FileDown className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button 
            onClick={calculateDCF} 
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
            ) : (
              <Calculator className="h-4 w-4 mr-2" />
            )}
            Calculate DCF
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-700">
          <AlertCircle className="h-5 w-5" />
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Panel */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Model Assumptions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="modelName">Model Name</Label>
                <Input
                  id="modelName"
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  placeholder="Enter model name"
                />
              </div>

              <Tabs defaultValue="revenue" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="revenue">Revenue</TabsTrigger>
                  <TabsTrigger value="costs">Costs</TabsTrigger>
                  <TabsTrigger value="finance">Finance</TabsTrigger>
                </TabsList>

                <TabsContent value="revenue" className="space-y-4">
                  <div>
                    <Label htmlFor="baseRevenue">Base Revenue ($)</Label>
                    <Input
                      id="baseRevenue"
                      type="number"
                      value={assumptions.base_revenue}
                      onChange={(e) => updateAssumption('base_revenue', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label>Revenue Growth Rates (%)</Label>
                    {assumptions.revenue_growth_rates.map((rate, index) => (
                      <div key={index} className="flex items-center gap-2 mt-2">
                        <Label className="w-16">Year {index + 1}:</Label>
                        <Input
                          type="number"
                          value={rate}
                          onChange={(e) => updateGrowthRate(index, parseFloat(e.target.value) || 0)}
                          className="flex-1"
                        />
                      </div>
                    ))}
                  </div>

                  <div>
                    <Label htmlFor="grossMargin">Gross Margin (%)</Label>
                    <Input
                      id="grossMargin"
                      type="number"
                      value={assumptions.gross_margin}
                      onChange={(e) => updateAssumption('gross_margin', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </TabsContent>

                <TabsContent value="costs" className="space-y-4">
                  <div>
                    <Label htmlFor="operatingMargin">Operating Margin (%)</Label>
                    <Input
                      id="operatingMargin"
                      type="number"
                      value={assumptions.operating_margin}
                      onChange={(e) => updateAssumption('operating_margin', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="taxRate">Tax Rate (%)</Label>
                    <Input
                      id="taxRate"
                      type="number"
                      value={assumptions.tax_rate}
                      onChange={(e) => updateAssumption('tax_rate', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="depreciationRate">Depreciation Rate (%)</Label>
                    <Input
                      id="depreciationRate"
                      type="number"
                      value={assumptions.depreciation_rate}
                      onChange={(e) => updateAssumption('depreciation_rate', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="capexRate">CapEx Rate (%)</Label>
                    <Input
                      id="capexRate"
                      type="number"
                      value={assumptions.capex_rate}
                      onChange={(e) => updateAssumption('capex_rate', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </TabsContent>

                <TabsContent value="finance" className="space-y-4">
                  <div>
                    <Label htmlFor="riskFreeRate">Risk-Free Rate (%)</Label>
                    <Input
                      id="riskFreeRate"
                      type="number"
                      value={assumptions.risk_free_rate}
                      onChange={(e) => updateAssumption('risk_free_rate', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="marketRiskPremium">Market Risk Premium (%)</Label>
                    <Input
                      id="marketRiskPremium"
                      type="number"
                      value={assumptions.market_risk_premium}
                      onChange={(e) => updateAssumption('market_risk_premium', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="beta">Beta</Label>
                    <Input
                      id="beta"
                      type="number"
                      step="0.1"
                      value={assumptions.beta}
                      onChange={(e) => updateAssumption('beta', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="debtRatio">Debt Ratio (%)</Label>
                    <Input
                      id="debtRatio"
                      type="number"
                      value={assumptions.debt_ratio}
                      onChange={(e) => updateAssumption('debt_ratio', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="costOfDebt">Cost of Debt (%)</Label>
                    <Input
                      id="costOfDebt"
                      type="number"
                      value={assumptions.cost_of_debt}
                      onChange={(e) => updateAssumption('cost_of_debt', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="terminalGrowth">Terminal Growth Rate (%)</Label>
                    <Input
                      id="terminalGrowth"
                      type="number"
                      value={assumptions.terminal_growth_rate}
                      onChange={(e) => updateAssumption('terminal_growth_rate', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="sharesOutstanding">Shares Outstanding</Label>
                    <Input
                      id="sharesOutstanding"
                      type="number"
                      value={sharesOutstanding}
                      onChange={(e) => setSharesOutstanding(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Financial Projections Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Financial Projections</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={projectionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value.toFixed(1)}M`]} />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    name="Revenue"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="fcf" 
                    stroke="#10B981" 
                    strokeWidth={2}
                    name="Free Cash Flow"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* DCF Results */}
          {results && (
            <Card>
              <CardHeader>
                <CardTitle>DCF Valuation Results</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-600">WACC</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {results.wacc.toFixed(2)}%
                    </p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-gray-600">Enterprise Value</p>
                    <p className="text-2xl font-bold text-green-600">
                      ${(results.enterprise_value / 1000000).toFixed(1)}M
                    </p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <p className="text-sm text-gray-600">Equity Value</p>
                    <p className="text-2xl font-bold text-purple-600">
                      ${(results.equity_value / 1000000).toFixed(1)}M
                    </p>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <p className="text-sm text-gray-600">Value per Share</p>
                    <p className="text-2xl font-bold text-yellow-600">
                      ${results.value_per_share?.toFixed(2) || 'N/A'}
                    </p>
                  </div>
                </div>

                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Component</TableHead>
                      <TableHead>Value ($M)</TableHead>
                      <TableHead>% of Enterprise Value</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>PV of Free Cash Flow</TableCell>
                      <TableCell>${(results.pv_of_fcf / 1000000).toFixed(1)}M</TableCell>
                      <TableCell>
                        {((results.pv_of_fcf / results.enterprise_value) * 100).toFixed(1)}%
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>PV of Terminal Value</TableCell>
                      <TableCell>${(results.pv_of_terminal_value / 1000000).toFixed(1)}M</TableCell>
                      <TableCell>
                        {((results.pv_of_terminal_value / results.enterprise_value) * 100).toFixed(1)}%
                      </TableCell>
                    </TableRow>
                    <TableRow className="font-semibold">
                      <TableCell>Enterprise Value</TableCell>
                      <TableCell>${(results.enterprise_value / 1000000).toFixed(1)}M</TableCell>
                      <TableCell>100.0%</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};