"""
Performance Monitoring and Optimization Service
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from dataclasses import dataclass
from functools import wraps
import psutil
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None


@dataclass
class SystemHealth:
    """System health status"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    database_connections: int
    response_time_avg: float
    error_rate: float
    timestamp: datetime


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self, db: Session):
        self.db = db
        self.metrics_buffer = []
        self.alerts_config = {}
        self.monitoring_active = False
        self.response_times = []
        self.error_count = 0
        self.request_count = 0
        self._lock = threading.Lock()
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring_active = True
        threading.Thread(target=self._monitoring_loop, daemon=True).start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        logger.info("Performance monitoring stopped")
    
    def record_metric(self, name: str, value: float, unit: str = "", tags: Dict[str, str] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow(),
            tags=tags or {}
        )
        
        with self._lock:
            self.metrics_buffer.append(metric)
    
    def record_response_time(self, response_time: float):
        """Record API response time"""
        with self._lock:
            self.response_times.append(response_time)
            self.request_count += 1
            
            # Keep only last 1000 response times
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
    
    def record_error(self):
        """Record an error occurrence"""
        with self._lock:
            self.error_count += 1
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health metrics"""
        # CPU and Memory usage
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database connections
        try:
            db_connections = self.db.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            ).scalar() or 0
        except Exception:
            db_connections = 0
        
        # Response time average
        with self._lock:
            if self.response_times:
                avg_response_time = sum(self.response_times) / len(self.response_times)
            else:
                avg_response_time = 0.0
            
            # Error rate (errors per 100 requests)
            if self.request_count > 0:
                error_rate = (self.error_count / self.request_count) * 100
            else:
                error_rate = 0.0
        
        return SystemHealth(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            database_connections=db_connections,
            response_time_avg=avg_response_time,
            error_rate=error_rate,
            timestamp=datetime.utcnow()
        )
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter metrics by time
        recent_metrics = [m for m in self.metrics_buffer if m.timestamp >= cutoff_time]
        
        # Group metrics by name
        metrics_by_name = {}
        for metric in recent_metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric.value)
        
        # Calculate statistics
        summary = {}
        for name, values in metrics_by_name.items():
            if values:
                summary[name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "latest": values[-1]
                }
        
        return summary
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                health = self.get_system_health()
                
                # Record system metrics
                self.record_metric("cpu_usage", health.cpu_usage, "percent")
                self.record_metric("memory_usage", health.memory_usage, "percent")
                self.record_metric("disk_usage", health.disk_usage, "percent")
                self.record_metric("db_connections", health.database_connections, "count")
                self.record_metric("response_time_avg", health.response_time_avg, "ms")
                self.record_metric("error_rate", health.error_rate, "percent")
                
                # Check alerts
                self._check_alerts(health)
                
                # Clean old metrics (keep last 24 hours)
                self._clean_old_metrics()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
            
            time.sleep(60)  # Monitor every minute
    
    def _check_alerts(self, health: SystemHealth):
        """Check if any alerts should be triggered"""
        alerts = []
        
        # CPU usage alert
        if health.cpu_usage > 80:
            alerts.append({
                "type": "high_cpu",
                "message": f"High CPU usage: {health.cpu_usage:.1f}%",
                "severity": "critical" if health.cpu_usage > 90 else "high"
            })
        
        # Memory usage alert
        if health.memory_usage > 85:
            alerts.append({
                "type": "high_memory",
                "message": f"High memory usage: {health.memory_usage:.1f}%",
                "severity": "critical" if health.memory_usage > 95 else "high"
            })
        
        # Response time alert
        if health.response_time_avg > 2000:  # 2 seconds
            alerts.append({
                "type": "slow_response",
                "message": f"Slow response time: {health.response_time_avg:.0f}ms",
                "severity": "medium"
            })
        
        # Error rate alert
        if health.error_rate > 5:  # 5% error rate
            alerts.append({
                "type": "high_error_rate",
                "message": f"High error rate: {health.error_rate:.1f}%",
                "severity": "high"
            })
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Performance Alert: {alert['message']}")
    
    def _clean_old_metrics(self):
        """Clean metrics older than 24 hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        with self._lock:
            self.metrics_buffer = [m for m in self.metrics_buffer if m.timestamp >= cutoff_time]


