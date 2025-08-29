# app/services/migration_service.py
"""
Migration & Data Import Services - Core business logic for migration operations
"""

import io
import json
import logging
import asyncio
from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from fastapi import UploadFile, HTTPException
import pandas as pd

from app.models.migration_models import (
    MigrationJob, MigrationDataMapping, MigrationLog, MigrationTemplate,
    MigrationConflict, MigrationSourceType, MigrationDataType, 
    MigrationJobStatus, MigrationLogLevel
)
from app.models import Organization, User
from app.schemas.migration import (
    MigrationJobCreate, MigrationJobUpdate, FileUploadResponse,
    DataValidationResponse, FieldMappingPreview, MigrationPreview,
    MigrationProgressResponse, MigrationSummaryResponse
)
from app.services.excel_service import ExcelService
from app.services.tally_service import TallyIntegrationService

logger = logging.getLogger(__name__)


class MigrationService:
    """Core migration service"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def create_migration_job(
        self, 
        job_data: MigrationJobCreate, 
        organization_id: int, 
        user_id: int
    ) -> MigrationJob:
        """Create a new migration job"""
        try:
            # Create migration job
            migration_job = MigrationJob(
                organization_id=organization_id,
                created_by=user_id,
                job_name=job_data.job_name,
                description=job_data.description,
                source_type=MigrationSourceType(job_data.source_type),
                data_types=[dt.value for dt in job_data.data_types],
                conflict_resolution_strategy=job_data.conflict_resolution_strategy,
                import_config=job_data.import_config or {},
                status=MigrationJobStatus.DRAFT
            )
            
            self.db.add(migration_job)
            self.db.commit()
            self.db.refresh(migration_job)
            
            # Create initial log entry
            await self._log_migration_event(
                migration_job.id,
                organization_id,
                MigrationLogLevel.INFO,
                f"Migration job '{job_data.job_name}' created",
                operation="create_job"
            )
            
            logger.info(f"Created migration job {migration_job.id} for org {organization_id}")
            return migration_job
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create migration job: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create migration job: {str(e)}")
    
    async def upload_source_file(
        self, 
        migration_job_id: int, 
        organization_id: int, 
        file: UploadFile
    ) -> FileUploadResponse:
        """Upload and analyze source file"""
        try:
            # Get migration job
            migration_job = self.db.query(MigrationJob).filter(
                and_(
                    MigrationJob.id == migration_job_id,
                    MigrationJob.organization_id == organization_id
                )
            ).first()
            
            if not migration_job:
                raise HTTPException(status_code=404, detail="Migration job not found")
            
            # Validate file type based on source type
            source_type = migration_job.source_type
            detected_source_type = self._detect_source_type(file.filename)
            
            if source_type not in [detected_source_type, MigrationSourceType.MANUAL]:
                # Allow manual override, but warn
                await self._log_migration_event(
                    migration_job_id,
                    organization_id,
                    MigrationLogLevel.WARNING,
                    f"File type mismatch: expected {source_type.value}, got {detected_source_type.value}",
                    operation="file_upload"
                )
            
            # Process file based on type
            file_analysis = await self._analyze_source_file(file, detected_source_type)
            
            # Update migration job with file information
            migration_job.source_file_name = file.filename
            migration_job.source_file_size = file_analysis["file_size"]
            migration_job.source_metadata = file_analysis["metadata"]
            migration_job.total_records = file_analysis["total_records"]
            migration_job.status = MigrationJobStatus.MAPPING
            
            self.db.commit()
            
            # Log upload success
            await self._log_migration_event(
                migration_job_id,
                organization_id,
                MigrationLogLevel.INFO,
                f"File '{file.filename}' uploaded successfully ({file_analysis['total_records']} records)",
                operation="file_upload"
            )
            
            return FileUploadResponse(
                success=True,
                file_id=str(migration_job_id),
                file_name=file.filename,
                file_size=file_analysis["file_size"],
                detected_source_type=detected_source_type,
                detected_data_types=file_analysis["detected_data_types"],
                preview_data=file_analysis["preview_data"],
                total_records=file_analysis["total_records"],
                validation_errors=file_analysis.get("validation_errors", []),
                validation_warnings=file_analysis.get("validation_warnings", [])
            )
            
        except Exception as e:
            logger.error(f"Failed to upload source file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    async def create_field_mappings(
        self, 
        migration_job_id: int, 
        organization_id: int, 
        auto_map: bool = True
    ) -> FieldMappingPreview:
        """Create or suggest field mappings"""
        try:
            # Get migration job
            migration_job = self.db.query(MigrationJob).filter(
                and_(
                    MigrationJob.id == migration_job_id,
                    MigrationJob.organization_id == organization_id
                )
            ).first()
            
            if not migration_job:
                raise HTTPException(status_code=404, detail="Migration job not found")
            
            # Get source fields from metadata
            source_fields = migration_job.source_metadata.get("fields", [])
            
            # Get suggested mappings based on templates and AI
            suggested_mappings = []
            unmapped_fields = []
            required_fields_missing = []
            
            for data_type in migration_job.data_types:
                # Get template for this data type
                template = await self._get_migration_template(
                    migration_job.source_type, 
                    MigrationDataType(data_type)
                )
                
                if template:
                    # Apply template mappings
                    template_mappings = template.field_mappings
                    for source_field in source_fields:
                        if source_field in template_mappings:
                            mapping = MigrationDataMapping(
                                migration_job_id=migration_job_id,
                                organization_id=organization_id,
                                data_type=MigrationDataType(data_type),
                                source_field=source_field,
                                target_field=template_mappings[source_field]["target"],
                                field_type=template_mappings[source_field]["type"],
                                is_required=template_mappings[source_field].get("required", False),
                                transformation_rule=template_mappings[source_field].get("transform")
                            )
                            
                            if auto_map:
                                self.db.add(mapping)
                                suggested_mappings.append(mapping)
                        else:
                            unmapped_fields.append(source_field)
                
                # Check for required fields
                required_fields = self._get_required_fields(MigrationDataType(data_type))
                mapped_targets = [m.target_field for m in suggested_mappings]
                required_fields_missing.extend([
                    field for field in required_fields 
                    if field not in mapped_targets
                ])
            
            if auto_map:
                self.db.commit()
            
            return FieldMappingPreview(
                source_fields=source_fields,
                suggested_mappings=suggested_mappings,
                unmapped_fields=unmapped_fields,
                required_fields_missing=required_fields_missing
            )
            
        except Exception as e:
            logger.error(f"Failed to create field mappings: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create field mappings: {str(e)}")
    
    async def validate_migration_data(
        self, 
        migration_job_id: int, 
        organization_id: int
    ) -> DataValidationResponse:
        """Validate migration data"""
        try:
            # Get migration job with mappings
            migration_job = self.db.query(MigrationJob).filter(
                and_(
                    MigrationJob.id == migration_job_id,
                    MigrationJob.organization_id == organization_id
                )
            ).first()
            
            if not migration_job:
                raise HTTPException(status_code=404, detail="Migration job not found")
            
            # Get data mappings
            mappings = self.db.query(MigrationDataMapping).filter(
                MigrationDataMapping.migration_job_id == migration_job_id
            ).all()
            
            if not mappings:
                raise HTTPException(status_code=400, detail="No field mappings found")
            
            # Validate data based on mappings
            validation_errors = []
            validation_warnings = []
            field_analysis = {}
            
            # Process source data and apply validations
            source_data = await self._load_source_data(migration_job)
            
            for mapping in mappings:
                field_name = mapping.source_field
                if field_name in source_data.columns:
                    # Analyze field data
                    field_data = source_data[field_name]
                    analysis = {
                        "non_null_count": field_data.notna().sum(),
                        "null_count": field_data.isna().sum(),
                        "unique_count": field_data.nunique(),
                        "data_type": str(field_data.dtype)
                    }
                    
                    # Validate required fields
                    if mapping.is_required and analysis["null_count"] > 0:
                        validation_errors.append({
                            "field": field_name,
                            "error": f"Required field has {analysis['null_count']} null values",
                            "severity": "error"
                        })
                    
                    # Validate data types
                    if not self._validate_field_type(field_data, mapping.field_type):
                        validation_errors.append({
                            "field": field_name,
                            "error": f"Data type mismatch: expected {mapping.field_type}",
                            "severity": "error"
                        })
                    
                    field_analysis[field_name] = analysis
            
            # Generate preview data
            preview_data = source_data.head(10).to_dict("records")
            
            # Update migration job status
            is_valid = len(validation_errors) == 0
            migration_job.status = MigrationJobStatus.APPROVED if is_valid else MigrationJobStatus.VALIDATION
            self.db.commit()
            
            return DataValidationResponse(
                is_valid=is_valid,
                total_records=len(source_data),
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                field_analysis=field_analysis,
                preview_data=preview_data
            )
            
        except Exception as e:
            logger.error(f"Failed to validate migration data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to validate data: {str(e)}")
    
    async def start_migration_job(
        self, 
        migration_job_id: int, 
        organization_id: int,
        user_id: int
    ) -> MigrationProgressResponse:
        """Start migration job execution"""
        try:
            # Get migration job
            migration_job = self.db.query(MigrationJob).filter(
                and_(
                    MigrationJob.id == migration_job_id,
                    MigrationJob.organization_id == organization_id
                )
            ).first()
            
            if not migration_job:
                raise HTTPException(status_code=404, detail="Migration job not found")
            
            if migration_job.status != MigrationJobStatus.APPROVED:
                raise HTTPException(status_code=400, detail="Migration job not ready for execution")
            
            # Update job status
            migration_job.status = MigrationJobStatus.RUNNING
            migration_job.started_at = datetime.utcnow()
            migration_job.progress_percentage = 0.0
            self.db.commit()
            
            # Start background migration task
            asyncio.create_task(self._execute_migration(migration_job_id, organization_id, user_id))
            
            return MigrationProgressResponse(
                job_id=migration_job_id,
                status=MigrationJobStatus.RUNNING,
                progress_percentage=0.0,
                processed_records=0,
                total_records=migration_job.total_records,
                success_records=0,
                failed_records=0,
                current_operation="Starting migration...",
                recent_logs=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to start migration job: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to start migration: {str(e)}")
    
    async def get_migration_progress(
        self, 
        migration_job_id: int, 
        organization_id: int
    ) -> MigrationProgressResponse:
        """Get migration job progress"""
        try:
            # Get migration job
            migration_job = self.db.query(MigrationJob).filter(
                and_(
                    MigrationJob.id == migration_job_id,
                    MigrationJob.organization_id == organization_id
                )
            ).first()
            
            if not migration_job:
                raise HTTPException(status_code=404, detail="Migration job not found")
            
            # Get recent logs
            recent_logs = self.db.query(MigrationLog).filter(
                MigrationLog.migration_job_id == migration_job_id
            ).order_by(desc(MigrationLog.created_at)).limit(10).all()
            
            # Estimate completion time
            estimated_completion = None
            if migration_job.status == MigrationJobStatus.RUNNING and migration_job.progress_percentage > 0:
                elapsed = (datetime.utcnow() - migration_job.started_at).total_seconds()
                estimated_total = elapsed / (migration_job.progress_percentage / 100)
                estimated_completion = migration_job.started_at + timedelta(seconds=estimated_total)
            
            return MigrationProgressResponse(
                job_id=migration_job_id,
                status=migration_job.status,
                progress_percentage=migration_job.progress_percentage,
                processed_records=migration_job.processed_records,
                total_records=migration_job.total_records,
                success_records=migration_job.success_records,
                failed_records=migration_job.failed_records,
                estimated_completion_time=estimated_completion,
                recent_logs=recent_logs
            )
            
        except Exception as e:
            logger.error(f"Failed to get migration progress: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")
    
    # Helper methods
    def _detect_source_type(self, filename: str) -> MigrationSourceType:
        """Detect source type from filename"""
        if filename.endswith(('.xlsx', '.xls')):
            return MigrationSourceType.EXCEL
        elif filename.endswith('.csv'):
            return MigrationSourceType.CSV
        elif filename.endswith('.json'):
            return MigrationSourceType.JSON
        else:
            return MigrationSourceType.MANUAL
    
    async def _analyze_source_file(self, file: UploadFile, source_type: MigrationSourceType) -> Dict[str, Any]:
        """Analyze uploaded source file"""
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Reset file position
        await file.seek(0)
        
        analysis = {
            "file_size": file_size,
            "metadata": {},
            "total_records": 0,
            "detected_data_types": [],
            "preview_data": [],
            "validation_errors": [],
            "validation_warnings": []
        }
        
        try:
            if source_type == MigrationSourceType.EXCEL:
                # Use Excel service for analysis
                excel_buffer = io.BytesIO(content)
                df = pd.read_excel(excel_buffer)
                
                analysis["total_records"] = len(df)
                analysis["metadata"]["fields"] = df.columns.tolist()
                analysis["preview_data"] = df.head(5).to_dict("records")
                
                # Detect data types based on columns
                detected_types = self._detect_data_types_from_columns(df.columns.tolist())
                analysis["detected_data_types"] = detected_types
                
            elif source_type == MigrationSourceType.CSV:
                # CSV analysis
                csv_buffer = io.StringIO(content.decode('utf-8'))
                df = pd.read_csv(csv_buffer)
                
                analysis["total_records"] = len(df)
                analysis["metadata"]["fields"] = df.columns.tolist()
                analysis["preview_data"] = df.head(5).to_dict("records")
                
                detected_types = self._detect_data_types_from_columns(df.columns.tolist())
                analysis["detected_data_types"] = detected_types
                
            elif source_type == MigrationSourceType.JSON:
                # JSON analysis
                json_data = json.loads(content.decode('utf-8'))
                
                if isinstance(json_data, list):
                    analysis["total_records"] = len(json_data)
                    if json_data:
                        analysis["metadata"]["fields"] = list(json_data[0].keys())
                        analysis["preview_data"] = json_data[:5]
                else:
                    analysis["total_records"] = 1
                    analysis["metadata"]["fields"] = list(json_data.keys())
                    analysis["preview_data"] = [json_data]
                
                detected_types = self._detect_data_types_from_columns(analysis["metadata"]["fields"])
                analysis["detected_data_types"] = detected_types
        
        except Exception as e:
            analysis["validation_errors"].append(f"Failed to analyze file: {str(e)}")
        
        return analysis
    
    def _detect_data_types_from_columns(self, columns: List[str]) -> List[MigrationDataType]:
        """Detect data types based on column names"""
        detected_types = []
        
        # Define patterns for different data types
        patterns = {
            MigrationDataType.CUSTOMERS: ['customer', 'client', 'buyer'],
            MigrationDataType.VENDORS: ['vendor', 'supplier', 'seller'],
            MigrationDataType.PRODUCTS: ['product', 'item', 'sku'],
            MigrationDataType.STOCK: ['stock', 'inventory', 'quantity'],
            MigrationDataType.LEDGERS: ['ledger', 'account', 'balance'],
            MigrationDataType.VOUCHERS: ['voucher', 'transaction', 'entry'],
            MigrationDataType.CONTACTS: ['contact', 'person', 'name', 'email', 'phone']
        }
        
        column_text = ' '.join(columns).lower()
        
        for data_type, keywords in patterns.items():
            if any(keyword in column_text for keyword in keywords):
                detected_types.append(data_type)
        
        # Default to contacts if nothing detected
        if not detected_types:
            detected_types.append(MigrationDataType.CONTACTS)
        
        return detected_types
    
    async def _get_migration_template(
        self, 
        source_type: MigrationSourceType, 
        data_type: MigrationDataType
    ) -> Optional[MigrationTemplate]:
        """Get migration template for source and data type"""
        return self.db.query(MigrationTemplate).filter(
            and_(
                MigrationTemplate.source_type == source_type,
                MigrationTemplate.data_type == data_type,
                MigrationTemplate.is_active == True
            )
        ).first()
    
    def _get_required_fields(self, data_type: MigrationDataType) -> List[str]:
        """Get required fields for data type"""
        required_fields = {
            MigrationDataType.CUSTOMERS: ['name', 'contact_number'],
            MigrationDataType.VENDORS: ['name', 'contact_number'],
            MigrationDataType.PRODUCTS: ['product_name', 'unit'],
            MigrationDataType.STOCK: ['product_name', 'quantity'],
            MigrationDataType.LEDGERS: ['account_name', 'account_type'],
            MigrationDataType.VOUCHERS: ['voucher_number', 'date', 'amount'],
            MigrationDataType.CONTACTS: ['name']
        }
        
        return required_fields.get(data_type, [])
    
    def _validate_field_type(self, field_data: pd.Series, expected_type: str) -> bool:
        """Validate field data type"""
        try:
            if expected_type == "string":
                return True  # Most data can be string
            elif expected_type == "number":
                pd.to_numeric(field_data, errors='coerce')
                return True
            elif expected_type == "date":
                pd.to_datetime(field_data, errors='coerce')
                return True
            elif expected_type == "boolean":
                return field_data.dtype == bool or field_data.isin([True, False, 'true', 'false', 'yes', 'no', 1, 0]).all()
            else:
                return True
        except:
            return False
    
    async def _load_source_data(self, migration_job: MigrationJob) -> pd.DataFrame:
        """Load source data from migration job"""
        # This would load the actual source data
        # For now, return empty DataFrame
        return pd.DataFrame()
    
    async def _log_migration_event(
        self, 
        migration_job_id: int, 
        organization_id: int, 
        level: MigrationLogLevel, 
        message: str, 
        operation: str = None,
        source_record_id: str = None,
        target_record_id: int = None,
        error_details: Dict[str, Any] = None
    ):
        """Log migration event"""
        try:
            log_entry = MigrationLog(
                migration_job_id=migration_job_id,
                organization_id=organization_id,
                level=level,
                message=message,
                operation=operation,
                source_record_id=source_record_id,
                target_record_id=target_record_id,
                error_details=error_details
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log migration event: {str(e)}")
    
    async def _execute_migration(self, migration_job_id: int, organization_id: int, user_id: int):
        """Background task to execute migration"""
        try:
            # This would contain the actual migration logic
            # For now, simulate migration progress
            migration_job = self.db.query(MigrationJob).filter(
                MigrationJob.id == migration_job_id
            ).first()
            
            if not migration_job:
                return
            
            total_records = migration_job.total_records
            
            for i in range(0, total_records, 10):
                # Simulate processing batch
                await asyncio.sleep(1)
                
                processed = min(i + 10, total_records)
                progress = (processed / total_records) * 100
                
                # Update progress
                migration_job.processed_records = processed
                migration_job.progress_percentage = progress
                migration_job.success_records = processed  # Simulate all success for now
                
                self.db.commit()
                
                # Log progress
                await self._log_migration_event(
                    migration_job_id,
                    organization_id,
                    MigrationLogLevel.INFO,
                    f"Processed {processed}/{total_records} records",
                    operation="process_batch"
                )
            
            # Complete migration
            migration_job.status = MigrationJobStatus.COMPLETED
            migration_job.completed_at = datetime.utcnow()
            migration_job.progress_percentage = 100.0
            self.db.commit()
            
            await self._log_migration_event(
                migration_job_id,
                organization_id,
                MigrationLogLevel.INFO,
                "Migration completed successfully",
                operation="complete_migration"
            )
            
        except Exception as e:
            # Handle migration failure
            migration_job = self.db.query(MigrationJob).filter(
                MigrationJob.id == migration_job_id
            ).first()
            
            if migration_job:
                migration_job.status = MigrationJobStatus.FAILED
                self.db.commit()
                
                await self._log_migration_event(
                    migration_job_id,
                    organization_id,
                    MigrationLogLevel.ERROR,
                    f"Migration failed: {str(e)}",
                    operation="migration_error",
                    error_details={"error": str(e)}
                )
            
            logger.error(f"Migration execution failed: {str(e)}")


class TallyMigrationService:
    """Specialized service for Tally migration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tally_service = TallyIntegrationService()
    
    async def fetch_tally_data(self, organization_id: int, data_types: List[MigrationDataType]) -> Dict[str, Any]:
        """Fetch data from Tally"""
        # Implementation would fetch actual Tally data
        # For now, return mock data
        return {
            "ledgers": [],
            "vouchers": [],
            "companies": []
        }


class ZohoMigrationService:
    """Specialized service for Zoho migration"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def fetch_zoho_data(self, organization_id: int, data_types: List[MigrationDataType]) -> Dict[str, Any]:
        """Fetch data from Zoho"""
        # Implementation would fetch actual Zoho data
        # For now, return mock data
        return {
            "contacts": [],
            "products": [],
            "invoices": []
        }