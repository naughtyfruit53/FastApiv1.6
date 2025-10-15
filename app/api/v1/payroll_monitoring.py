# app/api/v1/payroll_monitoring.py
# Phase 2: Payroll Monitoring and Observability System

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date, timedelta
import time

from app.db.session import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.models.user_models import User
from app.models.payroll_models import PayrollComponent, PayrollRun, PayrollLine
from app.models.erp_models import ChartOfAccounts
from app.schemas.payroll_schemas import (
    PayrollMonitoringMetrics,
    PayrollHealthCheck
)

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/payroll/monitoring/health", response_model=PayrollHealthCheck)
async def get_payroll_health_check(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get comprehensive payroll system health check"""
    try:
        start_time = time.time()
        query_count = 0
        
        # Get last successful payroll run
        last_successful_run = db.query(PayrollRun.gl_posted_at).filter(
            PayrollRun.organization_id == organization_id,
            PayrollRun.gl_posted == True
        ).order_by(desc(PayrollRun.gl_posted_at)).first()
        query_count += 1
        
        # Count unmapped components
        unmapped_components = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True,
            PayrollComponent.expense_account_id.is_(None),
            PayrollComponent.payable_account_id.is_(None)
        ).scalar()
        query_count += 1
        
        # Count inactive accounts being used
        inactive_accounts = db.query(func.count(ChartOfAccounts.id.distinct())).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.is_active == False,
            or_(
                ChartOfAccounts.id.in_(
                    db.query(PayrollComponent.expense_account_id).filter(
                        PayrollComponent.organization_id == organization_id,
                        PayrollComponent.expense_account_id.isnot(None)
                    )
                ),
                ChartOfAccounts.id.in_(
                    db.query(PayrollComponent.payable_account_id).filter(
                        PayrollComponent.organization_id == organization_id,
                        PayrollComponent.payable_account_id.isnot(None)
                    )
                )
            )
        ).scalar()
        query_count += 1
        
        # Count validation issues
        validation_issues = 0
        components = db.query(PayrollComponent).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True
        ).all()
        query_count += 1
        
        for component in components:
            # Check for missing required mappings
            if component.component_type in ['earning', 'deduction'] and not component.expense_account_id:
                validation_issues += 1
            if component.component_type in ['deduction', 'employer_contribution'] and not component.payable_account_id:
                validation_issues += 1
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Get memory usage
        memory_usage = 0  # psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Determine overall health status
        status_level = "healthy"
        if unmapped_components > 0 or inactive_accounts > 0:
            status_level = "warning"
        if validation_issues > 5 or unmapped_components > 10:
            status_level = "error"
        
        # Create performance metrics
        performance_metrics = PayrollMonitoringMetrics(
            processing_time=processing_time,
            memory_usage=memory_usage,
            database_queries=query_count,
            validation_errors=validation_issues,
            warnings=unmapped_components + inactive_accounts
        )
        
        return PayrollHealthCheck(
            status=status_level,
            last_successful_run=last_successful_run[0] if last_successful_run else None,
            unmapped_components=unmapped_components,
            inactive_accounts=inactive_accounts,
            validation_issues=validation_issues,
            performance_metrics=performance_metrics
        )
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing health check"
        )


@router.get("/payroll/monitoring/metrics")
async def get_payroll_metrics(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get detailed payroll metrics and analytics"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Payroll run metrics
        runs_query = db.query(PayrollRun).filter(
            PayrollRun.organization_id == organization_id,
            PayrollRun.created_at >= start_date
        )
        
        total_runs = runs_query.count()
        successful_runs = runs_query.filter(PayrollRun.gl_posted == True).count()
        failed_runs = total_runs - successful_runs
        
        # Processing time analysis
        avg_processing_time = db.query(
            func.avg(
                func.extract('epoch', PayrollRun.gl_posted_at - PayrollRun.created_at)
            )
        ).filter(
            PayrollRun.organization_id == organization_id,
            PayrollRun.gl_posted == True,
            PayrollRun.created_at >= start_date
        ).scalar()
        
        # Amount trends
        amount_trends = db.query(
            func.date(PayrollRun.created_at).label('date'),
            func.sum(PayrollRun.total_gross_amount).label('total_gross'),
            func.sum(PayrollRun.total_deductions).label('total_deductions'),
            func.sum(PayrollRun.total_net_amount).label('total_net'),
            func.count(PayrollRun.id).label('run_count')
        ).filter(
            PayrollRun.organization_id == organization_id,
            PayrollRun.created_at >= start_date
        ).group_by(
            func.date(PayrollRun.created_at)
        ).order_by(
            func.date(PayrollRun.created_at)
        ).all()
        
        # Component usage statistics
        component_usage = db.query(
            PayrollComponent.component_name,
            PayrollComponent.component_type,
            func.count(PayrollLine.id).label('usage_count'),
            func.sum(PayrollLine.amount).label('total_amount')
        ).join(
            PayrollLine, PayrollComponent.id == PayrollLine.component_id
        ).join(
            PayrollRun, PayrollLine.payroll_run_id == PayrollRun.id
        ).filter(
            PayrollRun.organization_id == organization_id,
            PayrollRun.created_at >= start_date
        ).group_by(
            PayrollComponent.id,
            PayrollComponent.component_name,
            PayrollComponent.component_type
        ).order_by(
            desc(func.count(PayrollLine.id))
        ).limit(10).all()
        
        # Error patterns
        error_patterns = []
        # This would be enhanced with actual error logging
        
        # Account mapping coverage
        total_components = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True
        ).scalar()
        
        mapped_components = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True,
            or_(
                PayrollComponent.expense_account_id.isnot(None),
                PayrollComponent.payable_account_id.isnot(None)
            )
        ).scalar()
        
        mapping_coverage = (mapped_components / total_components * 100) if total_components > 0 else 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "days": days
            },
            "payroll_runs": {
                "total": total_runs,
                "successful": successful_runs,
                "failed": failed_runs,
                "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                "avg_processing_time_seconds": float(avg_processing_time) if avg_processing_time else 0
            },
            "amount_trends": [
                {
                    "date": trend.date.isoformat(),
                    "total_gross": float(trend.total_gross) if trend.total_gross else 0,
                    "total_deductions": float(trend.total_deductions) if trend.total_deductions else 0,
                    "total_net": float(trend.total_net) if trend.total_net else 0,
                    "run_count": trend.run_count
                }
                for trend in amount_trends
            ],
            "component_usage": [
                {
                    "component_name": usage.component_name,
                    "component_type": usage.component_type,
                    "usage_count": usage.usage_count,
                    "total_amount": float(usage.total_amount) if usage.total_amount else 0
                }
                for usage in component_usage
            ],
            "mapping_coverage": {
                "total_components": total_components,
                "mapped_components": mapped_components,
                "coverage_percentage": round(mapping_coverage, 2)
            },
            "error_patterns": error_patterns
        }
        
    except Exception as e:
        logger.error(f"Error getting payroll metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payroll metrics"
        )


@router.get("/payroll/monitoring/performance")
async def get_performance_analysis(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get performance analysis and bottleneck identification"""
    try:
        start_time = time.time()
        
        # Database performance metrics
        db_stats = db.execute(text("""
            SELECT 
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                idx_tup_fetch,
                n_tup_ins,
                n_tup_upd,
                n_tup_del
            FROM pg_stat_user_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('payroll_components', 'payroll_runs', 'payroll_lines', 'chart_of_accounts')
        """)).fetchall()
        
        # Query performance for common operations
        query_times = {}
        
        # Test component fetch time
        start = time.time()
        db.query(PayrollComponent).filter(
            PayrollComponent.organization_id == organization_id
        ).limit(100).all()
        query_times['component_fetch'] = time.time() - start
        
        # Test GL preview generation time
        start = time.time()
        db.query(PayrollLine).filter(
            PayrollLine.organization_id == organization_id
        ).limit(100).all()
        query_times['gl_preview'] = time.time() - start
        
        # Test chart account lookup time
        start = time.time()
        db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.is_active == True
        ).limit(50).all()
        query_times['account_lookup'] = time.time() - start
        
        # System resource usage
        memory_usage = 0  # memory_info = psutil.virtual_memory()
        cpu_percent = 0  # psutil.cpu_percent(interval=1)
        
        # Database connection pool status
        connection_pool_info = {
            "size": db.bind.pool.size(),
            "checked_in": db.bind.pool.checkedin(),
            "checked_out": db.bind.pool.checkedout(),
            "overflow": db.bind.pool.overflow(),
            "invalid": db.bind.pool.invalid()
        }
        
        # Recommendations based on performance
        recommendations = []
        
        if query_times['component_fetch'] > 0.5:
            recommendations.append("Consider adding indexes on payroll_components table")
        
        if query_times['gl_preview'] > 1.0:
            recommendations.append("GL preview generation is slow - consider optimizing payroll_lines queries")
        
        if cpu_percent > 80:
            recommendations.append("High CPU usage detected - consider load balancing")
        
        if memory_usage > 85:  # memory_info.percent > 85:
            recommendations.append("High memory usage - consider memory optimization")
        
        total_time = time.time() - start_time
        
        return {
            "performance_analysis": {
                "total_analysis_time": total_time,
                "query_performance": query_times,
                "system_resources": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_usage,  # memory_info.percent,
                    "memory_available_gb": 0,  # memory_info.available / (1024**3),
                    "memory_used_gb": 0  # memory_info.used / (1024**3)
                },
                "database_performance": [
                    {
                        "table": stat.tablename,
                        "sequential_scans": stat.seq_scan,
                        "sequential_reads": stat.seq_tup_read,
                        "index_scans": stat.idx_scan,
                        "index_reads": stat.idx_tup_fetch,
                        "inserts": stat.n_tup_ins,
                        "updates": stat.n_tup_upd,
                        "deletes": stat.n_tup_del
                    }
                    for stat in db_stats
                ],
                "connection_pool": connection_pool_info,
                "recommendations": recommendations
            }
        }
        
    except Exception as e:
        logger.error(f"Error in performance analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing performance analysis"
        )


