"""
Logging configuration for the CopilotKit FastAPI app
"""

import logging
import sys

def setup_logging(verbose: bool = False):
    """
    Configure logging levels for the application
    
    Args:
        verbose: If True, enable debug logging for the app
    """
    
    # Root logger level
    root_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=root_level)
    
    # Mute ALL haive packages at the root level
    logging.getLogger("haive").setLevel(logging.CRITICAL)
    
    # Specifically mute the most verbose modules
    """
    haive_modules = [
        "haive.core",
        "haive.agents", 
        "haive.core.graph",
        "haive.core.graph.node",
        "haive.core.graph.node.engine_node",
        "haive.core.persistence",
        "haive.core.persistence.handlers",
        "haive.agents.base",
        "haive.agents.base.agent",
        "haive.core.engine",
        "haive.core.models",
        "haive.core.schema"
    ]
   
    for module in haive_modules:
        logger = logging.getLogger(module)
        logger.setLevel(logging.CRITICAL)
        logger.propagate = False  # Prevent propagation to parent loggers
     """
    # Mute other noisy libraries
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Mute OpenAI client logging
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    logging.getLogger("openai._client").setLevel(logging.WARNING)
    
    # Mute other potentially noisy AI/ML libraries
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langchain_core").setLevel(logging.WARNING)
    logging.getLogger("langgraph").setLevel(logging.WARNING)
    
    # Keep our app logging visible
    logging.getLogger("copilotkit").setLevel(logging.INFO)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    
    print(f"🔇 Logging configured - Haive modules COMPLETELY muted, app logging {'verbose' if verbose else 'normal'}")

def mute_all_haive():
    """Completely mute all haive logging"""
    logging.getLogger("haive").setLevel(logging.CRITICAL)
    print("🔇 All Haive logging muted")

def mute_openai_completely():
    """Completely silence OpenAI client logging"""
    logging.getLogger("openai").setLevel(logging.CRITICAL)
    logging.getLogger("openai._base_client").setLevel(logging.CRITICAL)
    logging.getLogger("openai._client").setLevel(logging.CRITICAL)
    print("🔇 OpenAI client completely muted")

def unmute_haive():
    """Re-enable haive logging"""
    logging.getLogger("haive").setLevel(logging.INFO)
    print("🔊 Haive logging re-enabled")

def nuclear_silence():
    """Nuclear option - silence almost everything except critical errors"""
    for logger_name in [
        "haive", "openai", "anthropic", "langchain", "langchain_core", 
         "httpx", "httpcore", "urllib3", "asyncio",
         #"langgraph",
    ]:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    print("☢️ Nuclear silence activated - only critical errors will show") 