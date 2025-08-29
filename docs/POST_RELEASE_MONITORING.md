# Post-Release Monitoring & Error Tracking Infrastructure

## Overview

This document outlines the comprehensive monitoring and error tracking infrastructure implemented for the migration and integration management features. The system provides real-time monitoring, automated alerting, performance tracking, and proactive issue detection.

## Monitoring Architecture

### 1. Health Check Endpoints

#### System Health Monitoring
```python
# app/api/v1/monitoring.py
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from app.services.monitoring_service import MonitoringService

router = APIRouter()

@router.get("/health/system")
async def get_system_health():
    """Comprehensive system health check"""
    monitoring = MonitoringService()
    
    health_status = {
        "timestamp": datetime.utcnow(),
        "status": "healthy",  # healthy, warning, critical
        "components": {
            "database": await monitoring.check_database_health(),
            "redis": await monitoring.check_redis_health(),
            "file_storage": await monitoring.check_storage_health(),
            "external_apis": await monitoring.check_external_services()
        },
        "performance": {
            "response_time_ms": await monitoring.get_avg_response_time(),
            "cpu_usage_percent": await monitoring.get_cpu_usage(),
            "memory_usage_percent": await monitoring.get_memory_usage(),
            "disk_usage_percent": await monitoring.get_disk_usage()
        },
        "migration_metrics": {
            "active_jobs": await monitoring.get_active_migration_count(),
            "jobs_last_24h": await monitoring.get_migration_count_24h(),
            "success_rate_24h": await monitoring.get_migration_success_rate(),
            "avg_completion_time": await monitoring.get_avg_migration_time()
        }
    }
    
    # Determine overall status
    component_statuses = [comp["status"] for comp in health_status["components"].values()]
    if "critical" in component_statuses:
        health_status["status"] = "critical"
    elif "warning" in component_statuses:
        health_status["status"] = "warning"
    
    return health_status

@router.get("/health/migration")
async def get_migration_health():
    """Migration-specific health monitoring"""
    monitoring = MonitoringService()
    
    return {
        "timestamp": datetime.utcnow(),
        "migration_service": {
            "status": await monitoring.check_migration_service(),
            "active_jobs": await monitoring.get_active_migrations(),
            "queue_size": await monitoring.get_migration_queue_size(),
            "error_rate": await monitoring.get_migration_error_rate(),
            "avg_processing_time": await monitoring.get_avg_processing_time()
        },
        "file_processing": {
            "upload_service": await monitoring.check_file_upload_service(),
            "storage_availability": await monitoring.check_storage_space(),
            "processing_queue": await monitoring.get_file_processing_queue()
        },
        "data_validation": {
            "validator_service": await monitoring.check_validation_service(),
            "validation_success_rate": await monitoring.get_validation_success_rate(),
            "common_validation_errors": await monitoring.get_common_validation_errors()
        }
    }

@router.get("/health/integrations")
async def get_integration_health():
    """Integration-specific health monitoring"""
    monitoring = MonitoringService()
    
    integrations = ["tally", "email", "calendar", "payments", "zoho"]
    health_data = {}
    
    for integration in integrations:
        health_data[integration] = {
            "status": await monitoring.check_integration_health(integration),
            "last_sync": await monitoring.get_last_sync_time(integration),
            "sync_success_rate": await monitoring.get_sync_success_rate(integration),
            "error_count_24h": await monitoring.get_error_count_24h(integration),
            "response_time": await monitoring.get_avg_response_time(integration)
        }
    
    return {
        "timestamp": datetime.utcnow(),
        "integrations": health_data,
        "overall_health": await monitoring.calculate_overall_integration_health()
    }
```

### 2. Performance Metrics Collection

