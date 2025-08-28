// services/transportService.ts
// Transport and Freight Management service for API interactions

import api from '../lib/api';

export interface Carrier {
  id: number;
  carrier_code: string;
  carrier_name: string;
  carrier_type: 'road' | 'rail' | 'air' | 'sea' | 'courier' | 'multimodal';
  contact_person?: string;
  phone?: string;
  email?: string;
  city?: string;
  state?: string;
  rating: number;
  on_time_percentage: number;
  tracking_capability: boolean;
  is_active: boolean;
  is_preferred: boolean;
  created_at: string;
}

export interface Route {
  id: number;
  route_code: string;
  route_name: string;
  carrier_id: number;
  origin_city: string;
  destination_city: string;
  distance_km?: number;
  estimated_transit_time_hours?: number;
  status: 'active' | 'inactive' | 'seasonal' | 'suspended';
  created_at: string;
}

export interface FreightRate {
  id: number;
  rate_code: string;
  carrier_id: number;
  route_id?: number;
  effective_date: string;
  expiry_date?: string;
  freight_mode: 'ltl' | 'ftl' | 'express' | 'standard' | 'economy';
  rate_basis: string;
  minimum_charge: number;
  is_active: boolean;
  created_at: string;
}

export interface Shipment {
  id: number;
  shipment_number: string;
  carrier_id: number;
  tracking_number?: string;
  freight_mode: 'ltl' | 'ftl' | 'express' | 'standard' | 'economy';
  origin_city: string;
  destination_city: string;
  total_weight_kg: number;
  total_volume_cbm: number;
  total_pieces: number;
  declared_value: number;
  status: 'planned' | 'booked' | 'in_transit' | 'delivered' | 'cancelled' | 'delayed';
  pickup_date?: string;
  expected_delivery_date?: string;
  actual_delivery_date?: string;
  total_charges: number;
  created_at: string;
}

export interface TransportDashboard {
  total_carriers: number;
  active_shipments: number;
  delivered_this_month: number;
  pending_pickups: number;
  total_freight_cost_this_month: number;
}

export interface CarrierCreate {
  carrier_code: string;
  carrier_name: string;
  carrier_type: 'road' | 'rail' | 'air' | 'sea' | 'courier' | 'multimodal';
  contact_person?: string;
  phone?: string;
  email?: string;
  website?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  license_number?: string;
  license_expiry_date?: string;
  insurance_number?: string;
  insurance_expiry_date?: string;
  service_areas?: string[];
  vehicle_types?: string[];
  special_handling?: string[];
  payment_terms?: string;
  credit_limit?: number;
  tracking_capability?: boolean;
  real_time_updates?: boolean;
  is_preferred?: boolean;
  notes?: string;
}

export interface RouteCreate {
  route_code: string;
  route_name: string;
  carrier_id: number;
  origin_city: string;
  origin_state?: string;
  origin_country?: string;
  destination_city: string;
  destination_state?: string;
  destination_country?: string;
  distance_km?: number;
  estimated_transit_time_hours?: number;
  max_transit_time_hours?: number;
  vehicle_type?: 'truck' | 'van' | 'container' | 'aircraft' | 'ship' | 'train';
  frequency?: string;
  operating_days?: string[];
  max_weight_kg?: number;
  max_volume_cbm?: number;
  temperature_controlled?: boolean;
  hazmat_allowed?: boolean;
  fuel_surcharge_applicable?: boolean;
  toll_charges_applicable?: boolean;
  notes?: string;
}

export interface FreightRateCreate {
  rate_code: string;
  carrier_id: number;
  route_id?: number;
  effective_date: string;
  expiry_date?: string;
  freight_mode: 'ltl' | 'ftl' | 'express' | 'standard' | 'economy';
  service_type?: string;
  rate_basis: string;
  minimum_charge?: number;
  rate_per_kg?: number;
  minimum_weight_kg?: number;
  maximum_weight_kg?: number;
  rate_per_cbm?: number;
  minimum_volume_cbm?: number;
  maximum_volume_cbm?: number;
  rate_per_km?: number;
  fixed_rate?: number;
  fuel_surcharge_percentage?: number;
  handling_charge?: number;
  documentation_charge?: number;
  insurance_percentage?: number;
  standard_transit_days?: number;
  currency?: string;
  tax_applicable?: boolean;
  tax_percentage?: number;
  is_negotiated?: boolean;
  notes?: string;
  terms_conditions?: string;
}

