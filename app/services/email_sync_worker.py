# app/services/email_sync_worker.py

"""
Background Email Sync Worker using APScheduler
Handles scheduled email synchronization tasks

Note: For production scale, consider migrating to Celery for distributed task processing
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from sqlalchemy.orm import Session
from sqlalchemy import delete

from app.core.config import settings
from app.core.database import SessionLocal, sync_engine
from app.models.email import MailAccount, EmailSyncStatus, EmailSyncLog
from app.services.email_sync_service import email_sync_service

logger = logging.getLogger(__name__)


class EmailSyncWorker:
    """
    Email synchronization worker with APScheduler
    
    Configuration via environment variables:
    - EMAIL_SYNC_ENABLED: Enable/disable email sync worker (default: True)
    - EMAIL_SYNC_INTERVAL_MINUTES: Sync interval in minutes (default: 15)
    - EMAIL_SYNC_MAX_WORKERS: Max concurrent sync workers (default: 3)
    - EMAIL_SYNC_BATCH_SIZE: Accounts to sync per batch (default: 5)
    """
    
    def __init__(self):
        self.scheduler = None
        self.is_running = False
        
        # Configuration
        self.sync_enabled = getattr(settings, 'EMAIL_SYNC_ENABLED', True)
        self.sync_interval_minutes = getattr(settings, 'EMAIL_SYNC_INTERVAL_MINUTES', 15)
        self.max_workers = getattr(settings, 'EMAIL_SYNC_MAX_WORKERS', 3)
        self.batch_size = getattr(settings, 'EMAIL_SYNC_BATCH_SIZE', 5)
        
        # Job store configuration
        self.jobstore_url = getattr(settings, 'DATABASE_URL', 'sqlite:///./email_sync_jobs.db').replace("postgresql+asyncpg", "postgresql+psycopg2").replace("postgres+asyncpg", "postgres+psycopg2")
        
        # Initialize scheduler if enabled
        if self.sync_enabled:
            self._initialize_scheduler()
        else:
            logger.info("Email sync worker is disabled")
    
    def _initialize_scheduler(self):
        """
        Initialize APScheduler with appropriate configuration
        """
        try:
            # Configure job stores
            jobstores = {
                'default': SQLAlchemyJobStore(url=self.jobstore_url, tablename='email_sync_jobs')
            }
            
            # Configure executors
            executors = {
                'default': ThreadPoolExecutor(max_workers=self.max_workers)
            }
            
            # Job defaults
            job_defaults = {
                'coalesce': True,  # Combine multiple pending instances into one
                'max_instances': 1,  # Only one instance per job
                'misfire_grace_time': 300  # 5 minutes grace time
            }
            
            # Create scheduler
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
            
            # Add event listeners
            self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
            self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
            
            logger.info("Email sync scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
            self.scheduler = None
    
    def start(self):
        """
        Start the email sync worker
        """
        if not self.sync_enabled:
            logger.info("Email sync worker is disabled")
            return False
        
        if not self.scheduler:
            logger.error("Scheduler not initialized")
            return False
        
        try:
            # Add periodic sync job
            self.scheduler.add_job(
                func=self.run_sync_batch,
                trigger=IntervalTrigger(minutes=self.sync_interval_minutes),
                id='email_sync_batch',
                name='Email Sync Batch Job',
                replace_existing=True
            )
            
            # Add daily cleanup job
            self.scheduler.add_job(
                func=self.cleanup_old_sync_logs,
                trigger=CronTrigger(hour=2, minute=0),  # Run at 2 AM daily
                id='email_sync_cleanup',
                name='Email Sync Log Cleanup',
                replace_existing=True
            )
            
            # Add account health check job
            self.scheduler.add_job(
                func=self.check_account_health,
                trigger=CronTrigger(hour=6, minute=0),  # Run at 6 AM daily
                id='email_account_health_check',
                name='Email Account Health Check',
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"Email sync worker started with {self.sync_interval_minutes}min interval")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start email sync worker: {str(e)}")
            return False
    
    def stop(self):
        """
        Stop the email sync worker
        """
        if self.scheduler and self.is_running:
            try:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                logger.info("Email sync worker stopped")
                return True
            except Exception as e:
                logger.error(f"Error stopping email sync worker: {str(e)}")
                return False
        return True
    
    def run_sync_batch(self):
        """
        Run synchronization for a batch of accounts
        This is the main sync job that runs periodically
        """
        logger.info("Starting email sync batch")
        
        db = SessionLocal()
        try:
            # Get accounts that need syncing
            accounts = self._get_accounts_for_sync(db)
            
            if not accounts:
                logger.info("No accounts need syncing")
                return
            
            logger.info(f"Syncing {len(accounts)} accounts")
            
            # Process accounts in batches
            for i in range(0, len(accounts), self.batch_size):
                batch = accounts[i:i + self.batch_size]
                
                for account in batch:
                    try:
                        self._sync_single_account(account.id)
                    except Exception as e:
                        logger.error(f"Error syncing account {account.id}: {str(e)}")
                        # Update account error status
                        account.last_sync_error = str(e)
                        account.sync_status = EmailSyncStatus.ERROR
                        db.commit()
            
            logger.info("Email sync batch completed")
            
        except Exception as e:
            logger.error(f"Error in sync batch: {str(e)}")
        finally:
            db.close()
    
    def _get_accounts_for_sync(self, db: Session) -> list:
        """
        Get accounts that need synchronization based on their sync frequency
        """
        try:
            now = datetime.utcnow()
            
            # Get active accounts that are due for sync
            accounts = db.query(MailAccount).filter(
                MailAccount.sync_enabled == True,
                MailAccount.sync_status.in_([EmailSyncStatus.ACTIVE, EmailSyncStatus.ERROR])
            ).all()
            
            accounts_to_sync = []
            
            for account in accounts:
                # Check if account is due for sync
                if account.last_sync_at is None:
                    # Never synced before
                    accounts_to_sync.append(account)
                else:
                    # Check if enough time has passed since last sync
                    next_sync_time = account.last_sync_at + timedelta(minutes=account.sync_frequency_minutes)
                    if now >= next_sync_time:
                        accounts_to_sync.append(account)
            
            return accounts_to_sync
            
        except Exception as e:
            logger.error(f"Error getting accounts for sync: {str(e)}")
            return []
    
    def _sync_single_account(self, account_id: int):
        """
        Sync a single account with error handling
        """
        try:
            logger.info(f"Starting sync for account {account_id}")
            
            # Use the email management service for sync
            success = email_sync_service.sync_account(account_id)
            
            if success:
                logger.info(f"Successfully synced account {account_id}")
            else:
                logger.warning(f"Sync completed with issues for account {account_id}")
            
        except Exception as e:
            logger.error(f"Failed to sync account {account_id}: {str(e)}")
            raise
    
    def cleanup_old_sync_logs(self):
        """
        Clean up old sync logs to prevent database bloat
        """
        logger.info("Starting sync log cleanup")
        
        db = SessionLocal()
        try:
            # Delete sync logs older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            stmt = delete(EmailSyncLog).where(
                EmailSyncLog.started_at < cutoff_date
            )
            result = db.execute(stmt)
            deleted_count = result.rowcount
            
            db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old sync log entries")
            
        except Exception as e:
            logger.error(f"Error cleaning up sync logs: {str(e)}")
        finally:
            db.close()
    
    def check_account_health(self):
        """
        Check health of email accounts and disable problematic ones
        """
        logger.info("Starting account health check")
        
        db = SessionLocal()
        try:
            # Get accounts with recent sync errors
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            accounts = db.query(MailAccount).filter(
                MailAccount.sync_enabled == True,
                MailAccount.last_sync_at >= cutoff_date,
                MailAccount.last_sync_error.isnot(None)
            ).all()
            
            for account in accounts:
                # Check recent sync success rate
                recent_logs = db.query(EmailSyncLog).filter(
                    EmailSyncLog.account_id == account.id,
                    EmailSyncLog.started_at >= cutoff_date
                ).all()
                
                if len(recent_logs) >= 5:  # Need at least 5 attempts
                    error_count = sum(1 for log in recent_logs if log.status == 'error')
                    error_rate = error_count / len(recent_logs)
                    
                    if error_rate >= 0.8:  # 80% error rate
                        logger.warning(f"Account {account.id} has high error rate ({error_rate:.1%}), pausing sync")
                        account.sync_status = EmailSyncStatus.PAUSED
                        db.commit()
            
            logger.info("Account health check completed")
            
        except Exception as e:
            logger.error(f"Error in account health check: {str(e)}")
        finally:
            db.close()
    
    def sync_account_now(self, account_id: int) -> bool:
        """
        Trigger immediate sync for a specific account
        """
        try:
            if self.scheduler and self.is_running:
                # Add one-time job
                job = self.scheduler.add_job(
                    func=self._sync_single_account,
                    args=[account_id],
                    id=f'manual_sync_{account_id}_{datetime.now().timestamp()}',
                    name=f'Manual Sync Account {account_id}',
                    replace_existing=False
                )
                
                logger.info(f"Scheduled immediate sync for account {account_id}")
                return True
            else:
                # Run directly if scheduler not available
                self._sync_single_account(account_id)
                return True
                
        except Exception as e:
            logger.error(f"Error scheduling manual sync for account {account_id}: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the sync worker
        """
        status = {
            'enabled': self.sync_enabled,
            'running': self.is_running,
            'sync_interval_minutes': self.sync_interval_minutes,
            'max_workers': self.max_workers,
            'batch_size': self.batch_size
        }
        
        if self.scheduler:
            jobs = self.scheduler.get_jobs()
            status['scheduled_jobs'] = [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time
                }
                for job in jobs
            ]
        
        return status
    
    def _job_executed(self, event):
        """
        Event listener for successful job execution
        """
        logger.debug(f"Job {event.job_id} executed successfully")
    
    def _job_error(self, event):
        """
        Event listener for job errors
        """
        logger.error(f"Job {event.job_id} failed: {event.exception}")


# Global instance
email_sync_worker = EmailSyncWorker()

# Functions for easy integration
def start_email_sync_worker():
    """Start the email sync background worker"""
    return email_sync_worker.start()

def stop_email_sync_worker():
    """Stop the email sync background worker"""
    return email_sync_worker.stop()

def get_sync_worker_status():
    """Get sync worker status"""
    return email_sync_worker.get_status()

def trigger_manual_sync(account_id: int):
    """Trigger manual sync for specific account"""
    return email_sync_worker.sync_account_now(account_id)