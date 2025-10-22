"""
AI Agents API endpoints for microservices architecture
Manages modular AI agents: analytics, business advice, navigation, website customization
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.user_models import User
from app.models.ai_agents import AIAgent, AIAgentInteraction, AIAgentCapability

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-agents", tags=["ai-agents"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class AIAgentCreate(BaseModel):
    """Schema for creating AI agent"""
    name: str = Field(..., description="Agent name")
    agent_type: str = Field(..., description="Type of agent")
    description: Optional[str] = None
    version: str = Field(default="1.0.0")
    capabilities: Optional[Dict[str, Any]] = None
    endpoint_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


class AIAgentUpdate(BaseModel):
    """Schema for updating AI agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    version: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None
    endpoint_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


class AIAgentResponse(BaseModel):
    """Schema for AI agent response"""
    id: int
    organization_id: int
    name: str
    agent_type: str
    description: Optional[str]
    status: str
    version: str
    capabilities: Optional[Dict[str, Any]]
    endpoint_url: Optional[str]
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: Optional[float]
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AIAgentInteractionCreate(BaseModel):
    """Schema for creating interaction"""
    agent_id: int
    interaction_type: str
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    response_time_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    session_id: Optional[str] = None


class AIAgentInteractionResponse(BaseModel):
    """Schema for interaction response"""
    id: int
    organization_id: int
    agent_id: int
    user_id: Optional[int]
    interaction_type: str
    request_data: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]
    response_time_ms: Optional[int]
    success: bool
    error_message: Optional[str]
    session_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AI Agent Endpoints
# ============================================================================

@router.post("/", response_model=AIAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_agent(
    agent_data: AIAgentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new AI agent.
    """
    try:
        agent = AIAgent(
            organization_id=current_user.organization_id,
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            description=agent_data.description,
            version=agent_data.version,
            capabilities=agent_data.capabilities,
            endpoint_url=agent_data.endpoint_url,
            config=agent_data.config,
            parameters=agent_data.parameters,
            status="inactive"
        )
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        logger.info(f"User {current_user.id} created AI agent {agent.id} ({agent.name})")
        return agent
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating AI agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AI agent: {str(e)}"
        )


@router.get("/", response_model=List[AIAgentResponse])
async def list_ai_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    agent_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all AI agents for the organization.
    """
    try:
        query = db.query(AIAgent).filter(
            AIAgent.organization_id == current_user.organization_id
        )
        
        if agent_type:
            query = query.filter(AIAgent.agent_type == agent_type)
        
        if status:
            query = query.filter(AIAgent.status == status)
        
        agents = query.order_by(desc(AIAgent.created_at)).offset(skip).limit(limit).all()
        
        logger.info(f"User {current_user.id} listed {len(agents)} AI agents")
        return agents
        
    except Exception as e:
        logger.error(f"Error listing AI agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list AI agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AIAgentResponse)
async def get_ai_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific AI agent.
    """
    try:
        agent = db.query(AIAgent).filter(
            and_(
                AIAgent.id == agent_id,
                AIAgent.organization_id == current_user.organization_id
            )
        ).first()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI agent not found"
            )
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI agent: {str(e)}"
        )


@router.put("/{agent_id}", response_model=AIAgentResponse)
async def update_ai_agent(
    agent_id: int,
    agent_data: AIAgentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an AI agent.
    """
    try:
        agent = db.query(AIAgent).filter(
            and_(
                AIAgent.id == agent_id,
                AIAgent.organization_id == current_user.organization_id
            )
        ).first()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI agent not found"
            )
        
        # Update fields
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        db.commit()
        db.refresh(agent)
        
        logger.info(f"User {current_user.id} updated AI agent {agent.id}")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating AI agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update AI agent: {str(e)}"
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an AI agent.
    """
    try:
        agent = db.query(AIAgent).filter(
            and_(
                AIAgent.id == agent_id,
                AIAgent.organization_id == current_user.organization_id
            )
        ).first()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI agent not found"
            )
        
        db.delete(agent)
        db.commit()
        
        logger.info(f"User {current_user.id} deleted AI agent {agent_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting AI agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete AI agent: {str(e)}"
        )


# ============================================================================
# AI Agent Interaction Endpoints
# ============================================================================

@router.post("/interactions", response_model=AIAgentInteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction_data: AIAgentInteractionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Log an AI agent interaction.
    """
    try:
        # Verify agent belongs to organization
        agent = db.query(AIAgent).filter(
            and_(
                AIAgent.id == interaction_data.agent_id,
                AIAgent.organization_id == current_user.organization_id
            )
        ).first()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI agent not found"
            )
        
        interaction = AIAgentInteraction(
            organization_id=current_user.organization_id,
            agent_id=interaction_data.agent_id,
            user_id=current_user.id,
            interaction_type=interaction_data.interaction_type,
            request_data=interaction_data.request_data,
            response_data=interaction_data.response_data,
            response_time_ms=interaction_data.response_time_ms,
            success=interaction_data.success,
            error_message=interaction_data.error_message,
            session_id=interaction_data.session_id
        )
        
        db.add(interaction)
        
        # Update agent statistics
        agent.total_requests += 1
        if interaction_data.success:
            agent.successful_requests += 1
        else:
            agent.failed_requests += 1
        
        if interaction_data.response_time_ms:
            if agent.average_response_time:
                agent.average_response_time = (
                    agent.average_response_time * 0.9 + interaction_data.response_time_ms * 0.1
                )
            else:
                agent.average_response_time = float(interaction_data.response_time_ms)
        
        agent.last_used_at = datetime.utcnow()
        
        db.commit()
        db.refresh(interaction)
        
        return interaction
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating interaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interaction: {str(e)}"
        )


@router.get("/interactions", response_model=List[AIAgentInteractionResponse])
async def list_interactions(
    agent_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List AI agent interactions.
    """
    try:
        query = db.query(AIAgentInteraction).filter(
            AIAgentInteraction.organization_id == current_user.organization_id
        )
        
        if agent_id:
            query = query.filter(AIAgentInteraction.agent_id == agent_id)
        
        interactions = query.order_by(desc(AIAgentInteraction.created_at)).offset(skip).limit(limit).all()
        
        return interactions
        
    except Exception as e:
        logger.error(f"Error listing interactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list interactions: {str(e)}"
        )


@router.get("/statistics", response_model=Dict[str, Any])
async def get_agent_statistics(
    agent_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for AI agents.
    """
    try:
        query = db.query(AIAgent).filter(
            AIAgent.organization_id == current_user.organization_id
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
                    "total_requests": a.total_requests,
                    "success_rate": (a.successful_requests / a.total_requests * 100) if a.total_requests > 0 else 0,
                    "average_response_time": a.average_response_time
                }
                for a in agents
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
