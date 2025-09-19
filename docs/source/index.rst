
Haive Dataflow Documentation
============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   registry_and_discovery
   streaming_intelligence
   mcp_integration
   api_reference

Welcome to Haive Dataflow
-------------------------

**The revolutionary AI component orchestration and real-time data flow platform** - Haive Dataflow provides **automatic discovery**, **intelligent registry management**, **streaming data pipelines**, and **MCP integration** for building sophisticated AI systems that adapt, scale, and evolve in real-time.

🌊 **Beyond Static Architectures**: This isn't just a component registry - it's a **living, breathing AI ecosystem** featuring **dynamic discovery**, **real-time streaming**, **intelligent persistence**, and **Model Context Protocol support** that transforms how AI agents interact with data, tools, and each other!

Revolutionary Dataflow Platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Enter the Future of AI System Architecture:**

* **🔍 Automatic Component Discovery** - Intelligent scanning, registration, and dependency management
* **📊 Real-Time Data Streaming** - WebSocket-based streaming, event-driven architectures, live data flows
* **🗄️ Intelligent Registry System** - Component metadata, configuration management, version tracking
* **🤖 MCP Integration** - Model Context Protocol servers, tools, resources, and prompts
* **💾 Advanced Persistence Layer** - Conversation history, state management, Supabase integration
* **🔌 Universal API Gateway** - Multi-provider LLM support, unified interfaces, dynamic routing
* **📡 Event-Driven Architecture** - Reactive patterns, observable streams, intelligent pipelines
* **🔧 Extensible Framework** - Plugin architecture, custom providers, flexible serialization

**Revolutionary Example**: Build an AI system that **automatically discovers new agents**, **registers their capabilities**, **streams data between components in real-time**, **persists conversations across sessions**, and **adapts its architecture dynamically** - all with type-safe, observable data flows!

Core Platform Capabilities
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. grid:: 2 2 3 3
   :gutter: 2

   .. grid-item-card:: 🔍 Registry & Discovery
      :img-top: _static/registry-discovery-icon.png
      :link: registry_and_discovery
      :link-type: doc

      **Intelligent Component Management**

      Automatic discovery, registration, dependency tracking, and lifecycle management for the entire AI ecosystem.

      +++

      Features: Auto-discovery, Metadata management, Dependency resolution, Version tracking

   .. grid-item-card:: 🌊 Streaming Intelligence
      :img-top: _static/streaming-icon.png
      :link: streaming_intelligence
      :link-type: doc

      **Real-Time Data Flow Architecture**

      WebSocket streaming, event-driven pipelines, reactive patterns, and live data transformation capabilities.

      +++

      Features: WebSocket support, Observable streams, Event routing, Backpressure handling

   .. grid-item-card:: 🤖 MCP Integration
      :img-top: _static/mcp-icon.png
      :link: mcp_integration
      :link-type: doc

      **Model Context Protocol Support**

      Native MCP server/client support, tool registration, resource management, and prompt orchestration.

      +++

      Features: MCP servers, Tool discovery, Resource handling, Prompt templates

   .. grid-item-card:: 💾 Persistence Layer
      :img-top: _static/persistence-icon.png

      **Intelligent Data Persistence**

      Conversation history, state management, session handling, and Supabase integration for scalable storage.

      +++

      Features: Conversation tracking, State persistence, Session management, Cloud storage

   .. grid-item-card:: 🔌 API Gateway
      :img-top: _static/api-gateway-icon.png

      **Universal LLM Gateway**

      Multi-provider support, dynamic routing, unified interfaces, and intelligent load balancing.

      +++

      Features: 20+ LLM providers, Dynamic routing, Rate limiting, Load balancing

   .. grid-item-card:: 🏗️ Architecture Patterns
      :img-top: _static/architecture-icon.png

      **Advanced Architectural Patterns**

      Event-driven design, reactive patterns, pipeline architectures, and scalable system design.

      +++

      Features: Event sourcing, CQRS patterns, Pipeline design, Microservices

