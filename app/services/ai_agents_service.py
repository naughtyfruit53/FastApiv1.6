"""
AI Agents Service Layer
Business logic for managing AI agents and their interactions
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.ai_agents import AIAgent, AIAgentInteraction, AIAgentCapability

logger = logging.getLogger(__name__)


class AIAgentsService:
    """Service for managing AI agents"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_agent(
        self,
        organization_id: int,
        name: str,
        agent_type: str,
        **kwargs
    ) -> AIAgent:
        """
        Create a new AI agent.
        
        Args:
            organization_id: Organization ID
            name: Agent name
            agent_type: Type of agent
            **kwargs: Additional agent properties
            
        Returns:
            Created AI agent
        """
        agent = AIAgent(
            organization_id=organization_id,
            name=name,
            agent_type=agent_type,
            **kwargs
        )
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        
        logger.info(f"Created AI agent {agent.id} ({name}) for organization {organization_id}")
        return agent
    
    def get_agent(self, agent_id: int, organization_id: int) -> Optional[AIAgent]:
        """
        Get an AI agent by ID.
        
        Args:
            agent_id: Agent ID
            organization_id: Organization ID
            
        Returns:
            AI agent or None
        """
        return self.db.query(AIAgent).filter(
            and_(
                AIAgent.id == agent_id,
                AIAgent.organization_id == organization_id
            )
        ).first()
    
    def list_agents(
        self,
        organization_id: int,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIAgent]:
        """
        List AI agents for an organization.
        
        Args:
            organization_id: Organization ID
            agent_type: Filter by agent type
            status: Filter by status
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of AI agents
        """
        query = self.db.query(AIAgent).filter(
            AIAgent.organization_id == organization_id
        )
        
        if agent_type:
            query = query.filter(AIAgent.agent_type == agent_type)
        
        if status:
            query = query.filter(AIAgent.status == status)
        
        return query.order_by(desc(AIAgent.created_at)).offset(skip).limit(limit).all()
    
    def update_agent(
        self,
        agent_id: int,
        organization_id: int,
        **kwargs
    ) -> Optional[AIAgent]:
        """
        Update an AI agent.
        
        Args:
            agent_id: Agent ID
            organization_id: Organization ID
            **kwargs: Fields to update
            
        Returns:
            Updated agent or None
        """
        agent = self.get_agent(agent_id, organization_id)
        if not agent:
            return None
        
        for key, value in kwargs.items():
            if hasattr(agent, key) and value is not None:
                setattr(agent, key, value)
        
        self.db.commit()
        self.db.refresh(agent)
        
        logger.info(f"Updated AI agent {agent_id}")
        return agent
    
    def delete_agent(self, agent_id: int, organization_id: int) -> bool:
        """
        Delete an AI agent.
        
        Args:
            agent_id: Agent ID
            organization_id: Organization ID
            
        Returns:
            True if deleted, False if not found
        """
        agent = self.get_agent(agent_id, organization_id)
        if not agent:
            return False
        
        self.db.delete(agent)
        self.db.commit()
        
        logger.info(f"Deleted AI agent {agent_id}")
        return True
    
    def log_interaction(
        self,
        agent_id: int,
        organization_id: int,
        user_id: Optional[int],
        interaction_type: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        response_time_ms: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AIAgentInteraction:
        """
        Log an interaction with an AI agent.
        
        Args:
            agent_id: Agent ID
            organization_id: Organization ID
            user_id: User ID
            interaction_type: Type of interaction
            request_data: Request payload
            response_data: Response payload
            response_time_ms: Response time in milliseconds
            success: Whether interaction was successful
            error_message: Error message if failed
            session_id: Session ID
            ip_address: IP address
            user_agent: User agent
            
        Returns:
            Created interaction record
        """
        interaction = AIAgentInteraction(
            organization_id=organization_id,
            agent_id=agent_id,
            user_id=user_id,
            interaction_type=interaction_type,
            request_data=request_data,
            response_data=response_data,
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_message,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(interaction)
        
        # Update agent statistics
        agent = self.get_agent(agent_id, organization_id)
        if agent:
            agent.total_requests += 1
            if success:
                agent.successful_requests += 1
            else:
                agent.failed_requests += 1
            
            if response_time_ms:
                if agent.average_response_time:
                    # Exponential moving average
                    agent.average_response_time = (
                        agent.average_response_time * 0.9 + response_time_ms * 0.1
                    )
                else:
                    agent.average_response_time = float(response_time_ms)
            
            agent.last_used_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(interaction)
        
        return interaction
    
    def get_agent_statistics(
        self,
        organization_id: int,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for AI agents.
        
        Args:
            organization_id: Organization ID
            agent_id: Specific agent ID (optional)
            
        Returns:
            Statistics dictionary
        """
        query = self.db.query(AIAgent).filter(
            AIAgent.organization_id == organization_id
        )
        
        if agent_id:
            query = query.filter(AIAgent.id == agent_id)
        
        agents = query.all()
        
        total_requests = sum(a.total_requests for a in agents)
        successful_requests = sum(a.successful_requests for a in agents)
        failed_requests = sum(a.failed_requests for a in agents)
        
        return {
            "total_agents": len(agents),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "agents": [
                {
                    "id": a.id,
                    "name": a.name,
                    "type": a.agent_type,
                    "status": a.status,
                    "total_requests": a.total_requests,
                    "success_rate": (a.successful_requests / a.total_requests * 100) if a.total_requests > 0 else 0,
                    "average_response_time": a.average_response_time,
                    "last_used_at": a.last_used_at
                }
                for a in agents
            ]
        }
    
    def activate_agent(self, agent_id: int, organization_id: int) -> Optional[AIAgent]:
        """
        Activate an AI agent.
        
        Args:
            agent_id: Agent ID
            organization_id: Organization ID
            
        Returns:
            Updated agent or None
        """
        return self.update_agent(agent_id, organization_id, status="active")
    
    def deactivate_agent(self, agent_id: int, organization_id: int) -> Optional[AIAgent]:
        """
        Deactivate an AI agent.
        
        Args:
            agent_id: Agent ID
            organization_id: Organization ID
            
        Returns:
            Updated agent or None
        """
        return self.update_agent(agent_id, organization_id, status="inactive")
