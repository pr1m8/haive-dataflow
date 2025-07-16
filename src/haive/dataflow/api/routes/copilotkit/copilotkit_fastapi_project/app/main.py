# app/main.py
# Main FastAPI + CopilotKit server with rich logging

# CRITICAL: Configure logging BEFORE any haive imports
import logging
import sys

from haive.dataflow.api.routes.copilotkit.copilotkit_fastapi_project.app import logging_config
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
# Immediately silence haive logging before any imports happen
#logging.getLogger("haive").setLevel(logging.CRITICAL)
#logging.getLogger("haive").propagate = False

# More detailed logging setup
from haive.dataflow.api.routes.copilotkit.copilotkit_fastapi_project.app.logging_config import setup_logging
setup_logging(verbose=False)  # Set to True for verbose app logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import uuid
import contextvars
import traceback

# Rich imports for better console output
from rich.console import Console
from rich.traceback import install
from rich import print as rprint

from haive.agents.simple.agent import SimpleAgent
from langchain_core.messages import HumanMessage
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent, CopilotKitContext
from copilotkit.integrations.fastapi import add_fastapi_endpoint

from haive.dataflow.api.routes.copilotkit.copilotkit_fastapi_project.app.logging_setup import setup_logger
from haive.dataflow.api.routes.copilotkit.copilotkit_fastapi_project.app.models import MessagePayload, HealthResponse

# Install rich traceback handler for beautiful error messages
install(show_locals=True, max_frames=10)

# Create rich console for better output
console = Console()

logger = setup_logger("copilotkit")
request_id_var = contextvars.ContextVar("request_id", default="unknown")

