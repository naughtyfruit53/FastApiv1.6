"""
AI Agents Models for Modular Microservices Architecture
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Float, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any

from app.core.database import Base


class AgentType(PyEnum):
    """Types of AI agents available"""
    ANALYTICS = "analytics"
    BUSINESS_ADVICE = "business_advice"
    NAVIGATION = "navigation"
    WEBSITE_CUSTOMIZATION = "website_customization"
    CHATBOT = "chatbot"
    AUTOMATION = "automation"


class AgentStatus(PyEnum):
    """Status of AI agent"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AgentCapability(PyEnum):
    """Capabilities that agents can have"""
    NLP = "nlp"
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    ANALYSIS = "analysis"


class AIAgent(Base):
    """
    AI Agent configuration and metadata.
    Represents a modular AI microservice agent.
    """
    __tablename__ = "ai_agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_ai_agent_organization_id"), 
        nullable=False, 
        index=True
    )
    
    # Agent identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Agent configuration
    status: Mapped[str] = mapped_column(String(50), default="inactive", nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    capabilities: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Service endpoint information
    endpoint_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Configuration and settings
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Performance and usage tracking
    total_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_response_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interactions: Mapped[list["AIAgentInteraction"]] = relationship(
        "AIAgentInteraction", 
        back_populates="agent",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_ai_agent_org_type', 'organization_id', 'agent_type'),
        Index('idx_ai_agent_status', 'status'),
        {'extend_existing': True}
    )


class AIAgentInteraction(Base):
    """
    Log of interactions with AI agents.
    Tracks requests, responses, and performance metrics.
    """
    __tablename__ = "ai_agent_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_ai_interaction_organization_id"), 
        nullable=False, 
        index=True
    )
    
    # Agent reference
    agent_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("ai_agents.id", name="fk_ai_interaction_agent_id"), 
        nullable=False,
        index=True
    )
    
    # User reference
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_ai_interaction_user_id"), 
        nullable=True,
        index=True
    )
    
    # Interaction details
    interaction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    request_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    response_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Performance metrics
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Context
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent: Mapped["AIAgent"] = relationship("AIAgent", back_populates="interactions")
    user: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    
    __table_args__ = (
        Index('idx_ai_interaction_org_agent', 'organization_id', 'agent_id'),
        Index('idx_ai_interaction_created', 'created_at'),
        Index('idx_ai_interaction_session', 'session_id'),
        {'extend_existing': True}
    )


class AIAgentCapability(Base):
    """
    Capabilities and features of AI agents.
    Allows agents to declare what they can do.
    """
    __tablename__ = "ai_agent_capabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Agent reference
    agent_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("ai_agents.id", name="fk_ai_capability_agent_id"), 
        nullable=False,
        index=True
    )
    
    # Capability details
    capability_name: Mapped[str] = mapped_column(String(100), nullable=False)
    capability_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Configuration
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_ai_capability_agent', 'agent_id'),
        {'extend_existing': True}
    )