@router.get("/payroll/monitoring/alerts")
async def get_payroll_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: low, medium, high, critical"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get current payroll system alerts and warnings"""
    try:
        alerts = []
        
        # Check for unmapped components
        unmapped_count = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True,
            PayrollComponent.expense_account_id.is_(None),
            PayrollComponent.payable_account_id.is_(None)
        ).scalar()
        
        if unmapped_count > 0:
            severity_level = "high" if unmapped_count > 5 else "medium"
            alerts.append({
                "id": "unmapped_components",
                "severity": severity_level,
                "title": f"{unmapped_count} unmapped payroll components",
                "description": f"There are {unmapped_count} active payroll components without chart account mappings",
                "action": "Map components to appropriate chart accounts",
                "created_at": datetime.utcnow().isoformat()
            })
        
        # Check for inactive accounts in use
        inactive_accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.is_active == False,
            or_(
                ChartOfAccounts.id.in_(
                    db.query(PayrollComponent.expense_account_id).filter(
                        PayrollComponent.organization_id == organization_id,
                        PayrollComponent.expense_account_id.isnot(None)
                    )
                ),
                ChartOfAccounts.id.in_(
                    db.query(PayrollComponent.payable_account_id).filter(
                        PayrollComponent.organization_id == organization_id,
                        PayrollComponent.payable_account_id.isnot(None)
                    )
                )
            )
        ).count()
        
        if inactive_accounts > 0:
            alerts.append({
                "id": "inactive_accounts",
                "severity": "high",
                "title": f"{inactive_accounts} inactive accounts in use",
                "description": f"There are {inactive_accounts} inactive chart accounts being used by payroll components",
                "action": "Activate accounts or remap components to active accounts",
                "created_at": datetime.utcnow().isoformat()
            })
        
        # Check for failed payroll runs
        failed_runs = db.query(func.count(PayrollRun.id)).filter(
            PayrollRun.organization_id == organization_id,
            PayrollRun.status == "failed",
            PayrollRun.created_at >= datetime.utcnow() - timedelta(days=7)
        ).scalar()
        
        if failed_runs > 0:
            alerts.append({
                "id": "failed_runs",
                "severity": "critical",
                "title": f"{failed_runs} failed payroll runs",
                "description": f"There are {failed_runs} failed payroll runs in the last 7 days",
                "action": "Review and fix failed payroll runs",
                "created_at": datetime.utcnow().isoformat()
            })
        
        # Check for old unprocessed runs
        old_runs = db.query(func.count(PayrollRun.id)).filter(
            PayrollRun.organization_id == organization_id,
            PayrollRun.status == "draft",
            PayrollRun.created_at <= datetime.utcnow() - timedelta(days=30)
        ).scalar()
        
        if old_runs > 0:
            alerts.append({
                "id": "old_draft_runs",
                "severity": "low",
                "title": f"{old_runs} old draft payroll runs",
                "description": f"There are {old_runs} payroll runs in draft status for over 30 days",
                "action": "Process or clean up old draft runs",
                "created_at": datetime.utcnow().isoformat()
            })
        
        # Filter by severity if specified
        if severity:
            alerts = [alert for alert in alerts if alert["severity"] == severity]
        
        # Sort by severity (critical > high > medium > low)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 4))
        
        return {
            "total_alerts": len(alerts),
            "alerts_by_severity": {
                "critical": len([a for a in alerts if a["severity"] == "critical"]),
                "high": len([a for a in alerts if a["severity"] == "high"]),
                "medium": len([a for a in alerts if a["severity"] == "medium"]),
                "low": len([a for a in alerts if a["severity"] == "low"])
            },
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Error getting payroll alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payroll alerts"
        )


