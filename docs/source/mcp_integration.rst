MCP Integration
===============

.. currentmodule:: haive.dataflow.mcp

The **Model Context Protocol (MCP) Integration** represents a revolutionary advancement in AI interoperability - providing **standardized communication**, **universal tool discovery**, **resource federation**, and **prompt orchestration** that enables AI systems to seamlessly connect, share capabilities, and collaborate across platforms and implementations.

🤖 **The Universal AI Protocol**
---------------------------------

**Transform Isolated AI Systems into a Unified Intelligence Network:**

**Native MCP Server Support**
   Build MCP-compliant servers that expose tools, resources, and prompts with standardized interfaces

**Intelligent Tool Federation**
   Automatically discover and integrate tools from any MCP-compliant source into your AI ecosystem

**Resource Sharing Protocol**
   Share knowledge bases, documents, and data sources across AI systems with unified access patterns

**Prompt Template Exchange**
   Exchange and compose sophisticated prompt templates across different AI implementations

**Cross-Platform Compatibility**
   Connect with Claude, GPT, and any MCP-compliant AI system for true interoperability

Core MCP Technologies
---------------------

MCP Server Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: haive.dataflow.mcp.server
   :members:
   :undoc-members:

**Enterprise-Grade MCP Server**

Build MCP servers that expose your AI capabilities to the broader ecosystem with full protocol compliance.

**Server Features**:
* **Tool Registration**: Expose functions as MCP tools with automatic schema generation
* **Resource Management**: Share data sources with controlled access and versioning
* **Prompt Templates**: Provide reusable prompt templates with parameter validation
* **Transport Support**: stdio, HTTP, and WebSocket transports
* **Authentication**: Built-in auth mechanisms for secure tool access
* **Discovery Service**: Automatic service discovery and capability advertisement

**Quick Start: MCP Server**

.. code-block:: python

   from haive.dataflow.mcp import (
       MCPServer, MCPTool, MCPResource,
       MCPPrompt, Transport
   )

   # Create MCP server
   server = MCPServer(
       name="haive-intelligence-server",
       version="1.0.0",
       description="Advanced AI capabilities via MCP",
       transport=Transport.STDIO  # or HTTP, WebSocket
   )

   # Register tools
   @server.tool(
       name="analyze_sentiment",
       description="Analyze sentiment of text with advanced NLP"
   )
   async def analyze_sentiment(text: str, language: str = "en") -> dict:
       """Perform sentiment analysis on text.
       
       Args:
           text: Text to analyze
           language: Language code (default: en)
           
       Returns:
           Sentiment analysis results with confidence scores
       """
       result = await sentiment_model.analyze(text, language)
       return {
           "sentiment": result.label,
           "confidence": result.confidence,
           "emotions": result.emotions,
           "aspects": result.aspect_sentiments
       }

   # Register resources
   @server.resource(
       name="knowledge_base",
       description="Company knowledge base and documentation"
   )
   async def get_knowledge_base(query: str = None) -> dict:
       """Access knowledge base resources.
       
       Args:
           query: Optional search query
           
       Returns:
           Knowledge base entries
       """
       if query:
           entries = await kb.search(query)
       else:
           entries = await kb.list_recent()
       
       return {
           "entries": entries,
           "total": len(entries),
           "source": "corporate_knowledge_base"
       }

   # Register prompts
   @server.prompt(
       name="code_review",
       description="Comprehensive code review prompt"
   )
   def code_review_prompt(
       code: str,
       language: str,
       focus_areas: List[str] = None
   ) -> str:
       """Generate code review prompt.
       
       Args:
           code: Code to review
           language: Programming language
           focus_areas: Specific areas to focus on
           
       Returns:
           Formatted prompt for code review
       """
       focus = ", ".join(focus_areas) if focus_areas else "general quality"
       
       return f"""
       Please review the following {language} code with focus on {focus}:
       
       ```{language}
       {code}
       ```
       
       Provide feedback on:
       1. Code quality and best practices
       2. Potential bugs or issues
       3. Performance considerations
       4. Security concerns
       5. Suggested improvements
       """

   # Start server
   await server.start()

**Advanced MCP Server Patterns**