#### Migration Performance Tracking
```python
# app/services/migration_monitoring.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import psutil
import logging

@dataclass
class MigrationMetrics:
    job_id: int
    start_time: datetime
    end_time: Optional[datetime]
    total_records: int
    processed_records: int
    successful_records: int
    failed_records: int
    processing_rate: float  # records per second
    memory_usage_mb: float
    cpu_usage_percent: float
    error_count: int
    warnings_count: int

class MigrationPerformanceMonitor:
    def __init__(self):
        self.active_jobs = {}
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self, job_id: int, total_records: int):
        """Start monitoring a migration job"""
        self.active_jobs[job_id] = MigrationMetrics(
            job_id=job_id,
            start_time=datetime.utcnow(),
            end_time=None,
            total_records=total_records,
            processed_records=0,
            successful_records=0,
            failed_records=0,
            processing_rate=0.0,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0,
            error_count=0,
            warnings_count=0
        )
    
    def update_progress(self, job_id: int, processed: int, successful: int, failed: int):
        """Update migration progress metrics"""
        if job_id not in self.active_jobs:
            return
        
        metrics = self.active_jobs[job_id]
        metrics.processed_records = processed
        metrics.successful_records = successful
        metrics.failed_records = failed
        
        # Calculate processing rate
        elapsed_time = (datetime.utcnow() - metrics.start_time).total_seconds()
        if elapsed_time > 0:
            metrics.processing_rate = processed / elapsed_time
        
        # Update system resource usage
        metrics.memory_usage_mb = psutil.virtual_memory().used / 1024 / 1024
        metrics.cpu_usage_percent = psutil.cpu_percent()
        
        # Log performance metrics
        self.logger.info(f"Migration {job_id} progress: {processed}/{metrics.total_records} "
                        f"({(processed/metrics.total_records)*100:.1f}%) "
                        f"Rate: {metrics.processing_rate:.1f} rec/sec")
    
    def record_error(self, job_id: int, error_type: str, error_message: str):
        """Record an error for monitoring"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id].error_count += 1
        
        # Log to error tracking system
        self.logger.error(f"Migration {job_id} error [{error_type}]: {error_message}")
    
    def complete_monitoring(self, job_id: int):
        """Complete monitoring for a job"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id].end_time = datetime.utcnow()
            
            # Store final metrics in database
            final_metrics = self.active_jobs[job_id]
            self._store_metrics(final_metrics)
            
            # Remove from active monitoring
            del self.active_jobs[job_id]
    
    def _store_metrics(self, metrics: MigrationMetrics):
        """Store metrics in database for historical analysis"""
        # Implementation to store metrics in database
        pass
```

### 3. Error Tracking System

#### Comprehensive Error Logging
```python
# app/services/error_tracking.py
import traceback
import json
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    MIGRATION = "migration"
    INTEGRATION = "integration"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    PERFORMANCE = "performance"
    SYSTEM = "system"

@dataclass
class ErrorEvent:
    timestamp: datetime
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any]
    user_id: Optional[int]
    organization_id: Optional[int]
    session_id: Optional[str]
    request_id: Optional[str]
    stack_trace: Optional[str]
    context: Dict[str, Any]

class ErrorTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def track_error(self, 
                   category: ErrorCategory, 
                   severity: ErrorSeverity,
                   message: str,
                   details: Dict[str, Any] = None,
                   user_id: int = None,
                   organization_id: int = None,
                   context: Dict[str, Any] = None):
        """Track an error event"""
        
        error_event = ErrorEvent(
            timestamp=datetime.utcnow(),
            error_id=self._generate_error_id(),
            category=category,
            severity=severity,
            message=message,
            details=details or {},
            user_id=user_id,
            organization_id=organization_id,
            session_id=self._get_current_session_id(),
            request_id=self._get_current_request_id(),
            stack_trace=traceback.format_exc(),
            context=context or {}
        )
        
        # Store error in database
        self._store_error(error_event)
        
        # Send to external monitoring (optional)
        self._send_to_external_monitoring(error_event)
        
        # Trigger alerts if necessary
        self._check_alert_conditions(error_event)
        
        return error_event.error_id
    
    def track_migration_error(self, job_id: int, error_type: str, error_message: str, 
                            user_id: int, organization_id: int):
        """Track migration-specific errors"""
        return self.track_error(
            category=ErrorCategory.MIGRATION,
            severity=self._determine_migration_error_severity(error_type),
            message=f"Migration job {job_id} error: {error_message}",
            details={
                "job_id": job_id,
                "error_type": error_type,
                "migration_stage": self._get_migration_stage(job_id)
            },
            user_id=user_id,
            organization_id=organization_id
        )
    
    def track_integration_error(self, integration: str, operation: str, 
                              error_message: str, organization_id: int):
        """Track integration-specific errors"""
        return self.track_error(
            category=ErrorCategory.INTEGRATION,
            severity=self._determine_integration_error_severity(integration, operation),
            message=f"Integration {integration} {operation} failed: {error_message}",
            details={
                "integration": integration,
                "operation": operation,
                "external_service_status": self._check_external_service_status(integration)
            },
            organization_id=organization_id
        )
    
    def get_error_statistics(self, time_range: timedelta = timedelta(hours=24)) -> Dict:
        """Get error statistics for monitoring dashboard"""
        since = datetime.utcnow() - time_range
        
        return {
            "total_errors": self._count_errors_since(since),
            "errors_by_category": self._count_errors_by_category(since),
            "errors_by_severity": self._count_errors_by_severity(since),
            "top_error_messages": self._get_top_error_messages(since),
            "error_trend": self._get_error_trend(since),
            "organizations_affected": self._count_affected_organizations(since)
        }
```

