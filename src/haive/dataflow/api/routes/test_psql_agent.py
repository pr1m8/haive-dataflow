from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import logging
import os
import sys
from datetime import datetime

from haive.agents.simple.agent import SimpleAgent
from langchain_core.messages import HumanMessage

from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("HAIVE_DEBUG") == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("debug_psql_agent.log")
    ]
)
logger = logging.getLogger(__name__)

# Initialize agent with error handling
try:
    logger.info("Initializing SimpleAgent...")
    agent = SimpleAgent(
        persistence=True,
        checkpoint_mode="async"
    )
    print(agent.checkpointer)
    compiled_graph = agent.compile()
    print(agent.runnable_config["configurable"])
    logger.info("SimpleAgent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SimpleAgent: {e}")
    agent = None

app = FastAPI(title="PostgreSQL Agent Test API", version="1.0.0")

sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="simple_agent",
            description="Simple agent for CopilotKit integration.",
            graph=compiled_graph,
        ),
    ],
)

add_fastapi_endpoint(app, sdk, "/api/copilotkit")

class HealthResponse(BaseModel):
    status: str
    message: str

# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {"message": "PostgreSQL Agent Test API", "status": "running"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    agent_status = "initialized" if agent is not None else "failed"
    return HealthResponse(
        status="healthy", 
        message=f"API is running, Agent status: {agent_status}"
    )

@app.post("/react-agent/generate")
async def generate(request):
    """Generate endpoint"""
    print(request)
    result = agent.run({"messages": [HumanMessage(content=request)]})
    print("****************", agent.runnable_config["configurable"])
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