.. code-block:: python

   # Advanced MCP server with middleware
   class AdvancedMCPServer:
       """MCP server with advanced features."""
       
       def __init__(self):
           self.server = MCPServer(name="advanced-mcp")
           self.middleware = []
           self.rate_limiter = RateLimiter()
           self.auth_manager = AuthManager()
       
       def add_middleware(self, middleware):
           """Add processing middleware."""
           self.middleware.append(middleware)
       
       async def register_authenticated_tool(self, tool_func, required_scopes):
           """Register tool with authentication."""
           
           @self.server.tool(name=tool_func.__name__)
           @self.auth_manager.require_scopes(required_scopes)
           @self.rate_limiter.limit(calls=100, period="1h")
           async def authenticated_tool(*args, **kwargs):
               # Pre-process through middleware
               for mw in self.middleware:
                   args, kwargs = await mw.pre_process(args, kwargs)
               
               # Execute tool
               result = await tool_func(*args, **kwargs)
               
               # Post-process through middleware
               for mw in reversed(self.middleware):
                   result = await mw.post_process(result)
               
               return result
           
           return authenticated_tool
       
       async def start_with_discovery(self):
           """Start server with service discovery."""
           
           # Register with discovery service
           await self.register_with_discovery({
               "name": self.server.name,
               "version": self.server.version,
               "capabilities": self.get_capabilities(),
               "endpoint": self.server.endpoint
           })
           
           # Start server
           await self.server.start()
           
           # Heartbeat for discovery
           asyncio.create_task(self.heartbeat_loop())

MCP Client Integration
~~~~~~~~~~~~~~~~~~~~~~

**Intelligent MCP Client**

.. code-block:: python

   from haive.dataflow.mcp import (
       MCPClient, ServerDiscovery,
       ToolExecutor, ResourceFetcher
   )

   # Discover available MCP servers
   discovery = ServerDiscovery()
   servers = await discovery.discover_servers(
       filter_capabilities=["sentiment_analysis", "code_review"]
   )

   print(f"Found {len(servers)} MCP servers")

   # Connect to server
   client = MCPClient()
   await client.connect(servers[0].endpoint)

   # List available tools
   tools = await client.list_tools()
   for tool in tools:
       print(f"Tool: {tool.name}")
       print(f"  Description: {tool.description}")
       print(f"  Parameters: {tool.input_schema}")

   # Execute tool
   result = await client.execute_tool(
       "analyze_sentiment",
       {
           "text": "This MCP integration is amazing!",
           "language": "en"
       }
   )

   print(f"Sentiment: {result['sentiment']} ({result['confidence']:.2%})")

   # Fetch resources
   resources = await client.list_resources()
   kb_data = await client.fetch_resource(
       "knowledge_base",
       {"query": "MCP integration guide"}
   )

   # Use prompts
   prompts = await client.list_prompts()
   review_prompt = await client.get_prompt(
       "code_review",
       {
           "code": "def hello(): print('world')",
           "language": "python",
           "focus_areas": ["style", "efficiency"]
       }
   )

**Advanced Client Patterns**

.. code-block:: python

   # Multi-server MCP client
   class MultiServerMCPClient:
       """Client that connects to multiple MCP servers."""
       
       def __init__(self):
           self.servers = {}
           self.tool_registry = {}
           self.load_balancer = LoadBalancer()
       
       async def add_server(self, name: str, endpoint: str):
           """Add MCP server to pool."""
           
           client = MCPClient()
           await client.connect(endpoint)
           
           # Cache server info
           self.servers[name] = {
               "client": client,
               "tools": await client.list_tools(),
               "resources": await client.list_resources(),
               "health": "healthy"
           }
           
           # Update tool registry
           for tool in self.servers[name]["tools"]:
               if tool.name not in self.tool_registry:
                   self.tool_registry[tool.name] = []
               self.tool_registry[tool.name].append(name)
       
       async def execute_tool(self, tool_name: str, params: dict):
           """Execute tool with load balancing."""
           
           if tool_name not in self.tool_registry:
               raise ValueError(f"Tool {tool_name} not found")
           
           # Select server based on load
           available_servers = [
               name for name in self.tool_registry[tool_name]
               if self.servers[name]["health"] == "healthy"
           ]
           
           server_name = self.load_balancer.select(available_servers)
           client = self.servers[server_name]["client"]
           
           try:
               result = await client.execute_tool(tool_name, params)
               self.load_balancer.record_success(server_name)
               return result
           except Exception as e:
               self.load_balancer.record_failure(server_name)
               # Try another server
               if len(available_servers) > 1:
                   return await self.execute_tool(tool_name, params)
               raise

Tool Federation
~~~~~~~~~~~~~~~

**Universal Tool Discovery and Integration**

.. code-block:: python

   from haive.dataflow.mcp import (
       ToolFederation, ToolAdapter,
       SchemaMapper, ToolComposer
   )

   # Create tool federation
   federation = ToolFederation()

   # Add MCP servers to federation
   await federation.add_server("server1", "http://mcp1.example.com")
   await federation.add_server("server2", "http://mcp2.example.com")
   await federation.add_server("claude", "stdio://claude-mcp")

   # Discover all available tools
   all_tools = await federation.discover_all_tools()
   print(f"Total tools available: {len(all_tools)}")

   # Search tools by capability
   nlp_tools = await federation.search_tools(
       capabilities=["text_analysis", "nlp", "language"]
   )

   # Create tool adapter for seamless integration
   adapter = ToolAdapter(federation)

   # Adapt external tool to internal format
   @adapter.wrap_tool("external_translator")
   async def translate_text(text: str, target_lang: str) -> str:
       """Wrapper for external translation tool."""
       # Adapter handles schema mapping and protocol conversion
       pass

   # Compose tools into workflows
   composer = ToolComposer(federation)

   workflow = await composer.compose_workflow([
       ("analyze_sentiment", {"source": "input.text"}),
       ("translate_text", {
           "text": "input.text",
           "target_lang": "es"
       }),
       ("analyze_sentiment", {
           "text": "previous.result",
           "language": "es"
       })
   ])

   # Execute composed workflow
   result = await workflow.execute({
       "input": {"text": "This is amazing!"}
   })

Resource Sharing
~~~~~~~~~~~~~~~~

**Federated Resource Access**

.. code-block:: python

   from haive.dataflow.mcp import (
       ResourceFederation, ResourceIndex,
       AccessControl, CacheManager
   )

   # Create resource federation
   resource_fed = ResourceFederation()

   # Index available resources
   index = ResourceIndex()
   await index.scan_servers(federation.servers)

   print(f"Indexed {len(index.resources)} resources")

   # Search resources
   docs = await index.search_resources(
       query="machine learning",
       resource_types=["document", "knowledge_base"],
       min_relevance=0.7
   )

   # Federated resource access with caching
   cache = CacheManager(max_size="1GB", ttl=3600)

   @cache.cached()
   async def get_resource_with_fallback(resource_id: str):
       """Get resource with fallback servers."""
       
       # Try primary server
       try:
           return await resource_fed.fetch_resource(
               resource_id,
               server="primary"
           )
       except:
           # Fallback to replicas
           replicas = await resource_fed.find_replicas(resource_id)
           for replica in replicas:
               try:
                   return await resource_fed.fetch_resource(
                       resource_id,
                       server=replica.server
                   )
               except:
                   continue
           
           raise ResourceNotFoundError(resource_id)

   # Access controlled resources
   access_control = AccessControl()

   @access_control.require_permission("read:sensitive")
   async def get_sensitive_resource(resource_id: str, user_context: dict):
       """Access sensitive resources with permission check."""
       
       # Verify user permissions
       if not access_control.has_permission(user_context, "read:sensitive"):
           raise PermissionDeniedError()
       
       # Fetch with user context
       return await resource_fed.fetch_resource(
           resource_id,
           context=user_context
       )

Prompt Orchestration
~~~~~~~~~~~~~~~~~~~~

**Advanced Prompt Management**

.. code-block:: python

   from haive.dataflow.mcp import (
       PromptOrchestrator, PromptTemplate,
       PromptComposer, VariableResolver
   )

   # Create prompt orchestrator
   orchestrator = PromptOrchestrator()

   # Register prompt templates
   @orchestrator.template("analysis_chain")
   class AnalysisChainPrompt(PromptTemplate):
       """Multi-stage analysis prompt chain."""
       
       stages = [
           "initial_analysis",
           "deep_dive",
           "synthesis",
           "recommendations"
       ]
       
       def initial_analysis(self, data: dict) -> str:
           return f"""
           Analyze the following data:
           {json.dumps(data, indent=2)}
           
           Provide initial insights and identify areas for deeper analysis.
           """
       
       def deep_dive(self, initial_results: dict, focus_areas: List[str]) -> str:
           return f"""
           Based on initial analysis:
           {initial_results}
           
           Perform deep analysis on: {', '.join(focus_areas)}
           """
       
       def synthesis(self, all_results: List[dict]) -> str:
           return f"""
           Synthesize findings from all analyses:
           {json.dumps(all_results, indent=2)}
           
           Create comprehensive summary.
           """
       
       def recommendations(self, synthesis: dict) -> str:
           return f"""
           Based on synthesis:
           {synthesis}
           
           Provide actionable recommendations.
           """

   # Compose prompts dynamically
   composer = PromptComposer(orchestrator)

   # Create dynamic prompt pipeline
   pipeline = composer.create_pipeline([
       ("gather_context", {"sources": ["knowledge_base", "recent_data"]}),
       ("analysis_chain", {"stages": ["initial_analysis", "deep_dive"]}),
       ("format_output", {"format": "executive_summary"})
   ])

   # Execute prompt pipeline
   result = await pipeline.execute({
       "data": market_data,
       "context": user_context
   })

Advanced MCP Features
---------------------

Protocol Extensions
~~~~~~~~~~~~~~~~~~~

**Custom Protocol Extensions**

.. code-block:: python

   from haive.dataflow.mcp import (
       ProtocolExtension, ExtensionRegistry,
       CustomTransport, MessageHandler
   )

   # Define custom extension
   class StreamingExtension(ProtocolExtension):
       """Add streaming capabilities to MCP."""
       
       name = "streaming"
       version = "1.0.0"
       
       def extend_protocol(self, protocol):
           """Extend MCP protocol with streaming."""
           
           # Add streaming message types
           protocol.add_message_type(
               "stream_start",
               schema={
                   "stream_id": "string",
                   "tool_name": "string",
                   "parameters": "object"
               }
           )
           
           protocol.add_message_type(
               "stream_chunk",
               schema={
                   "stream_id": "string",
                   "chunk": "object",
                   "sequence": "integer"
               }
           )
           
           protocol.add_message_type(
               "stream_end",
               schema={
                   "stream_id": "string",
                   "final": "boolean"
               }
           )
       
       async def handle_streaming_tool(self, tool_name: str, params: dict):
           """Handle streaming tool execution."""
           
           stream_id = str(uuid.uuid4())
           
           # Send stream start
           await self.send_message({
               "type": "stream_start",
               "stream_id": stream_id,
               "tool_name": tool_name,
               "parameters": params
           })
           
           # Stream results
           async for chunk in self.execute_streaming_tool(tool_name, params):
               await self.send_message({
                   "type": "stream_chunk",
                   "stream_id": stream_id,
                   "chunk": chunk,
                   "sequence": chunk.sequence
               })
           
           # Send stream end
           await self.send_message({
               "type": "stream_end",
               "stream_id": stream_id,
               "final": True
           })

   # Register extension
   ExtensionRegistry.register(StreamingExtension())

   # Use extended protocol
   server = MCPServer(
       name="extended-server",
       extensions=["streaming"]
   )

   @server.streaming_tool("live_analysis")
   async def live_analysis(data_stream):
       """Streaming analysis tool."""
       async for data in data_stream:
           analysis = await analyze_chunk(data)
           yield analysis

Cross-Platform Bridge
~~~~~~~~~~~~~~~~~~~~~

**Universal AI Platform Bridge**

.. code-block:: python

   # Bridge between different AI platforms
   class UniversalMCPBridge:
       """Bridge MCP across different AI platforms."""
       
       def __init__(self):
           self.platform_adapters = {
               "openai": OpenAIAdapter(),
               "anthropic": AnthropicAdapter(),
               "google": GoogleAdapter(),
               "custom": CustomPlatformAdapter()
           }
       
       async def expose_platform_as_mcp(self, platform: str, config: dict):
           """Expose platform capabilities via MCP."""
           
           adapter = self.platform_adapters[platform]
           server = MCPServer(name=f"{platform}-bridge")
           
           # Convert platform tools to MCP
           platform_tools = await adapter.get_tools(config)
           for tool in platform_tools:
               mcp_tool = self.convert_to_mcp_tool(tool, adapter)
               server.register_tool(mcp_tool)
           
           # Convert platform resources
           platform_resources = await adapter.get_resources(config)
           for resource in platform_resources:
               mcp_resource = self.convert_to_mcp_resource(resource, adapter)
               server.register_resource(mcp_resource)
           
           return server
       
       def convert_to_mcp_tool(self, platform_tool, adapter):
           """Convert platform-specific tool to MCP tool."""
           
           @tool(name=platform_tool.name)
           async def mcp_tool(**kwargs):
               # Convert parameters
               platform_params = adapter.convert_params(kwargs)
               
               # Execute on platform
               result = await adapter.execute_tool(
                   platform_tool,
                   platform_params
               )
               
               # Convert result
               return adapter.convert_result(result)
           
           return mcp_tool

Security & Governance
~~~~~~~~~~~~~~~~~~~~~

**Enterprise Security for MCP**