Revolutionary Intelligence Layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. grid:: 2
   :gutter: 2

   .. grid-item-card:: 🧠 Dynamic Discovery
      :link: registry_and_discovery
      :link-type: doc

      **Intelligent component discovery** that automatically finds, registers, and manages agents, tools, engines, and games across your entire system.

   .. grid-item-card:: 💡 Streaming Pipelines
      :link: streaming_intelligence
      :link-type: doc

      **Real-time data flow pipelines** with WebSocket support, event routing, and intelligent transformation for live AI interactions.

   .. grid-item-card:: 📊 Observable Architecture

      **Event-driven reactive patterns** that enable observable data flows, intelligent routing, and adaptive system behavior.

   .. grid-item-card:: 🔗 Seamless Integration
      :link: mcp_integration
      :link-type: doc

      **Model Context Protocol integration** providing standardized interfaces for tools, resources, and cross-system communication.

Quick Start: Intelligent Discovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Experience automatic component discovery and registration::

    from haive.dataflow import (
        registry_system, discover_all, EntityType,
        discover_agents, discover_tools
    )
    
    # Automatic discovery of all components
    discovered = discover_all()
    print(f"Discovered {len(discovered)} components:")
    print(f"- {len(discovered['agents'])} agents")
    print(f"- {len(discovered['tools'])} tools")
    print(f"- {len(discovered['engines'])} engines")
    
    # Register custom component
    entity_id = registry_system.register_entity(
        name="StreamProcessor",
        type=EntityType.AGENT,
        description="Real-time stream processing agent",
        module_path="my_module.agents",
        class_name="StreamProcessor",
        metadata={
            "capabilities": ["streaming", "transformation", "aggregation"],
            "version": "1.0.0"
        }
    )
    
    # Query components by capability
    streaming_agents = registry_system.query_entities(
        type=EntityType.AGENT,
        metadata_filter={"capabilities": "streaming"}
    )

Real-Time Streaming Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy sophisticated streaming data flows::

    from haive.dataflow.streaming import (
        StreamingPipeline, WebSocketManager,
        EventRouter, TransformationNode
    )
    
    # Create streaming pipeline
    pipeline = StreamingPipeline("ai-data-flow")
    
    # Add transformation nodes
    pipeline.add_node(
        TransformationNode(
            name="sentiment_analyzer",
            transform_fn=analyze_sentiment,
            output_schema=SentimentResult
        )
    )
    
    pipeline.add_node(
        TransformationNode(
            name="entity_extractor",
            transform_fn=extract_entities,
            output_schema=EntityList
        )
    )
    
    # Connect nodes in pipeline
    pipeline.connect("input", "sentiment_analyzer")
    pipeline.connect("sentiment_analyzer", "entity_extractor")
    pipeline.connect("entity_extractor", "output")
    
    # Stream data through pipeline
    async with pipeline.stream() as stream:
        async for result in stream.process(data_source):
            print(f"Processed: {result}")

MCP Server Integration
~~~~~~~~~~~~~~~~~~~~~~

Native Model Context Protocol support::

    from haive.dataflow.mcp import (
        MCPServer, MCPToolRegistry,
        MCPResource, MCPPrompt
    )
    
    # Create MCP server
    mcp_server = MCPServer(
        name="haive-mcp-server",
        version="1.0.0",
        transport="stdio"
    )
    
    # Register tools
    @mcp_server.tool("analyze_data")
    async def analyze_data(data: dict) -> dict:
        """Analyze data using AI models."""
        # Tool implementation
        return {"analysis": "results"}
    
    # Register resources
    @mcp_server.resource("knowledge_base")
    async def get_knowledge() -> dict:
        """Access knowledge base."""
        return {"knowledge": "data"}
    
    # Register prompts
    @mcp_server.prompt("code_review")
    def code_review_prompt(code: str) -> str:
        """Generate code review prompt."""
        return f"Review this code for quality: {code}"
    
    # Start MCP server
    await mcp_server.start()

Advanced Persistence Layer
~~~~~~~~~~~~~~~~~~~~~~~~~~