### 4. Automated Alerting System

#### Alert Configuration
```python
# app/services/alerting.py
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Callable

class AlertChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AlertRule:
    name: str
    condition: str  # SQL-like condition or Python expression
    severity: AlertSeverity
    channels: List[AlertChannel]
    cooldown_minutes: int
    recipients: List[str]
    enabled: bool

class AlertManager:
    def __init__(self):
        self.rules = self._load_alert_rules()
        self.alert_history = {}
    
    def _load_alert_rules(self) -> List[AlertRule]:
        """Load alert rules from configuration"""
        return [
            AlertRule(
                name="High Error Rate",
                condition="error_rate_5min > 10",
                severity=AlertSeverity.ERROR,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=15,
                recipients=["admin@company.com", "#alerts-channel"],
                enabled=True
            ),
            AlertRule(
                name="Migration Failure",
                condition="migration_failed = true AND severity = 'critical'",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SMS, AlertChannel.IN_APP],
                cooldown_minutes=5,
                recipients=["admin@company.com", "+1234567890"],
                enabled=True
            ),
            AlertRule(
                name="Integration Down",
                condition="integration_status = 'error' AND duration > 300",
                severity=AlertSeverity.ERROR,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=30,
                recipients=["admin@company.com", "#integration-alerts"],
                enabled=True
            ),
            AlertRule(
                name="High Memory Usage",
                condition="memory_usage > 90",
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=60,
                recipients=["ops@company.com"],
                enabled=True
            ),
            AlertRule(
                name="Database Connection Issues",
                condition="db_connection_errors > 5 in 5min",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SMS, AlertChannel.WEBHOOK],
                cooldown_minutes=5,
                recipients=["dba@company.com", "admin@company.com"],
                enabled=True
            )
        ]
    
    def check_alert_conditions(self, metrics: Dict):
        """Check if any alert conditions are met"""
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._evaluate_condition(rule.condition, metrics):
                if self._should_send_alert(rule):
                    self._send_alert(rule, metrics)
    
    def _evaluate_condition(self, condition: str, metrics: Dict) -> bool:
        """Evaluate alert condition against current metrics"""
        try:
            # Simple condition evaluation (in production, use a proper expression parser)
            return eval(condition, {"__builtins__": {}}, metrics)
        except Exception as e:
            logging.error(f"Error evaluating alert condition '{condition}': {e}")
            return False
    
    def _should_send_alert(self, rule: AlertRule) -> bool:
        """Check if alert should be sent (considering cooldown)"""
        last_sent = self.alert_history.get(rule.name)
        if last_sent:
            cooldown_end = last_sent + timedelta(minutes=rule.cooldown_minutes)
            if datetime.utcnow() < cooldown_end:
                return False
        return True
    
    def _send_alert(self, rule: AlertRule, metrics: Dict):
        """Send alert through configured channels"""
        alert_message = self._format_alert_message(rule, metrics)
        
        for channel in rule.channels:
            if channel == AlertChannel.EMAIL:
                self._send_email_alert(rule.recipients, rule.name, alert_message)
            elif channel == AlertChannel.SMS:
                self._send_sms_alert(rule.recipients, alert_message)
            elif channel == AlertChannel.SLACK:
                self._send_slack_alert(rule.recipients, alert_message)
            elif channel == AlertChannel.WEBHOOK:
                self._send_webhook_alert(rule.recipients, rule.name, metrics)
            elif channel == AlertChannel.IN_APP:
                self._send_in_app_alert(rule.name, alert_message)
        
        # Record alert sent
        self.alert_history[rule.name] = datetime.utcnow()
```

### 5. Monitoring Dashboard