.. code-block:: python

   from haive.dataflow.mcp import (
       SecurityManager, AuditLogger,
       PolicyEngine, Encryption
   )

   # Secure MCP implementation
   class SecureMCPServer:
       """MCP server with enterprise security."""
       
       def __init__(self):
           self.security = SecurityManager()
           self.audit = AuditLogger()
           self.policy = PolicyEngine()
           self.encryption = Encryption()
       
       async def secure_tool_execution(self, tool_name: str, params: dict, context: dict):
           """Execute tool with full security."""
           
           # Authenticate request
           auth_result = await self.security.authenticate(context)
           if not auth_result.success:
               await self.audit.log_auth_failure(context)
               raise AuthenticationError()
           
           # Check policies
           policy_result = await self.policy.evaluate(
               action="execute_tool",
               resource=tool_name,
               principal=auth_result.principal,
               context=context
           )
           
           if not policy_result.allowed:
               await self.audit.log_policy_violation(
                   principal=auth_result.principal,
                   action="execute_tool",
                   resource=tool_name
               )
               raise PolicyViolationError()
           
           # Encrypt sensitive params
           encrypted_params = await self.encryption.encrypt_sensitive(
               params,
               sensitivity_rules=self.policy.sensitivity_rules
           )
           
           # Execute with audit trail
           await self.audit.log_tool_execution_start(
               tool=tool_name,
               principal=auth_result.principal,
               params_hash=hash(str(params))
           )
           
           try:
               result = await self.execute_tool(tool_name, encrypted_params)
               
               await self.audit.log_tool_execution_success(
                   tool=tool_name,
                   principal=auth_result.principal
               )
               
               return result
               
           except Exception as e:
               await self.audit.log_tool_execution_failure(
                   tool=tool_name,
                   principal=auth_result.principal,
                   error=str(e)
               )
               raise

Performance Optimization
------------------------

MCP Performance Tuning
~~~~~~~~~~~~~~~~~~~~~~

**High-Performance MCP**

.. code-block:: python

   # Performance optimizations
   class OptimizedMCPServer:
       """Performance-optimized MCP server."""
       
       def __init__(self):
           self.config = MCPConfig(
               # Connection pooling
               connection_pool_size=100,
               connection_timeout=30,
               
               # Message batching
               batch_size=100,
               batch_timeout=100,  # ms
               
               # Caching
               cache_size="1GB",
               cache_ttl=300,
               
               # Compression
               compression="zstd",
               compression_level=3
           )
           
           self.connection_pool = ConnectionPool(self.config)
           self.message_batcher = MessageBatcher(self.config)
           self.cache = ResponseCache(self.config)
       
       async def optimized_tool_execution(self, requests: List[ToolRequest]):
           """Execute multiple tool requests efficiently."""
           
           # Check cache
           cached_results = {}
           uncached_requests = []
           
           for req in requests:
               cache_key = self.cache.generate_key(req)
               if cached := await self.cache.get(cache_key):
                   cached_results[req.id] = cached
               else:
                   uncached_requests.append(req)
           
           # Batch uncached requests
           batches = self.message_batcher.create_batches(uncached_requests)
           
           # Execute batches in parallel
           batch_results = await asyncio.gather(*[
               self.execute_batch(batch) for batch in batches
           ])
           
           # Cache results
           for batch_result in batch_results:
               for req_id, result in batch_result.items():
                   await self.cache.set(
                       self.cache.generate_key_by_id(req_id),
                       result
                   )
           
           # Combine results
           all_results = {**cached_results}
           for batch_result in batch_results:
               all_results.update(batch_result)
           
           return all_results

Performance Metrics
-------------------

**MCP Performance Benchmarks**:

* **Tool Execution**: <50ms average latency
* **Resource Fetch**: <100ms for 1MB resources
* **Discovery Time**: <200ms for 1000 tools
* **Connection Time**: <100ms for initial connection
* **Message Throughput**: 10,000+ messages/second
* **Concurrent Clients**: 1,000+ simultaneous connections

**Federation Metrics**:

* **Tool Federation**: 10,000+ tools across 100 servers
* **Resource Index**: 1M+ resources with sub-second search
* **Cross-Server Latency**: <10ms additional overhead
* **Cache Hit Rate**: 90%+ for common operations
* **Load Balancing**: Even distribution across servers
* **Failover Time**: <1 second for server failure

Enterprise Integration
----------------------

**Production MCP Deployment**

* **High Availability**: Multi-region MCP server deployment
* **Service Mesh**: Istio/Linkerd integration for traffic management
* **Monitoring**: Prometheus metrics and Grafana dashboards
* **Tracing**: Distributed tracing with Jaeger
* **Security**: mTLS, OAuth2, API key authentication
* **Compliance**: Audit logging and policy enforcement

See Also
--------

* :doc:`registry_and_discovery` - Discover MCP-enabled components
* :doc:`streaming_intelligence` - Stream data via MCP
* :doc:`dataflow_architecture` - MCP architectural patterns
* :doc:`api_reference` - Complete MCP API documentation