class CacheManager:
    """Advanced caching manager for performance optimization"""
    
    def __init__(self):
        self.cache_store = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key in self.cache_store:
                entry = self.cache_store[key]
                
                # Check if expired
                if entry['expires_at'] and datetime.utcnow() > entry['expires_at']:
                    del self.cache_store[key]
                    self.cache_stats["misses"] += 1
                    return None
                
                self.cache_stats["hits"] += 1
                entry['access_count'] += 1
                entry['last_accessed'] = datetime.utcnow()
                return entry['value']
            else:
                self.cache_stats["misses"] += 1
                return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in cache with TTL"""
        with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
            
            self.cache_store[key] = {
                'value': value,
                'created_at': datetime.utcnow(),
                'last_accessed': datetime.utcnow(),
                'expires_at': expires_at,
                'access_count': 0,
                'ttl_seconds': ttl_seconds
            }
            
            self.cache_stats["sets"] += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self.cache_store:
                del self.cache_store[key]
                self.cache_stats["deletes"] += 1
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self.cache_store.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
            hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.cache_stats,
                "total_requests": total_requests,
                "hit_rate": hit_rate,
                "cache_size": len(self.cache_store),
                "memory_usage": self._estimate_memory_usage()
            }
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.utcnow()
        with self._lock:
            expired_keys = []
            for key, entry in self.cache_store.items():
                if entry['expires_at'] and now > entry['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache_store[key]
            
            return len(expired_keys)
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage of cache in bytes"""
        import sys
        total_size = 0
        for key, entry in self.cache_store.items():
            total_size += sys.getsizeof(key)
            total_size += sys.getsizeof(entry['value'])
            total_size += sys.getsizeof(entry)
        return total_size


