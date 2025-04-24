# haive_dataflow/auth/credits.py
from typing import Optional, Dict, Any
import logging
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel

from supabase import create_client
from haive.dataflow.config.environment import get_supabase_server_config

logger = logging.getLogger(__name__)

class UsageRecord(BaseModel):
    """Record of agent usage."""
    agent_id: str
    user_id: str
    conversation_id: Optional[str] = None
    token_count: int
    cost: Decimal
    created_at: Optional[datetime] = None

class CreditsManager:
    """Manager for user credits and usage tracking."""
    
    def __init__(self):
        """Initialize with server-side config."""
        self.config = get_supabase_server_config()
        self._client = None
        
    @property
    def client(self):
        """Lazy-loaded Supabase admin client."""
        if self._client is None:
            self._client = create_client(
                self.config.url, 
                self.config.service_role_key.get_secret_value()
            )
        return self._client
    
    async def check_credits(self, user_id: str, required_credits: float = 1.0) -> bool:
        """
        Check if user has sufficient credits.
        
        Args:
            user_id: User ID
            required_credits: Required credits for the operation
            
        Returns:
            True if user has sufficient credits, False otherwise
        """
        try:
            # Query user credits with service role
            response = await self.client.from_("user_data.credits") \
                .select("available_credits") \
                .eq("user_id", user_id) \
                .limit(1) \
                .execute()
                
            if not response.data:
                # No credits record found
                return False
                
            available_credits = response.data[0].get("available_credits", 0)
            return available_credits >= required_credits
        except Exception as e:
            logger.error(f"Error checking credits: {e}")
            return False
    
    async def deduct_credits(self, user_id: str, amount: float) -> bool:
        """
        Deduct credits from user account.
        
        Args:
            user_id: User ID
            amount: Amount to deduct
            
        Returns:
            True if deduction was successful, False otherwise
        """
        try:
            # Use a database function for atomic update
            response = await self.client.rpc(
                "deduct_user_credits",
                {"p_user_id": user_id, "p_amount": amount}
            ).execute()
            
            return response.data.get("success", False)
        except Exception as e:
            logger.error(f"Error deducting credits: {e}")
            return False
    
    async def log_usage(self, usage: UsageRecord) -> bool:
        """
        Log agent usage for billing and analytics.
        
        Args:
            usage: Usage record
            
        Returns:
            True if logging was successful, False otherwise
        """
        try:
            # Insert usage record
            response = await self.client.from_("user_data.usage") \
                .insert({
                    "user_id": usage.user_id,
                    "agent_id": usage.agent_id,
                    "conversation_id": usage.conversation_id,
                    "token_count": usage.token_count,
                    "cost": float(usage.cost),
                    "created_at": usage.created_at.isoformat() if usage.created_at else None
                }) \
                .execute()
                
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error logging usage: {e}")
            return False