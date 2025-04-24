# haive_dataflow/api/routes/agent_routes.py
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import logging

from haive.dataflow.auth.dependencies import require_auth
from haive.dataflow.auth.credits import CreditsManager, UsageRecord
from haive.dataflow.persistence.conversations import ConversationManager, ConversationMetadata
from haive.dataflow.config.settings import get_settings

# Try importing from your registry - adjust path as needed
try:
    from haive.core.registry import AgentRegistry
except ImportError:
    # Mock registry for testing
    class AgentRegistry:
        @staticmethod
        async def get_agent(agent_id: str):
            return None
        
        @staticmethod
        async def list_agents():
            return []

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["Agents"])
credits_manager = CreditsManager()
conversation_manager = ConversationManager()
settings = get_settings()

@router.get("/")
async def list_agents(
    user_id: str = Depends(require_auth),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """List available agents."""
    try:
        # Get agents from registry
        agents = await AgentRegistry.list_agents()
        
        # Return paginated results
        return {
            "agents": agents[offset:offset+limit],
            "total": len(agents),
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail="Error listing agents")

@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    user_id: str = Depends(require_auth)
):
    """Get agent details."""
    agent = await AgentRegistry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Return agent details (ensure not returning sensitive info)
    return {
        "id": agent_id,
        "name": getattr(agent, "name", "Unknown"),
        "description": getattr(agent, "description", None),
        "capabilities": getattr(agent, "capabilities", []),
    }

@router.post("/{agent_id}/conversations")
async def create_conversation(
    agent_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(require_auth)
):
    """Create a new conversation with an agent."""
    # Check if agent exists
    agent = await AgentRegistry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check credits
    has_credits = await credits_manager.check_credits(user_id)
    if not has_credits:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Process metadata
    conversation_metadata = ConversationMetadata(
        agent_id=agent_id,
        title=metadata.get("title") if metadata else None,
        description=metadata.get("description") if metadata else None,
        tags=metadata.get("tags") if metadata else None,
        custom_data=metadata.get("custom_data") if metadata else None
    )
    
    # Create conversation
    result = await conversation_manager.create_conversation(
        user_id, 
        conversation_metadata
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create conversation")
    
    return result