class DatabaseOptimizer:
    """Database query optimization and monitoring"""
    
    def __init__(self, db: Session):
        self.db = db
        self.slow_query_threshold = 1.0  # 1 second
        self.slow_queries = []
    
    def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze database query performance"""
        try:
            # Get slow queries
            slow_queries_sql = """
                SELECT query, mean_exec_time, calls, rows, total_exec_time
                FROM pg_stat_statements 
                WHERE mean_exec_time > :threshold
                ORDER BY mean_exec_time DESC
                LIMIT 10
            """
            
            slow_queries = self.db.execute(
                text(slow_queries_sql), 
                {"threshold": self.slow_query_threshold * 1000}
            ).fetchall()
            
            # Get database statistics
            db_stats_sql = """
                SELECT 
                    numbackends,
                    xact_commit,
                    xact_rollback,
                    blks_read,
                    blks_hit,
                    tup_returned,
                    tup_fetched,
                    tup_inserted,
                    tup_updated,
                    tup_deleted
                FROM pg_stat_database 
                WHERE datname = current_database()
            """
            
            db_stats = self.db.execute(text(db_stats_sql)).fetchone()
            
            # Calculate cache hit ratio
            cache_hit_ratio = 0
            if db_stats and (db_stats.blks_read + db_stats.blks_hit) > 0:
                cache_hit_ratio = (db_stats.blks_hit / (db_stats.blks_read + db_stats.blks_hit)) * 100
            
            return {
                "slow_queries": [dict(q) for q in slow_queries],
                "cache_hit_ratio": cache_hit_ratio,
                "active_connections": db_stats.numbackends if db_stats else 0,
                "transaction_stats": {
                    "commits": db_stats.xact_commit if db_stats else 0,
                    "rollbacks": db_stats.xact_rollback if db_stats else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing query performance: {str(e)}")
            return {"error": str(e)}
    
    def optimize_table_indexes(self, table_name: str) -> List[str]:
        """Suggest index optimizations for a table"""
        try:
            # Get table statistics
            table_stats_sql = """
                SELECT 
                    schemaname, tablename, attname, n_distinct, correlation
                FROM pg_stats 
                WHERE tablename = :table_name
                ORDER BY n_distinct DESC
            """
            
            table_stats = self.db.execute(
                text(table_stats_sql), 
                {"table_name": table_name}
            ).fetchall()
            
            suggestions = []
            
            for stat in table_stats:
                # Suggest index for columns with high cardinality
                if stat.n_distinct > 100:
                    suggestions.append(f"CREATE INDEX idx_{table_name}_{stat.attname} ON {table_name} ({stat.attname});")
                
                # Suggest index for columns with good correlation
                if abs(stat.correlation) > 0.8:
                    suggestions.append(f"CREATE INDEX idx_{table_name}_{stat.attname}_ordered ON {table_name} ({stat.attname});")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error optimizing table indexes: {str(e)}")
            return []


class PerformanceOptimizer:
    """Main performance optimization service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.monitor = PerformanceMonitor(db)
        self.cache = CacheManager()
        self.db_optimizer = DatabaseOptimizer(db)
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Start cache cleanup timer
        threading.Timer(3600, self._periodic_cache_cleanup).start()  # Every hour
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data"""
        system_health = self.monitor.get_system_health()
        cache_stats = self.cache.get_stats()
        db_performance = self.db_optimizer.analyze_query_performance()
        metrics_summary = self.monitor.get_metrics_summary()
        
        return {
            "timestamp": datetime.utcnow(),
            "system_health": {
                "cpu_usage": system_health.cpu_usage,
                "memory_usage": system_health.memory_usage,
                "disk_usage": system_health.disk_usage,
                "database_connections": system_health.database_connections,
                "response_time_avg": system_health.response_time_avg,
                "error_rate": system_health.error_rate
            },
            "cache_performance": cache_stats,
            "database_performance": db_performance,
            "metrics_summary": metrics_summary,
            "recommendations": self._generate_performance_recommendations(system_health, cache_stats, db_performance)
        }
    
    def _generate_performance_recommendations(
        self, 
        system_health: SystemHealth, 
        cache_stats: Dict[str, Any], 
        db_performance: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # CPU recommendations
        if system_health.cpu_usage > 80:
            recommendations.append({
                "type": "cpu",
                "priority": "high",
                "message": "High CPU usage detected. Consider scaling horizontally or optimizing CPU-intensive operations."
            })
        
        # Memory recommendations
        if system_health.memory_usage > 85:
            recommendations.append({
                "type": "memory",
                "priority": "high",
                "message": "High memory usage detected. Consider increasing memory or implementing memory optimization."
            })
        
        # Cache recommendations
        if cache_stats.get("hit_rate", 0) < 70:
            recommendations.append({
                "type": "cache",
                "priority": "medium",
                "message": "Low cache hit rate. Consider adjusting cache TTL or caching strategy."
            })
        
        # Database recommendations
        if db_performance.get("cache_hit_ratio", 100) < 90:
            recommendations.append({
                "type": "database",
                "priority": "medium",
                "message": "Low database cache hit ratio. Consider increasing shared_buffers or adding indexes."
            })
        
        # Response time recommendations
        if system_health.response_time_avg > 1000:
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "message": "Slow response times detected. Consider optimizing queries or implementing caching."
            })
        
        return recommendations
    
    def _periodic_cache_cleanup(self):
        """Periodic cache cleanup"""
        try:
            cleaned = self.cache.cleanup_expired()
            if cleaned > 0:
                logger.info(f"Cleaned {cleaned} expired cache entries")
        except Exception as e:
            logger.error(f"Error during cache cleanup: {str(e)}")
        
        # Schedule next cleanup
        threading.Timer(3600, self._periodic_cache_cleanup).start()


def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000  # milliseconds
            
            # Record performance metric
            # Note: In practice, you'd get the monitor instance from a global registry
            logger.debug(f"Function {func.__name__} executed in {execution_time:.2f}ms")
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Function {func.__name__} failed after {execution_time:.2f}ms: {str(e)}")
            raise
    
    return wrapper


def cache_result(key_prefix: str, ttl_seconds: int = 3600):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            # Note: In practice, you'd get the cache instance from a global registry
            # cached_result = cache_manager.get(cache_key)
            # if cached_result is not None:
            #     return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            # cache_manager.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator