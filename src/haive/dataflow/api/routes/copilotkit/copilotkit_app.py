from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from fastapi import FastAPI
from haive.agents.simple.agent import SimpleAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from contextlib import asynccontextmanager


# Create the FastAPI app
app = FastAPI(
    title="Haive CopilotKit API",
    description="CopilotKit endpoint for Haive agents",
    version="1.0.0"
)

# Create the agent with sync persistence for CopilotKit compatibility
graph = SimpleAgent(
    checkpoint_mode="sync",  # Use sync mode for better CopilotKit compatibility
    persistence=True  # Enable default persistence
)

# Compile the graph - the agent will set up persistence automatically
compiled_graph = graph.compile()

sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="simple_agent",
            description="Simple agent for CopilotKit integration.",
            graph=compiled_graph,
        ),
    ],
)

# Add the CopilotKit endpoint
add_fastapi_endpoint(app, sdk, "/api/copilotkit")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the CopilotKit service."""
    return {"status": "ok", "service": "copilotkit"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)