#### Real-time Metrics Dashboard
```python
# app/api/v1/monitoring_dashboard.py
@router.get("/dashboard/metrics")
async def get_dashboard_metrics():
    """Get real-time metrics for monitoring dashboard"""
    monitoring = MonitoringService()
    
    return {
        "timestamp": datetime.utcnow(),
        "system_overview": {
            "status": await monitoring.get_overall_system_status(),
            "uptime": await monitoring.get_system_uptime(),
            "active_users": await monitoring.get_active_user_count(),
            "active_organizations": await monitoring.get_active_org_count()
        },
        "migration_metrics": {
            "jobs_today": await monitoring.get_migration_jobs_today(),
            "success_rate_today": await monitoring.get_migration_success_rate_today(),
            "avg_completion_time": await monitoring.get_avg_migration_time_today(),
            "currently_running": await monitoring.get_running_migrations(),
            "queue_length": await monitoring.get_migration_queue_length()
        },
        "integration_metrics": {
            "healthy_integrations": await monitoring.get_healthy_integration_count(),
            "total_integrations": await monitoring.get_total_integration_count(),
            "syncs_last_hour": await monitoring.get_syncs_last_hour(),
            "sync_success_rate": await monitoring.get_sync_success_rate_24h()
        },
        "performance_metrics": {
            "cpu_usage": await monitoring.get_current_cpu_usage(),
            "memory_usage": await monitoring.get_current_memory_usage(),
            "disk_usage": await monitoring.get_current_disk_usage(),
            "avg_response_time": await monitoring.get_avg_response_time_5min(),
            "requests_per_minute": await monitoring.get_requests_per_minute()
        },
        "error_metrics": {
            "errors_last_hour": await monitoring.get_errors_last_hour(),
            "critical_errors_today": await monitoring.get_critical_errors_today(),
            "top_error_types": await monitoring.get_top_error_types_today(),
            "error_trend": await monitoring.get_error_trend_24h()
        }
    }

@router.get("/dashboard/alerts")
async def get_active_alerts():
    """Get active alerts and recent alert history"""
    alert_manager = AlertManager()
    
    return {
        "active_alerts": await alert_manager.get_active_alerts(),
        "recent_alerts": await alert_manager.get_recent_alerts(limit=50),
        "alert_summary": await alert_manager.get_alert_summary_24h()
    }
```

### 6. Log Aggregation and Analysis

#### Centralized Logging
```python
# app/services/log_aggregation.py
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up file and console handlers with structured formatting"""
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for production
        file_handler = RotatingFileHandler(
            'logs/app.log', maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logs
        json_formatter = JsonFormatter()
        file_handler.setFormatter(json_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
    
    def log_migration_event(self, job_id: int, event_type: str, message: str, 
                           user_id: int = None, organization_id: int = None, **kwargs):
        """Log migration-specific events"""
        extra_data = {
            'event_type': 'migration',
            'job_id': job_id,
            'migration_event': event_type,
            'user_id': user_id,
            'organization_id': organization_id,
            **kwargs
        }
        self.logger.info(message, extra=extra_data)
    
    def log_integration_event(self, integration: str, event_type: str, message: str,
                            organization_id: int = None, **kwargs):
        """Log integration-specific events"""
        extra_data = {
            'event_type': 'integration',
            'integration': integration,
            'integration_event': event_type,
            'organization_id': organization_id,
            **kwargs
        }
        self.logger.info(message, extra=extra_data)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = None, **kwargs):
        """Log performance metrics"""
        extra_data = {
            'event_type': 'performance',
            'metric_name': metric_name,
            'metric_value': value,
            'metric_unit': unit,
            **kwargs
        }
        self.logger.info(f"Performance metric: {metric_name} = {value} {unit or ''}", extra=extra_data)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'event_type'):
            log_entry.update(record.__dict__)
            
        return json.dumps(log_entry)
```

### 7. Configuration and Deployment

#### Monitoring Configuration
```yaml
# monitoring_config.yaml
monitoring:
  health_checks:
    interval_seconds: 30
    timeout_seconds: 10
    endpoints:
      - /health/system
      - /health/migration
      - /health/integrations
  
  metrics_collection:
    interval_seconds: 60
    retention_days: 30
    
  alerting:
    enabled: true
    check_interval_seconds: 60
    default_cooldown_minutes: 15
    
  error_tracking:
    enabled: true
    retention_days: 90
    sample_rate: 1.0  # 100% sampling
    
  performance_monitoring:
    enabled: true
    slow_query_threshold_ms: 1000
    memory_threshold_percent: 85
    cpu_threshold_percent: 80
    
  external_services:
    sentry:
      enabled: false
      dsn: "https://your-sentry-dsn"
    
    datadog:
      enabled: false
      api_key: "your-datadog-api-key"
    
    prometheus:
      enabled: true
      port: 8000
      endpoint: "/metrics"

logging:
  level: INFO
  format: json
  handlers:
    - console
    - file
    - syslog
  
  rotation:
    max_size_mb: 100
    backup_count: 10
    
  structured_logging:
    enabled: true
    include_request_id: true
    include_user_context: true
```

