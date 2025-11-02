/**
 * Streaming Analytics Service
 * Service for real-time streaming data and analytics
 */

import axios from 'axios';
import { getApiUrl, getApiBaseUrl } from '../utils/config';

const STREAMING_API = `${getApiUrl()}/streaming-analytics`;

export enum StreamStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  ERROR = 'error',
  STOPPED = 'stopped',
}

export enum AlertSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

export enum AlertStatus {
  OPEN = 'open',
  ACKNOWLEDGED = 'acknowledged',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
}

export interface DataSource {
  id: number;
  organization_id: number;
  source_name: string;
  source_type: string;
  description?: string;
  status: StreamStatus;
  is_active: boolean;
  message_count: number;
  error_count: number;
  last_message_at?: string;
  created_at: string;
}

export interface StreamingEvent {
  id: number;
  data_source_id: number;
  event_type: string;
  event_data: Record<string, any>;
  event_timestamp: string;
  processed: boolean;
  received_at: string;
}

export interface LivePrediction {
  id: number;
  organization_id: number;
  model_id?: number;
  prediction_type: string;
  prediction_result: Record<string, any>;
  confidence_score?: number;
  predicted_at: string;
}

export interface StreamingAlert {
  id: number;
  organization_id: number;
  alert_type: string;
  alert_title: string;
  alert_message: string;
  severity: AlertSeverity;
  status: AlertStatus;
  triggered_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
}

export interface StreamingMetric {
  id: number;
  organization_id: number;
  metric_name: string;
  metric_value: number;
  aggregation_type: string;
  time_window: string;
  window_start: string;
  window_end: string;
}

export interface DashboardData {
  active_data_sources: number;
  recent_events_1h: number;
  open_alerts: number;
  recent_predictions_1h: number;
  timestamp: string;
}

export interface DataSourceCreate {
  source_name: string;
  source_type: string;
  connection_config: Record<string, any>;
  description?: string;
}

export interface EventCreate {
  data_source_id: number;
  event_type: string;
  event_data: Record<string, any>;
  event_timestamp?: string;
}

export interface LivePredictionCreate {
  prediction_type: string;
  input_data: Record<string, any>;
  prediction_result: Record<string, any>;
  model_id?: number;
  confidence_score?: number;
  context?: Record<string, any>;
}

export interface AlertCreate {
  alert_type: string;
  alert_title: string;
  alert_message: string;
  severity?: AlertSeverity;
  data_source_id?: number;
  alert_data?: Record<string, any>;
}

class StreamingAnalyticsService {
  private getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // ============================================================================
  // DATA SOURCE MANAGEMENT
  // ============================================================================

  async createDataSource(data: DataSourceCreate): Promise<DataSource> {
    const response = await axios.post<DataSource>(
      `${STREAMING_API}/data-sources`,
      data,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async listDataSources(
    status?: StreamStatus,
    skip: number = 0,
    limit: number = 100
  ): Promise<DataSource[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());

    const response = await axios.get<DataSource[]>(
      `${STREAMING_API}/data-sources?${params.toString()}`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async getDataSource(sourceId: number): Promise<DataSource> {
    const response = await axios.get<DataSource>(
      `${STREAMING_API}/data-sources/${sourceId}`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async updateDataSource(
    sourceId: number,
    updates: Partial<DataSourceCreate>
  ): Promise<DataSource> {
    const response = await axios.patch<DataSource>(
      `${STREAMING_API}/data-sources/${sourceId}`,
      updates,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // ============================================================================
  // EVENT INGESTION
  // ============================================================================

  async ingestEvent(data: EventCreate): Promise<StreamingEvent> {
    const response = await axios.post<StreamingEvent>(
      `${STREAMING_API}/events`,
      data,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async getRecentEvents(
    dataSourceId?: number,
    eventType?: string,
    minutes: number = 60,
    limit: number = 100
  ): Promise<StreamingEvent[]> {
    const params = new URLSearchParams();
    if (dataSourceId) params.append('data_source_id', dataSourceId.toString());
    if (eventType) params.append('event_type', eventType);
    params.append('minutes', minutes.toString());
    params.append('limit', limit.toString());

    const response = await axios.get<StreamingEvent[]>(
      `${STREAMING_API}/events?${params.toString()}`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // ============================================================================
  // LIVE PREDICTIONS
  // ============================================================================

  async recordLivePrediction(data: LivePredictionCreate): Promise<LivePrediction> {
    const response = await axios.post<LivePrediction>(
      `${STREAMING_API}/predictions`,
      data,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async getRecentPredictions(
    predictionType?: string,
    modelId?: number,
    minutes: number = 60,
    limit: number = 100
  ): Promise<LivePrediction[]> {
    const params = new URLSearchParams();
    if (predictionType) params.append('prediction_type', predictionType);
    if (modelId) params.append('model_id', modelId.toString());
    params.append('minutes', minutes.toString());
    params.append('limit', limit.toString());

    const response = await axios.get<LivePrediction[]>(
      `${STREAMING_API}/predictions?${params.toString()}`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // ============================================================================
  // ALERTS
  // ============================================================================

  async createAlert(data: AlertCreate): Promise<StreamingAlert> {
    const response = await axios.post<StreamingAlert>(
      `${STREAMING_API}/alerts`,
      data,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async getAlerts(
    status?: AlertStatus,
    severity?: AlertSeverity,
    skip: number = 0,
    limit: number = 100
  ): Promise<StreamingAlert[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (severity) params.append('severity', severity);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());

    const response = await axios.get<StreamingAlert[]>(
      `${STREAMING_API}/alerts?${params.toString()}`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async acknowledgeAlert(alertId: number): Promise<StreamingAlert> {
    const response = await axios.post<StreamingAlert>(
      `${STREAMING_API}/alerts/acknowledge`,
      { alert_id: alertId },
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async resolveAlert(
    alertId: number,
    resolutionNotes?: string
  ): Promise<StreamingAlert> {
    const response = await axios.post<StreamingAlert>(
      `${STREAMING_API}/alerts/resolve`,
      { alert_id: alertId, resolution_notes: resolutionNotes },
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // ============================================================================
  // METRICS
  // ============================================================================

  async getMetrics(
    metricName?: string,
    timeWindow?: string,
    limit: number = 100
  ): Promise<StreamingMetric[]> {
    const params = new URLSearchParams();
    if (metricName) params.append('metric_name', metricName);
    if (timeWindow) params.append('time_window', timeWindow);
    params.append('limit', limit.toString());

    const response = await axios.get<StreamingMetric[]>(
      `${STREAMING_API}/metrics?${params.toString()}`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // ============================================================================
  // DASHBOARD
  // ============================================================================

  async getDashboardData(): Promise<DashboardData> {
    const response = await axios.get<DashboardData>(
      `${STREAMING_API}/dashboard`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // ============================================================================
  // WEBSOCKET CONNECTION
  // ============================================================================

  createWebSocketConnection(onMessage: (data: any) => void): WebSocket | null {
    try {
      const token = localStorage.getItem('token');
      // Convert HTTP(S) URL to WS(S) URL safely
      const apiUrl = getApiUrl();
      const wsUrl = apiUrl.replace(/^http(s?):\/\//, 'ws$1://') + '/streaming-analytics/ws/live-stream';
      
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connection established');
        // Send auth token if needed
        if (token) {
          ws.send(JSON.stringify({ type: 'auth', token }));
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket connection closed');
      };

      return ws;
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      return null;
    }
  }
}

export default new StreamingAnalyticsService();