export interface ShipmentCreate {
  carrier_id: number;
  route_id?: number;
  sales_order_id?: number;
  purchase_order_id?: number;
  manufacturing_order_id?: number;
  freight_mode: 'ltl' | 'ftl' | 'express' | 'standard' | 'economy';
  service_type?: string;
  origin_name: string;
  origin_address?: string;
  origin_city: string;
  origin_state?: string;
  origin_postal_code?: string;
  origin_country?: string;
  destination_name: string;
  destination_address?: string;
  destination_city: string;
  destination_state?: string;
  destination_postal_code?: string;
  destination_country?: string;
  declared_value?: number;
  is_fragile?: boolean;
  is_hazardous?: boolean;
  temperature_controlled?: boolean;
  signature_required?: boolean;
  pickup_date?: string;
  pickup_time_from?: string;
  pickup_time_to?: string;
  expected_delivery_date?: string;
  payment_terms?: string;
  cod_amount?: number;
  special_instructions?: string;
  notes?: string;
  items: Array<{
    product_id: number;
    quantity: number;
    unit: string;
    weight_per_unit_kg?: number;
    volume_per_unit_cbm?: number;
    packaging_type?: string;
    number_of_packages?: number;
    package_dimensions?: string;
    batch_number?: string;
    unit_value?: number;
    handling_instructions?: string;
    notes?: string;
  }>;
}

class TransportService {
  // Carrier Management
  async getCarriers(params?: {
    skip?: number;
    limit?: number;
    carrier_type?: string;
    is_active?: boolean;
    is_preferred?: boolean;
  }): Promise<Carrier[]> {
    const response = await api.get('/api/v1/transport/carriers/', { params });
    return response.data;
  }

  async getCarrier(id: number): Promise<Carrier> {
    const response = await api.get(`/api/v1/transport/carriers/${id}`);
    return response.data;
  }

  async createCarrier(data: CarrierCreate): Promise<Carrier> {
    const response = await api.post('/api/v1/transport/carriers/', data);
    return response.data;
  }

  async updateCarrier(id: number, data: Partial<CarrierCreate>): Promise<Carrier> {
    const response = await api.put(`/api/v1/transport/carriers/${id}`, data);
    return response.data;
  }

  // Route Management
  async getRoutes(params?: {
    skip?: number;
    limit?: number;
    carrier_id?: number;
    origin_city?: string;
    destination_city?: string;
    status?: string;
  }): Promise<Route[]> {
    const response = await api.get('/api/v1/transport/routes/', { params });
    return response.data;
  }

  async createRoute(data: RouteCreate): Promise<Route> {
    const response = await api.post('/api/v1/transport/routes/', data);
    return response.data;
  }

  // Freight Rate Management
  async getFreightRates(params?: {
    skip?: number;
    limit?: number;
    carrier_id?: number;
    route_id?: number;
    freight_mode?: string;
    is_active?: boolean;
  }): Promise<FreightRate[]> {
    const response = await api.get('/api/v1/transport/freight-rates/', { params });
    return response.data;
  }

  async createFreightRate(data: FreightRateCreate): Promise<FreightRate> {
    const response = await api.post('/api/v1/transport/freight-rates/', data);
    return response.data;
  }

  // Rate Comparison
  async compareFreightRates(data: {
    origin_city: string;
    destination_city: string;
    weight_kg: number;
    volume_cbm?: number;
    freight_mode?: string;
  }): Promise<any> {
    const response = await api.post('/api/v1/transport/freight-rates/compare', data);
    return response.data;
  }

  // Shipment Management
  async getShipments(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    carrier_id?: number;
    tracking_number?: string;
  }): Promise<Shipment[]> {
    const response = await api.get('/api/v1/transport/shipments/', { params });
    return response.data;
  }

  async createShipment(data: ShipmentCreate): Promise<Shipment> {
    const response = await api.post('/api/v1/transport/shipments/', data);
    return response.data;
  }

  async getShipmentTracking(shipmentId: number): Promise<any> {
    const response = await api.get(`/api/v1/transport/shipments/${shipmentId}/tracking`);
    return response.data;
  }

  async addTrackingEvent(
    shipmentId: number,
    data: {
      event_type: string;
      status: string;
      description: string;
      location?: string;
      city?: string;
      state?: string;
      country?: string;
      is_exception?: boolean;
      exception_reason?: string;
      notes?: string;
    }
  ): Promise<any> {
    const response = await api.post(`/api/v1/transport/shipments/${shipmentId}/tracking`, data);
    return response.data;
  }

  // Dashboard
  async getDashboardSummary(): Promise<TransportDashboard> {
    const response = await api.get('/api/v1/transport/dashboard/summary');
    return response.data;
  }
}

export const transportService = new TransportService();