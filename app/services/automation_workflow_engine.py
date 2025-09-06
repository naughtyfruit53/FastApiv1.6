"""
Intelligent Automation Workflow Engine
"""

import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.ai_analytics_models import AutomationWorkflow, AIModel, PredictionResult, AnomalyDetection
from app.services.ai_analytics_service import AIAnalyticsService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class WorkflowExecutionContext:
    """Context for workflow execution"""
    
    def __init__(self, workflow_id: int, trigger_data: Dict[str, Any], user_id: Optional[int] = None):
        self.workflow_id = workflow_id
        self.trigger_data = trigger_data
        self.user_id = user_id
        self.execution_id = str(uuid.uuid4())
        self.started_at = datetime.utcnow()
        self.current_step = 0
        self.variables = {}
        self.errors = []
        self.step_results = []


class AutomationWorkflowEngine:
    """Engine for executing intelligent automation workflows"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIAnalyticsService(db)
        self.notification_service = NotificationService(db)
        self.step_handlers = self._register_step_handlers()
    
    def _register_step_handlers(self) -> Dict[str, Callable]:
        """Register workflow step handlers"""
        return {
            "ai_prediction": self._handle_ai_prediction_step,
            "condition_check": self._handle_condition_check_step,
            "data_query": self._handle_data_query_step,
            "notification": self._handle_notification_step,
            "approval_request": self._handle_approval_request_step,
            "data_update": self._handle_data_update_step,
            "external_api": self._handle_external_api_step,
            "delay": self._handle_delay_step,
            "parallel_execution": self._handle_parallel_execution_step,
            "loop": self._handle_loop_step,
            "script_execution": self._handle_script_execution_step
        }
    
    def execute_workflow(
        self, 
        organization_id: int,
        workflow_id: int, 
        trigger_data: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute an automation workflow"""
        try:
            # Get workflow definition
            workflow = self.db.query(AutomationWorkflow).filter(
                and_(
                    AutomationWorkflow.id == workflow_id,
                    AutomationWorkflow.organization_id == organization_id,
                    AutomationWorkflow.is_active == True
                )
            ).first()
            
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found or inactive")
            
            # Create execution context
            context = WorkflowExecutionContext(workflow_id, trigger_data, user_id)
            
            logger.info(f"Starting workflow execution {context.execution_id} for workflow {workflow.workflow_name}")
            
            # Execute workflow steps
            success = self._execute_workflow_steps(workflow, context)
            
            # Update workflow statistics
            workflow.execution_count += 1
            if success:
                workflow.success_count += 1
                workflow.last_execution_status = "success"
            else:
                workflow.last_execution_status = "failed"
            
            workflow.last_execution_at = datetime.utcnow()
            self.db.commit()
            
            execution_result = {
                "execution_id": context.execution_id,
                "workflow_id": workflow_id,
                "status": "success" if success else "failed",
                "started_at": context.started_at,
                "completed_at": datetime.utcnow(),
                "steps_executed": context.current_step,
                "step_results": context.step_results,
                "errors": context.errors,
                "variables": context.variables
            }
            
            logger.info(f"Workflow execution {context.execution_id} completed with status: {execution_result['status']}")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
            raise
    
    def _execute_workflow_steps(self, workflow: AutomationWorkflow, context: WorkflowExecutionContext) -> bool:
        """Execute individual workflow steps"""
        try:
            steps = workflow.workflow_steps
            
            for i, step in enumerate(steps):
                context.current_step = i + 1
                
                step_type = step.get("type")
                if step_type not in self.step_handlers:
                    error_msg = f"Unknown step type: {step_type}"
                    context.errors.append(error_msg)
                    logger.error(error_msg)
                    return False
                
                # Check if step should be executed based on conditions
                if not self._should_execute_step(step, context):
                    context.step_results.append({
                        "step": i + 1,
                        "type": step_type,
                        "status": "skipped",
                        "reason": "Condition not met"
                    })
                    continue
                
                # Execute step
                try:
                    step_result = self.step_handlers[step_type](step, context)
                    context.step_results.append({
                        "step": i + 1,
                        "type": step_type,
                        "status": "success",
                        "result": step_result
                    })
                    
                    # Check if step failed and should stop execution
                    if step_result.get("stop_execution", False):
                        return False
                        
                except Exception as e:
                    error_msg = f"Step {i + 1} ({step_type}) failed: {str(e)}"
                    context.errors.append(error_msg)
                    context.step_results.append({
                        "step": i + 1,
                        "type": step_type,
                        "status": "failed",
                        "error": str(e)
                    })
                    
                    # Check if workflow should continue on error
                    if not step.get("continue_on_error", False):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing workflow steps: {str(e)}")
            context.errors.append(str(e))
            return False
    
    def _should_execute_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> bool:
        """Check if a step should be executed based on conditions"""
        conditions = step.get("conditions", [])
        if not conditions:
            return True
        
        for condition in conditions:
            condition_type = condition.get("type", "variable")
            
            if condition_type == "variable":
                variable_name = condition.get("variable")
                operator = condition.get("operator", "equals")
                expected_value = condition.get("value")
                
                actual_value = context.variables.get(variable_name)
                
                if operator == "equals" and actual_value != expected_value:
                    return False
                elif operator == "not_equals" and actual_value == expected_value:
                    return False
                elif operator == "greater_than" and actual_value <= expected_value:
                    return False
                elif operator == "less_than" and actual_value >= expected_value:
                    return False
                elif operator == "contains" and expected_value not in str(actual_value):
                    return False
                elif operator == "exists" and actual_value is None:
                    return False
                elif operator == "not_exists" and actual_value is not None:
                    return False
        
        return True
    
    # Step Handler Methods
    
    def _handle_ai_prediction_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle AI prediction step"""
        model_id = step.get("model_id")
        input_mapping = step.get("input_mapping", {})
        output_variable = step.get("output_variable", "prediction_result")
        
        # Prepare input data from context variables and trigger data
        input_data = {}
        for model_field, source_field in input_mapping.items():
            if source_field.startswith("trigger."):
                source_value = context.trigger_data.get(source_field[8:])
            elif source_field.startswith("var."):
                source_value = context.variables.get(source_field[4:])
            else:
                source_value = context.trigger_data.get(source_field)
            
            input_data[model_field] = source_value
        
        # Make prediction
        from app.schemas.ai_analytics import PredictionRequest
        prediction_request = PredictionRequest(
            model_id=model_id,
            input_data=input_data,
            prediction_context=f"workflow_{context.workflow_id}",
            business_entity_type="workflow_execution",
            business_entity_id=context.workflow_id
        )
        
        prediction_result = self.ai_service.make_prediction(
            organization_id=context.trigger_data.get("organization_id"),
            prediction_request=prediction_request,
            user_id=context.user_id
        )
        
        # Store result in context variables
        context.variables[output_variable] = {
            "prediction_id": prediction_result.prediction_id,
            "output": prediction_result.prediction_output,
            "confidence": prediction_result.confidence_score
        }
        
        return {
            "prediction_id": prediction_result.prediction_id,
            "confidence": prediction_result.confidence_score
        }
    
    def _handle_condition_check_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle condition check step"""
        conditions = step.get("conditions", [])
        logic_operator = step.get("logic_operator", "and")  # "and" or "or"
        
        results = []
        for condition in conditions:
            variable_name = condition.get("variable")
            operator = condition.get("operator")
            expected_value = condition.get("value")
            
            actual_value = context.variables.get(variable_name)
            result = self._evaluate_condition(actual_value, operator, expected_value)
            results.append(result)
        
        # Apply logic operator
        if logic_operator == "and":
            final_result = all(results)
        else:  # "or"
            final_result = any(results)
        
        context.variables[step.get("output_variable", "condition_result")] = final_result
        
        return {"result": final_result, "individual_results": results}
    
    def _handle_data_query_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle data query step"""
        query_type = step.get("query_type", "count")
        table_name = step.get("table_name")
        filters = step.get("filters", [])
        output_variable = step.get("output_variable", "query_result")
        
        # Build query (simplified implementation)
        if table_name == "customers":
            query = self.db.query(self.db.query(Customer))
        elif table_name == "sales":
            query = self.db.query(SalesAnalytics)
        else:
            raise ValueError(f"Unsupported table: {table_name}")
        
        # Apply filters
        for filter_condition in filters:
            field = filter_condition.get("field")
            operator = filter_condition.get("operator")
            value = filter_condition.get("value")
            
            # Add filter to query (simplified)
            if operator == "equals":
                query = query.filter(getattr(query.column_descriptions[0]['type'], field) == value)
        
        # Execute query based on type
        if query_type == "count":
            result = query.count()
        elif query_type == "sum":
            sum_field = step.get("sum_field")
            result = query.with_entities(func.sum(getattr(query.column_descriptions[0]['type'], sum_field))).scalar() or 0
        else:
            result = query.all()
        
        context.variables[output_variable] = result
        
        return {"result": result, "query_type": query_type}
    
    def _handle_notification_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle notification step"""
        notification_type = step.get("notification_type", "email")
        recipients = step.get("recipients", [])
        subject = step.get("subject", "")
        message = step.get("message", "")
        
        # Replace variables in subject and message
        subject = self._replace_variables(subject, context)
        message = self._replace_variables(message, context)
        
        # Send notification
        notification_id = self.notification_service.send_notification(
            notification_type=notification_type,
            recipients=recipients,
            subject=subject,
            message=message,
            context={"workflow_execution_id": context.execution_id}
        )
        
        return {"notification_id": notification_id}
    
    def _handle_approval_request_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle approval request step"""
        approvers = step.get("approvers", [])
        approval_message = step.get("approval_message", "")
        timeout_hours = step.get("timeout_hours", 24)
        
        # Create approval request (simplified implementation)
        approval_id = str(uuid.uuid4())
        
        # Send approval notification
        for approver_id in approvers:
            self.notification_service.send_notification(
                notification_type="approval_request",
                recipients=[approver_id],
                subject=f"Approval Required: Workflow {context.workflow_id}",
                message=approval_message,
                context={
                    "approval_id": approval_id,
                    "workflow_execution_id": context.execution_id
                }
            )
        
        context.variables["approval_id"] = approval_id
        context.variables["approval_status"] = "pending"
        
        return {
            "approval_id": approval_id,
            "status": "pending",
            "timeout_at": datetime.utcnow() + timedelta(hours=timeout_hours)
        }
    
    def _handle_data_update_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle data update step"""
        table_name = step.get("table_name")
        record_id = step.get("record_id")
        updates = step.get("updates", {})
        
        # Apply variable replacements to update values
        processed_updates = {}
        for field, value in updates.items():
            if isinstance(value, str):
                processed_updates[field] = self._replace_variables(value, context)
            else:
                processed_updates[field] = value
        
        # Update record (simplified implementation)
        # In practice, this would use the appropriate model and update the record
        
        return {"updated_fields": list(processed_updates.keys())}
    
    def _handle_external_api_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle external API call step"""
        import requests
        
        url = step.get("url")
        method = step.get("method", "GET")
        headers = step.get("headers", {})
        payload = step.get("payload", {})
        output_variable = step.get("output_variable", "api_response")
        
        # Replace variables in URL, headers, and payload
        url = self._replace_variables(url, context)
        
        processed_headers = {}
        for key, value in headers.items():
            processed_headers[key] = self._replace_variables(str(value), context)
        
        processed_payload = {}
        for key, value in payload.items():
            if isinstance(value, str):
                processed_payload[key] = self._replace_variables(value, context)
            else:
                processed_payload[key] = value
        
        # Make API call
        response = requests.request(
            method=method,
            url=url,
            headers=processed_headers,
            json=processed_payload if method in ["POST", "PUT", "PATCH"] else None,
            timeout=30
        )
        
        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        }
        
        context.variables[output_variable] = response_data
        
        return response_data
    
    def _handle_delay_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle delay step"""
        import time
        
        delay_seconds = step.get("delay_seconds", 0)
        delay_minutes = step.get("delay_minutes", 0)
        delay_hours = step.get("delay_hours", 0)
        
        total_seconds = delay_seconds + (delay_minutes * 60) + (delay_hours * 3600)
        
        if total_seconds > 0:
            time.sleep(min(total_seconds, 300))  # Cap at 5 minutes for safety
        
        return {"delayed_seconds": total_seconds}
    
    def _handle_parallel_execution_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle parallel execution step"""
        parallel_steps = step.get("parallel_steps", [])
        results = []
        
        # Execute steps in parallel (simplified sequential execution for now)
        for parallel_step in parallel_steps:
            step_type = parallel_step.get("type")
            if step_type in self.step_handlers:
                try:
                    result = self.step_handlers[step_type](parallel_step, context)
                    results.append({"status": "success", "result": result})
                except Exception as e:
                    results.append({"status": "failed", "error": str(e)})
            else:
                results.append({"status": "failed", "error": f"Unknown step type: {step_type}"})
        
        return {"parallel_results": results}
    
    def _handle_loop_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle loop step"""
        loop_variable = step.get("loop_variable", "i")
        loop_start = step.get("loop_start", 0)
        loop_end = step.get("loop_end", 1)
        loop_steps = step.get("loop_steps", [])
        
        results = []
        
        for i in range(loop_start, loop_end):
            context.variables[loop_variable] = i
            
            for loop_step in loop_steps:
                step_type = loop_step.get("type")
                if step_type in self.step_handlers:
                    try:
                        result = self.step_handlers[step_type](loop_step, context)
                        results.append({"iteration": i, "status": "success", "result": result})
                    except Exception as e:
                        results.append({"iteration": i, "status": "failed", "error": str(e)})
        
        return {"loop_results": results}
    
    def _handle_script_execution_step(self, step: Dict[str, Any], context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle script execution step (SECURITY WARNING: Only for trusted scripts)"""
        script_code = step.get("script_code", "")
        script_language = step.get("script_language", "python")
        output_variable = step.get("output_variable", "script_result")
        
        if script_language != "python":
            raise ValueError(f"Unsupported script language: {script_language}")
        
        # Create safe execution environment
        safe_globals = {
            "__builtins__": {},
            "context": context,
            "variables": context.variables,
            "trigger_data": context.trigger_data
        }
        
        try:
            # Execute script (CAUTION: This is potentially dangerous)
            exec(script_code, safe_globals)
            result = safe_globals.get("result", "Script executed successfully")
            context.variables[output_variable] = result
            return {"result": result}
        except Exception as e:
            raise Exception(f"Script execution failed: {str(e)}")
    
    # Helper Methods
    
    def _evaluate_condition(self, actual_value: Any, operator: str, expected_value: Any) -> bool:
        """Evaluate a single condition"""
        if operator == "equals":
            return actual_value == expected_value
        elif operator == "not_equals":
            return actual_value != expected_value
        elif operator == "greater_than":
            return actual_value > expected_value
        elif operator == "less_than":
            return actual_value < expected_value
        elif operator == "greater_than_or_equal":
            return actual_value >= expected_value
        elif operator == "less_than_or_equal":
            return actual_value <= expected_value
        elif operator == "contains":
            return expected_value in str(actual_value)
        elif operator == "not_contains":
            return expected_value not in str(actual_value)
        elif operator == "starts_with":
            return str(actual_value).startswith(str(expected_value))
        elif operator == "ends_with":
            return str(actual_value).endswith(str(expected_value))
        elif operator == "exists":
            return actual_value is not None
        elif operator == "not_exists":
            return actual_value is None
        elif operator == "in":
            return actual_value in expected_value
        elif operator == "not_in":
            return actual_value not in expected_value
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    
    def _replace_variables(self, text: str, context: WorkflowExecutionContext) -> str:
        """Replace variables in text with actual values"""
        import re
        
        # Replace variables like {{variable_name}} with actual values
        def replace_variable(match):
            var_name = match.group(1)
            
            if var_name.startswith("trigger."):
                return str(context.trigger_data.get(var_name[8:], ""))
            elif var_name.startswith("var."):
                return str(context.variables.get(var_name[4:], ""))
            else:
                return str(context.variables.get(var_name, ""))
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_variable, text)
    
    def trigger_workflows_by_event(
        self, 
        organization_id: int, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Trigger workflows based on business events"""
        try:
            # Find workflows that should be triggered by this event
            workflows = self.db.query(AutomationWorkflow).filter(
                and_(
                    AutomationWorkflow.organization_id == organization_id,
                    AutomationWorkflow.is_active == True,
                    AutomationWorkflow.workflow_type.in_(["event_driven", "ai_triggered"])
                )
            ).all()
            
            triggered_workflows = []
            
            for workflow in workflows:
                trigger_conditions = workflow.trigger_conditions
                
                # Check if this event should trigger the workflow
                if self._should_trigger_workflow(trigger_conditions, event_type, event_data):
                    try:
                        result = self.execute_workflow(
                            organization_id=organization_id,
                            workflow_id=workflow.id,
                            trigger_data={**event_data, "event_type": event_type},
                            user_id=event_data.get("user_id")
                        )
                        triggered_workflows.append(result)
                    except Exception as e:
                        logger.error(f"Failed to execute triggered workflow {workflow.id}: {str(e)}")
            
            return triggered_workflows
            
        except Exception as e:
            logger.error(f"Error triggering workflows by event: {str(e)}")
            return []
    
    def _should_trigger_workflow(
        self, 
        trigger_conditions: Dict[str, Any], 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> bool:
        """Check if a workflow should be triggered by an event"""
        # Check event type match
        if trigger_conditions.get("event_type") != event_type:
            return False
        
        # Check additional conditions
        conditions = trigger_conditions.get("conditions", [])
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            event_value = event_data.get(field)
            
            if not self._evaluate_condition(event_value, operator, value):
                return False
        
        return True