# Global variables for agent and graph
agent = None
compiled_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async lifecycle manager to set up agent with async checkpointer."""
    global agent, compiled_graph
    
    console.print("🛠️ [bold blue]Starting async lifecycle setup...[/bold blue]")
    
    try:
        # Import async checkpointer
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        import os
        
        # Get PostgreSQL connection string
        postgres_url = os.getenv(
            "POSTGRES_CONNECTION_STRING",
            "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
        )
        
        console.print(f"🐘 [bold blue]Connecting to PostgreSQL...[/bold blue]")
        
        # Use a direct connection approach to avoid prepared statement conflicts
        import psycopg
        from psycopg.rows import dict_row
        
        console.print("🔧 [bold cyan]Creating PostgreSQL connection...[/bold cyan]")
        
        # Create connection with specific settings to avoid prepared statement issues and JSON auto-conversion
        conn = await psycopg.AsyncConnection.connect(
            postgres_url,
            autocommit=True,
            prepare_threshold=None,  # Completely disable prepared statements
            row_factory=dict_row
        )
        
        # Configure the connection to avoid automatic JSON conversion that conflicts with JsonPlusSerializer
        from psycopg.types import json
        # Disable automatic JSON adaptation that's causing the HumanMessage serialization error
        json.set_json_dumps(None, conn)
        json.set_json_loads(None, conn)
        
        console.print("✅ [bold green]PostgreSQL connection created![/bold green]")
        
        # Create checkpointer with the direct connection and proper serializer
        console.print("🔧 [bold cyan]Creating AsyncPostgresSaver...[/bold cyan]")
        from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
        
        # Use JsonPlusSerializer which handles LangChain objects like HumanMessage
        serializer = JsonPlusSerializer()
        checkpointer = AsyncPostgresSaver(conn, serde=serializer)
        
        try:    
            console.print("🔧 [bold cyan]Setting up checkpointer tables...[/bold cyan]")
            await checkpointer.setup()
            console.print("✅ [bold green]Checkpointer tables set up![/bold green]")
        except Exception as e:
            console.print(f"❌ [bold red]Failed to set up PostgreSQL tables: {e}[/bold red]")
            # If setup fails, continue anyway as tables might already exist
            
        console.print("✅ [bold green]PostgreSQL connection established![/bold green]")
        
        # Create SimpleAgent with async checkpointer
        
      
      
        
        console.print("🔧 [bold cyan]Creating SimpleAgent with auto-built state...[/bold cyan]")
        
        # Create SimpleAgent WITHOUT specifying state_schema - let it auto-generate its own
        agent = SimpleAgent(persistence=False)
        console.print("✅ [bold green]SimpleAgent created with auto-built state![/bold green]")
        
        console.print("🔧 [bold cyan]Setting up agent with JsonPlusSerializer checkpointer...[/bold cyan]")
        # Use the checkpointer with JsonPlusSerializer that handles HumanMessage serialization
        agent.checkpointer = checkpointer
        
        # Use the agent's compile method which includes our JSON schema fix
        compiled_graph = agent.compile()
        console.print("✅ [bold green]Agent compiled with auto-generated state, JSON schema fix, and JsonPlusSerializer![/bold green]")
        
        # Set up CopilotKit endpoint
        setup_copilotkit_endpoint()
        console.print("✅ [bold green]CopilotKit endpoint registered![/bold green]")
        
        yield
        
        # Cleanup
        await conn.close()
        console.print("🧹 [bold yellow]Cleaned up PostgreSQL connection[/bold yellow]")
        
    except Exception as e:
        console.print("❌ [bold red]Failed to set up async lifecycle[/bold red]")
        console.print_exception(show_locals=True, max_frames=10)
        logger.exception("❌ Failed to set up async lifecycle", exc_info=e)
        raise

app = FastAPI(title="PostgreSQL Agent with CopilotKit", version="1.0.0", lifespan=lifespan)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # Allow CopilotKit frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Print startup banner
console.print("\n" + "="*60)
console.print("[bold blue]🤖 CopilotKit FastAPI Server[/bold blue]")
console.print("[dim]PostgreSQL Agent with Rich UI Tracebacks & CORS[/dim]")
console.print("="*60 + "\n")

# CopilotKit setup - will be called after lifespan setup
def setup_copilotkit_endpoint():
    """Set up CopilotKit endpoint after graph compilation."""
    global compiled_graph
    
    if compiled_graph:
        try:
            console.print("🔗 [bold blue]Registering CopilotKit endpoint...[/bold blue]")
            sdk = CopilotKitRemoteEndpoint(agents=[
                LangGraphAgent(
                    name="simple_agent",
                    description="Simple agent for CopilotKit integration.",
                    graph=compiled_graph,
                    langgraph_config=RunnableConfig(
                        configurable={
                            "thread_id": "123"
                        }
                    ),
                    copilotkit_config=CopilotKitContext(
                        frontend_url="http://localhost:3000"
                    )
                )
            ])
            add_fastapi_endpoint(app, sdk, "/api/copilotkit")
            console.print("✅ [bold green]CopilotKit endpoint registered at /api/copilotkit[/bold green]")
            
            # Debug: Check what the LangGraphAgent sees
            console.print(f"🔍 [bold cyan]LangGraphAgent created: {sdk.agents[0]}[/bold cyan]")
            console.print(f"🔍 [bold cyan]LangGraphAgent graph: {sdk.agents[0].graph}[/bold cyan]")
            
            # Try to call get_schema_keys to see what happens
            try:
                test_config = {"configurable": {"thread_id": "test"}}
                console.print(f"🔍 [bold cyan]Testing get_schema_keys with config: {test_config}[/bold cyan]")
                
                # Test the individual methods that get_schema_keys calls
                try:
                    input_schema = sdk.agents[0].graph.get_input_jsonschema()
                    console.print(f"🔍 [bold cyan]get_input_jsonschema result: {input_schema}[/bold cyan]")
                except Exception as input_error:
                    console.print(f"❌ [bold red]get_input_jsonschema error: {input_error}[/bold red]")
                
                try:
                    output_schema = sdk.agents[0].graph.get_output_jsonschema()
                    console.print(f"🔍 [bold cyan]get_output_jsonschema result: {output_schema}[/bold cyan]")
                except Exception as output_error:
                    console.print(f"❌ [bold red]get_output_jsonschema error: {output_error}[/bold red]")
                
                # Now test the actual get_schema_keys method
                schema_result = sdk.agents[0].get_schema_keys(test_config)
                console.print(f"🔍 [bold cyan]get_schema_keys result: {schema_result}[/bold cyan]")
                console.print(f"🔍 [bold cyan]get_schema_keys type: {type(schema_result)}[/bold cyan]")
                
                if schema_result is None:
                    console.print("❌ [bold red]CRITICAL: get_schema_keys returned None - this will cause the TypeError![/bold red]")
                else:
                    console.print("✅ [bold green]get_schema_keys returned a valid result[/bold green]")
                    
            except Exception as schema_error:
                console.print(f"❌ [bold red]Error testing schema methods: {schema_error}[/bold red]")
                console.print_exception(show_locals=True, max_frames=5)
            return True
        except Exception as e:
            console.print("❌ [bold red]Failed to register CopilotKit endpoint[/bold red]")
            console.print_exception(show_locals=True, max_frames=10)
            logger.exception("Failed to register CopilotKit endpoint", exc_info=e)
            return False
    else:
        console.print("⚠️ [bold yellow]No compiled graph available for CopilotKit[/bold yellow]")
        return False

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    start_time = datetime.now()
    
    # Log incoming request with rich console
    console.print(f"➡️ [bold magenta]{request.method}[/bold magenta] {request.url.path} [dim]({request_id[:8]})[/dim]")
    
    logger.info("➡️ Incoming request", extra={
        "request_id": request_id,
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    })
    
    # For POST requests, try to log the body (for debugging)
    request_body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                # Try to decode as JSON for pretty logging
                try:
                    import json
                    request_body = json.loads(body.decode())
                    logger.info("📝 Request body", extra={
                        "request_id": request_id,
                        "body": request_body
                    })
                except (json.JSONDecodeError, UnicodeDecodeError):
                    logger.info("📝 Request body (non-JSON)", extra={
                        "request_id": request_id,
                        "body_length": len(body)
                    })
        except Exception as body_error:
            logger.warning("Failed to read request body", extra={
                "request_id": request_id,
                "error": str(body_error)
            })
    
    # Call the actual endpoint
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds()
    
    # Color-code status codes
    if response.status_code < 400:
        status_color = "green"
        status_icon = "✅"
    else:
        status_color = "red" 
        status_icon = "❌"
    
    console.print(f"⬅️ [{status_color}]{status_icon} {response.status_code}[/{status_color}] ({duration*1000:.1f}ms)")
    
    logger.info("⬅️ Response completed", extra={
        "request_id": request_id,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "response_body": response
    })
    
    return response

@app.get("/", response_model=dict)
async def root():
    return {"message": "PostgreSQL Agent Test API", "status": "running"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    agent_status = "initialized" if agent else "failed"
    return HealthResponse(
        status="healthy",
        message=f"API is running. Agent status: {agent_status}"
    )

@app.post("/simple-agent/generate")
async def generate(payload: MessagePayload):
    if not agent:
        raise HTTPException(status_code=500, detail="Agent is not initialized.")

    start_time = datetime.now()
    request_id = request_id_var.get()
    
    console.print(f"📨 [bold cyan]Received generate request[/bold cyan] [dim]({request_id})[/dim]")
    console.print(f"💬 [yellow]Message:[/yellow] {payload.message}")

    try:
        # Use async run for async checkpointer compatibility
        result = await agent.arun({"messages": [HumanMessage(content=payload.message)]})
        duration = (datetime.now() - start_time).total_seconds()
        
        console.print(f"✅ [bold green]Agent run completed[/bold green] [dim]({duration:.2f}s)[/dim]")
        console.print(f"📤 [blue]Response:[/blue] {str(result)[:200]}...")
        
        logger.info("✅ Agent run completed", extra={
            "request_id": request_id,
            "duration_seconds": duration
        })
        return result
    except Exception as e:
        console.print(f"❌ [bold red]Error during agent run[/bold red] [dim]({request_id})[/dim]")
        console.print_exception(show_locals=True, max_frames=10)
        
        logger.exception("❌ Error during agent run", exc_info=e)
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "request_id": request_id,
                "traceback": traceback.format_exc()
            }
        )

@app.get("/debug/graph")
async def show_graph_config():
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized.")
    return {
        "runnable_config": agent.runnable_config.get("configurable", {}) if agent.runnable_config else {}
    }

# Debug endpoint to see if CopilotKit endpoint is accessible
@app.get("/api/copilotkit/debug")
async def copilotkit_debug():
    """Debug endpoint to check CopilotKit availability."""
    return {
        "status": "CopilotKit endpoint is accessible",
        "agent_available": agent is not None,
        "compiled_graph_available": compiled_graph is not None,
        "timestamp": datetime.now().isoformat()
    }

# Check all registered routes
@app.get("/debug/routes")
async def list_routes():
    """List all registered routes for debugging."""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    return {"routes": routes}

if __name__ == "__main__":
    import uvicorn
    # Note: For proper reload functionality, use the shell script instead
    # This direct run is mainly for testing without reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
