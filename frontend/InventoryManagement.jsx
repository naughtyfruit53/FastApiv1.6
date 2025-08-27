import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle, Package, Plus, Search, Filter } from 'lucide-react';

const InventoryManagement = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [inventoryData, setInventoryData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [jobParts, setJobParts] = useState([]);

  // Mock data for demonstration
  useEffect(() => {
    // Simulate API call for inventory data
    setInventoryData([
      {
        id: 1,
        name: 'Screws',
        currentStock: 15,
        reorderLevel: 100,
        unit: 'pcs',
        location: 'warehouse',
        unitCost: 0.10,
        totalValue: 1.50,
        status: 'low_stock'
      },
      {
        id: 2,
        name: 'Cables',
        currentStock: 75,
        reorderLevel: 50,
        unit: 'meters',
        location: 'warehouse',
        unitCost: 5.50,
        totalValue: 412.50,
        status: 'ok'
      },
      {
        id: 3,
        name: 'Circuit Boards',
        currentStock: 0,
        reorderLevel: 20,
        unit: 'pcs',
        location: 'warehouse',
        unitCost: 25.00,
        totalValue: 0.00,
        status: 'out_of_stock'
      }
    ]);

    setAlerts([
      {
        id: 1,
        productName: 'Screws',
        alertType: 'low_stock',
        currentStock: 15,
        reorderLevel: 100,
        priority: 'high',
        message: 'Screws stock is below reorder level',
        createdAt: '2024-01-15T15:00:00Z'
      },
      {
        id: 2,
        productName: 'Circuit Boards',
        alertType: 'out_of_stock',
        currentStock: 0,
        reorderLevel: 20,
        priority: 'critical',
        message: 'Circuit Boards are out of stock',
        createdAt: '2024-01-15T16:00:00Z'
      }
    ]);

    setTransactions([
      {
        id: 1,
        productName: 'Screws',
        transactionType: 'issue',
        quantity: -20,
        unit: 'pcs',
        referenceType: 'job',
        referenceNumber: 'JOB-2024-001',
        notes: 'Used in installation',
        transactionDate: '2024-01-15T14:30:00Z'
      },
      {
        id: 2,
        productName: 'Cables',
        transactionType: 'receipt',
        quantity: 25,
        unit: 'meters',
        referenceType: 'purchase',
        referenceNumber: 'PO-2024-001',
        notes: 'Stock replenishment',
        transactionDate: '2024-01-15T10:30:00Z'
      }
    ]);

    setJobParts([
      {
        id: 1,
        jobNumber: 'JOB-2024-001',
        productName: 'Screws',
        quantityRequired: 25,
        quantityUsed: 20,
        status: 'used',
        allocatedBy: 'John Manager',
        usedBy: 'Mike Technician'
      },
      {
        id: 2,
        jobNumber: 'JOB-2024-002',
        productName: 'Cables',
        quantityRequired: 10,
        quantityUsed: 0,
        status: 'allocated',
        allocatedBy: 'John Manager',
        usedBy: null
      }
    ]);
  }, []);

  const getStockStatusBadge = (status, currentStock, reorderLevel) => {
    if (status === 'out_of_stock' || currentStock === 0) {
      return <Badge variant="destructive">Out of Stock</Badge>;
    } else if (status === 'low_stock' || currentStock <= reorderLevel) {
      return <Badge variant="warning">Low Stock</Badge>;
    } else {
      return <Badge variant="success">In Stock</Badge>;
    }
  };

  const getPriorityBadge = (priority) => {
    const variants = {
      critical: 'destructive',
      high: 'warning',
      medium: 'default',
      low: 'secondary'
    };
    return <Badge variant={variants[priority]}>{priority.toUpperCase()}</Badge>;
  };

  const getTransactionTypeBadge = (type) => {
    const variants = {
      receipt: 'success',
      issue: 'warning',
      adjustment: 'default',
      transfer: 'secondary'
    };
    return <Badge variant={variants[type]}>{type.toUpperCase()}</Badge>;
  };

  const getJobPartsStatusBadge = (status) => {
    const variants = {
      planned: 'secondary',
      allocated: 'default',
      used: 'success',
      returned: 'warning'
    };
    return <Badge variant={variants[status]}>{status.toUpperCase()}</Badge>;
  };

  const filteredInventory = inventoryData.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const OverviewTab = () => (
    <div className="space-y-6">
      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            Active Alerts ({alerts.length})
          </h3>
          {alerts.map(alert => (
            <Alert key={alert.id} className="border-red-200">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="flex justify-between items-center">
                <div>
                  <strong>{alert.productName}</strong>: {alert.message}
                  <br />
                  Current: {alert.currentStock}, Reorder Level: {alert.reorderLevel}
                </div>
                <div className="flex gap-2">
                  {getPriorityBadge(alert.priority)}
                  <Button size="sm" variant="outline">Acknowledge</Button>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* Inventory Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Inventory Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{inventoryData.length}</div>
              <div className="text-sm text-gray-600">Total Products</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {inventoryData.filter(item => item.status === 'low_stock' || item.status === 'out_of_stock').length}
              </div>
              <div className="text-sm text-gray-600">Low/Out of Stock</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                ${inventoryData.reduce((sum, item) => sum + item.totalValue, 0).toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Total Value</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const InventoryTab = () => (
    <div className="space-y-4">
      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search inventory..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline" className="flex items-center gap-2">
          <Filter className="h-4 w-4" />
          Filter
        </Button>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Stock
        </Button>
      </div>

      {/* Inventory Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead>Current Stock</TableHead>
                <TableHead>Reorder Level</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Unit Cost</TableHead>
                <TableHead>Total Value</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredInventory.map(item => (
                <TableRow key={item.id}>
                  <TableCell className="font-medium">{item.name}</TableCell>
                  <TableCell>{item.currentStock} {item.unit}</TableCell>
                  <TableCell>{item.reorderLevel} {item.unit}</TableCell>
                  <TableCell>{item.location}</TableCell>
                  <TableCell>${item.unitCost.toFixed(2)}</TableCell>
                  <TableCell>${item.totalValue.toFixed(2)}</TableCell>
                  <TableCell>{getStockStatusBadge(item.status, item.currentStock, item.reorderLevel)}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">Adjust</Button>
                      <Button size="sm" variant="outline">Transfer</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  const TransactionsTab = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Recent Transactions</h3>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Transaction
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Product</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Reference</TableHead>
                <TableHead>Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map(transaction => (
                <TableRow key={transaction.id}>
                  <TableCell>{new Date(transaction.transactionDate).toLocaleDateString()}</TableCell>
                  <TableCell>{transaction.productName}</TableCell>
                  <TableCell>{getTransactionTypeBadge(transaction.transactionType)}</TableCell>
                  <TableCell className={transaction.quantity < 0 ? 'text-red-600' : 'text-green-600'}>
                    {transaction.quantity > 0 ? '+' : ''}{transaction.quantity} {transaction.unit}
                  </TableCell>
                  <TableCell>{transaction.referenceNumber}</TableCell>
                  <TableCell>{transaction.notes}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  const JobPartsTab = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Job Parts Assignments</h3>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Assign Parts
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Job Number</TableHead>
                <TableHead>Product</TableHead>
                <TableHead>Required</TableHead>
                <TableHead>Used</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Allocated By</TableHead>
                <TableHead>Used By</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {jobParts.map(jobPart => (
                <TableRow key={jobPart.id}>
                  <TableCell className="font-medium">{jobPart.jobNumber}</TableCell>
                  <TableCell>{jobPart.productName}</TableCell>
                  <TableCell>{jobPart.quantityRequired}</TableCell>
                  <TableCell>{jobPart.quantityUsed}</TableCell>
                  <TableCell>{getJobPartsStatusBadge(jobPart.status)}</TableCell>
                  <TableCell>{jobPart.allocatedBy}</TableCell>
                  <TableCell>{jobPart.usedBy || '-'}</TableCell>
                  <TableCell>
                    <Button size="sm" variant="outline">
                      {jobPart.status === 'allocated' ? 'Mark Used' : 'View'}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Inventory & Parts Management</h1>
        <div className="flex gap-2">
          <Button variant="outline">Export Report</Button>
          <Button variant="outline">Settings</Button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: Package },
            { id: 'inventory', label: 'Inventory', icon: Package },
            { id: 'transactions', label: 'Transactions', icon: Package },
            { id: 'job-parts', label: 'Job Parts', icon: Package }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'inventory' && <InventoryTab />}
        {activeTab === 'transactions' && <TransactionsTab />}
        {activeTab === 'job-parts' && <JobPartsTab />}
      </div>
    </div>
  );
};

export default InventoryManagement;