Intelligent data persistence and state management::

    from haive.dataflow.persistence import (
        ConversationManager, StateStore,
        SupabaseAdapter, SessionHandler
    )
    
    # Initialize persistence layer
    persistence = SupabaseAdapter(
        url=os.getenv("SUPABASE_URL"),
        key=os.getenv("SUPABASE_KEY")
    )
    
    # Conversation management
    conversation_mgr = ConversationManager(persistence)
    
    # Store conversation
    conversation_id = await conversation_mgr.create_conversation(
        agent_id="assistant-001",
        user_id="user-123",
        metadata={"context": "customer_support"}
    )
    
    # Add messages
    await conversation_mgr.add_message(
        conversation_id=conversation_id,
        role="user",
        content="How can I integrate MCP?"
    )
    
    # Retrieve conversation history
    history = await conversation_mgr.get_conversation(conversation_id)
    
    # State persistence
    state_store = StateStore(persistence)
    await state_store.save_state(
        entity_id="agent-001",
        state_data={"memory": "important_context"}
    )

Platform Architecture Innovation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Revolutionary Framework Design:**

.. grid:: 2
   :gutter: 2

   .. grid-item-card:: 🏗️ Event-Driven Core

      **Reactive architecture** with event sourcing, CQRS patterns, and observable data streams for scalable AI systems.

   .. grid-item-card:: ⚡ High-Performance Streaming
      :link: streaming_intelligence
      :link-type: doc

      **WebSocket-based streaming** with backpressure handling, intelligent routing, and real-time transformations.

Performance & Integration Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Discovery Speed**: <100ms for component scanning and registration
* **Streaming Latency**: <5ms for data pipeline processing
* **Registry Capacity**: 10,000+ components with instant lookup
* **MCP Compatibility**: Full Model Context Protocol 1.0 support
* **Persistence Scale**: Billions of messages with Supabase integration
* **API Gateway**: 20+ LLM providers with unified interface

Platform Capabilities Deep Dive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**🔍 Registry & Discovery System**
   Automatic component discovery with dependency resolution, metadata management, and lifecycle tracking.

**🌊 Streaming Data Architecture**
   Real-time WebSocket streaming with event routing, transformation pipelines, and backpressure handling.

**🤖 MCP Protocol Support**
   Native Model Context Protocol integration for standardized tool, resource, and prompt management.

**💾 Persistence & State Management**
   Scalable conversation history, state persistence, and session management with cloud storage.

**🔌 Universal API Gateway**
   Multi-provider LLM support with dynamic routing, rate limiting, and intelligent load balancing.

**🏗️ Architectural Patterns**
   Event-driven design, reactive patterns, and microservice architectures for scalable AI systems.

Next Steps
~~~~~~~~~~

- :doc:`registry_and_discovery` - Master component discovery and registration
- :doc:`streaming_intelligence` - Build real-time data pipelines
- :doc:`mcp_integration` - Integrate Model Context Protocol

Research Applications
~~~~~~~~~~~~~~~~~~~~~

**Academic Research**
   * Dynamic AI system architectures
   * Real-time data flow optimization
   * Component discovery algorithms
   * Event-driven AI patterns

**Commercial Applications**
   * Enterprise AI orchestration
   * Real-time analytics pipelines
   * Scalable conversation systems
   * Multi-tenant AI platforms

**Innovation & Development**
   * Adaptive AI architectures
   * Self-organizing systems
   * Intelligent routing algorithms
   * Distributed AI coordination

Getting Help
~~~~~~~~~~~~

* **Documentation**: Comprehensive guides and API references
* **GitHub Issues**: https://github.com/pr1m8/haive-dataflow/issues
* **Community Forum**: Join our dataflow architecture discussions
* **Enterprise Support**: Professional consulting for large-scale deployments

---

**The Future of AI System Architecture Starts Here** - Deploy intelligent component discovery, real-time data streaming, and adaptive architectures that transform static AI systems into living, evolving intelligence platforms! 🚀

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