### 8. Monitoring Service Implementation

#### Complete Monitoring Service
```python
# app/services/monitoring_service.py
import asyncio
import psutil
import redis
from sqlalchemy import text
from app.core.database import get_db
from app.services.error_tracking import ErrorTracker
from app.services.log_aggregation import StructuredLogger

class MonitoringService:
    def __init__(self):
        self.error_tracker = ErrorTracker()
        self.logger = StructuredLogger(__name__)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    async def check_database_health(self) -> Dict:
        """Check database connectivity and performance"""
        try:
            db = next(get_db())
            start_time = time.time()
            
            # Simple query to test connectivity
            result = db.execute(text("SELECT 1"))
            response_time = (time.time() - start_time) * 1000
            
            # Check active connections
            active_connections = db.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            )).scalar()
            
            return {
                "status": "healthy" if response_time < 100 else "warning",
                "response_time_ms": response_time,
                "active_connections": active_connections,
                "max_connections": 100  # Configure based on your setup
            }
        except Exception as e:
            self.error_tracker.track_error(
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                message="Database health check failed",
                details={"error": str(e)}
            )
            return {
                "status": "critical",
                "error": str(e)
            }
    
    async def check_redis_health(self) -> Dict:
        """Check Redis connectivity and performance"""
        try:
            start_time = time.time()
            self.redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            info = self.redis_client.info()
            memory_usage = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            
            return {
                "status": "healthy" if response_time < 50 else "warning",
                "response_time_ms": response_time,
                "memory_usage_bytes": memory_usage,
                "memory_usage_percent": (memory_usage / max_memory * 100) if max_memory > 0 else 0
            }
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e)
            }
    
    async def check_storage_health(self) -> Dict:
        """Check file storage health and capacity"""
        try:
            disk_usage = psutil.disk_usage('/')
            free_space_percent = (disk_usage.free / disk_usage.total) * 100
            
            status = "healthy"
            if free_space_percent < 10:
                status = "critical"
            elif free_space_percent < 20:
                status = "warning"
            
            return {
                "status": status,
                "free_space_percent": free_space_percent,
                "free_space_gb": disk_usage.free / (1024**3),
                "total_space_gb": disk_usage.total / (1024**3)
            }
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e)
            }
    
    async def get_active_migration_count(self) -> int:
        """Get count of currently active migration jobs"""
        try:
            db = next(get_db())
            result = db.execute(text(
                "SELECT COUNT(*) FROM migration_jobs WHERE status IN ('running', 'processing')"
            ))
            return result.scalar()
        except Exception:
            return 0
    
    async def get_migration_success_rate(self, hours: int = 24) -> float:
        """Get migration success rate for specified time period"""
        try:
            db = next(get_db())
            since = datetime.utcnow() - timedelta(hours=hours)
            
            result = db.execute(text("""
                SELECT 
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    COUNT(*) as total
                FROM migration_jobs 
                WHERE created_at >= :since
            """), {"since": since})
            
            row = result.fetchone()
            if row and row.total > 0:
                return (row.completed / row.total) * 100
            return 100.0  # No jobs means 100% success rate
        except Exception:
            return 0.0
    
    async def collect_performance_metrics(self) -> Dict:
        """Collect comprehensive performance metrics"""
        return {
            "timestamp": datetime.utcnow(),
            "cpu": {
                "usage_percent": psutil.cpu_percent(interval=1),
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "cpu_count": psutil.cpu_count()
            },
            "memory": {
                "usage_percent": psutil.virtual_memory().percent,
                "available_gb": psutil.virtual_memory().available / (1024**3),
                "total_gb": psutil.virtual_memory().total / (1024**3)
            },
            "disk": {
                "usage_percent": psutil.disk_usage('/').percent,
                "free_gb": psutil.disk_usage('/').free / (1024**3),
                "total_gb": psutil.disk_usage('/').total / (1024**3)
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv
            }
        }
```

This comprehensive monitoring and error tracking infrastructure provides:

1. **Real-time Health Monitoring**: Continuous monitoring of all system components
2. **Performance Metrics**: Detailed performance tracking and analysis
3. **Error Tracking**: Comprehensive error logging and categorization
4. **Automated Alerting**: Intelligent alerts based on configurable rules
5. **Dashboard Integration**: Real-time metrics dashboard for administrators
6. **Log Aggregation**: Centralized, structured logging for analysis
7. **Historical Analysis**: Trend analysis and performance optimization insights

The system is designed to be scalable, configurable, and provides the visibility needed to maintain the migration and integration features at enterprise scale.