@router.post("/payroll/monitoring/benchmark")
async def run_performance_benchmark(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Run comprehensive performance benchmark"""
    try:
        benchmark_results = {}
        
        # Component operations benchmark
        start_time = time.time()
        components = db.query(PayrollComponent).filter(
            PayrollComponent.organization_id == organization_id
        ).limit(100).all()
        benchmark_results['component_fetch_100'] = time.time() - start_time
        
        # Chart account lookup benchmark
        start_time = time.time()
        accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.is_active == True
        ).limit(50).all()
        benchmark_results['account_lookup_50'] = time.time() - start_time
        
        # Complex join benchmark
        start_time = time.time()
        complex_query = db.query(PayrollLine).join(
            PayrollComponent, PayrollLine.component_id == PayrollComponent.id
        ).join(
            ChartOfAccounts, PayrollLine.chart_account_id == ChartOfAccounts.id
        ).filter(
            PayrollLine.organization_id == organization_id
        ).limit(50).all()
        benchmark_results['complex_join_50'] = time.time() - start_time
        
        # Aggregation benchmark
        start_time = time.time()
        aggregation = db.query(
            func.sum(PayrollLine.amount),
            func.count(PayrollLine.id)
        ).filter(
            PayrollLine.organization_id == organization_id
        ).first()
        benchmark_results['aggregation'] = time.time() - start_time
        
        # Memory usage during benchmark
        memory_usage = 0  # memory_info = psutil.Process().memory_info()
        
        # Generate performance score (lower is better)
        total_time = sum(benchmark_results.values())
        if total_time < 0.1:
            performance_grade = "A+"
        elif total_time < 0.5:
            performance_grade = "A"
        elif total_time < 1.0:
            performance_grade = "B"
        elif total_time < 2.0:
            performance_grade = "C"
        else:
            performance_grade = "D"
        
        return {
            "benchmark_results": benchmark_results,
            "total_time": total_time,
            "performance_grade": performance_grade,
            "memory_usage_mb": memory_usage,  # memory_info.rss / 1024 / 1024,
            "recommendations": [
                "Consider adding database indexes if performance grade is below B",
                "Monitor memory usage during peak hours",
                "Run this benchmark regularly to track performance trends"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error running benchmark: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error running performance benchmark"
        )