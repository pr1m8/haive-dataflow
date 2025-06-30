# CLAUDE.md - Haive Documentation Navigation Hub

## 🧭 Navigation Guide

This is your main routing file for the Haive codebase. Use this guide to navigate to the appropriate documentation based on your needs.

## 🚀 Quick Start

```bash
# Always use poetry run for all commands
poetry run python -m haive.your_module
poetry run pytest packages/your_package/tests/
```

**Package Location**: `/home/will/Projects/haive/backend/haive/packages/`
**Test Location**: `packages/{package_name}/tests/`

## 📚 Documentation Hierarchy

### 1. **Professional Documentation** (Start Here for APIs & References)

- **Location**: `/docs/source/`
- **Format**: Sphinx RST + MyST Markdown
- **Audience**: End users, API consumers, integrators
- **Content**: API references, user guides, agent showcase

#### Key Sections:

- `/docs/source/agents/` - Agent showcase and architectures
- `/docs/source/api/` - API reference documentation
- `/docs/source/guides/` - User and integration guides
- `/docs/source/reference/` - Legacy reference docs

### 2. **Project Documentation** (Development & Technical Notes)

- **Location**: `/project_docs/`
- **Format**: Markdown
- **Audience**: Developers, contributors
- **Content**: Technical analysis, development logs, project notes

#### Key Sections:

- `/project_docs/documentation_cleanup/` - Documentation standards
- `/project_docs/agent_analysis/` - Agent implementation details
- `/project_docs/logs_and_data/` - Development artifacts

### 3. **Package Documentation** (Module-Specific)

- **Location**: `/packages/{package_name}/README.md`
- **Format**: Standardized Markdown template
- **Audience**: Package users and developers
- **Content**: Package-specific usage, examples, API

## 🎯 Documentation by Purpose

### For Agent Development

1. **Agent Architecture**: `/docs/source/agents/showcase.rst`
2. **Agent Templates**: `/CLAUDE_AGENTS.md`
3. **Agent Analysis**: `/project_docs/agent_analysis/`
4. **Agent Groups**: See "Agent Group Documentation" below

### For API Integration

1. **API Reference**: `/docs/source/api/`
2. **Integration Guide**: `/FRONTEND_INTEGRATION_GUIDE.md`
3. **WebSocket API**: `/docs/source/api/websocket.rst`

### For Testing

1. **Quick Test Guide**: `/QUICK_TEST.md`
2. **Test Examples**: `/test_*.py` files in root
3. **Package Tests**: `/packages/{package_name}/tests/`

### For Database & Persistence

1. **Supabase Setup**: `/SUPABASE_COMPLETE_SETUP.sql`
2. **Migration Guides**: `/migrate_*.py` files
3. **Schema Documentation**: `/docs/source/api/persistence.rst`

## 🏗️ Agent Group Documentation

### Core Agent Groups

#### 1. **Conversational Agents**

- **Docs**: `/CLAUDE_AGENTS_CONVERSATIONAL.md`
- **Examples**: Simple chat, customer service, tutoring
- **Key Packages**: `haive-agents`, `haive-core`

#### 2. **Task Execution Agents**

- **Docs**: `/CLAUDE_AGENTS_TASK.md`
- **Examples**: Code generation, data analysis, automation
- **Key Packages**: `haive-tools`, `haive-dataflow`

#### 3. **Game & Simulation Agents**

- **Docs**: `/CLAUDE_AGENTS_GAMES.md`
- **Examples**: Game playing, environment interaction
- **Key Packages**: `haive-games`

#### 4. **Tool-Using Agents**

- **Docs**: `/CLAUDE_AGENTS_TOOLS.md`
- **Examples**: MCP tools, external APIs
- **Key Packages**: `haive-mcp`, `haive-tools`

## 📋 Documentation Standards

### Document Types & Templates

#### 1. **API Documentation**

- **Template**: `/docs/source/_templates/api_template.rst`
- **Style**: Sphinx RST with Google docstrings
- **Location**: `/docs/source/api/`

#### 2. **Module README**

- **Template**: `/docs/source/_templates/module_readme_template.md`
- **Style**: Markdown with standard sections
- **Location**: `/packages/{package_name}/README.md`

#### 3. **Agent Documentation**

- **Template**: `/CLAUDE_AGENT_TEMPLATE.md`
- **Style**: Markdown with examples and use cases
- **Location**: `/CLAUDE_AGENTS_{GROUP}.md`

#### 4. **Quick Guides**

- **Template**: `/CLAUDE_QUICKGUIDE_TEMPLATE.md`
- **Style**: Action-oriented Markdown
- **Location**: Root directory with descriptive names

### Documentation Conventions

1. **Use poetry run** for all command examples
2. **Include type hints** in all code examples
3. **Follow Google docstring** format
4. **Provide working examples** for all features
5. **Link to related documentation** using relative paths

## 🔍 Finding Information

### By Package

```bash
# View package documentation
cat packages/{package_name}/README.md

# Find package examples
find packages/{package_name} -name "*.py" -type f
```

### By Feature

- **Agents**: Start with `/docs/source/agents/showcase.rst`
- **Tools**: Check `/packages/haive-tools/README.md`
- **Games**: See `/packages/haive-games/README.md`
- **Dataflow**: Read `/packages/haive-dataflow/README.md`

### By Task

- **Setup**: `/docs/source/guides/quickstart.rst`
- **Testing**: `/QUICK_TEST.md`
- **Integration**: `/FRONTEND_INTEGRATION_GUIDE.md`
- **Migration**: `/migrate_*.py` files

## 🛠️ Common Procedures

### Starting a New Agent Project

1. Read `/CLAUDE_AGENTS.md` for agent types
2. Choose appropriate agent group documentation
3. Follow template in `/CLAUDE_AGENT_TEMPLATE.md`
4. Use `poetry run` for all executions

### Running Tests

```bash
# Run all tests for a package
poetry run pytest packages/{package_name}/tests/

# Run specific test file
poetry run pytest packages/{package_name}/tests/test_specific.py

# Run with coverage
poetry run pytest --cov=packages/{package_name} packages/{package_name}/tests/
```

### Building Documentation

```bash
# Build Sphinx docs
cd docs
poetry run make html

# View built docs
open build/html/index.html
```

## 📦 Package Quick Reference

| Package        | Purpose               | Main Docs                            |
| -------------- | --------------------- | ------------------------------------ |
| haive-core     | Core functionality    | `/packages/haive-core/README.md`     |
| haive-agents   | Agent implementations | `/packages/haive-agents/README.md`   |
| haive-tools    | Tool integrations     | `/packages/haive-tools/README.md`    |
| haive-games    | Game environments     | `/packages/haive-games/README.md`    |
| haive-mcp      | MCP protocol support  | `/packages/haive-mcp/README.md`      |
| haive-dataflow | Data processing       | `/packages/haive-dataflow/README.md` |
| haive-prebuilt | Pre-built components  | `/packages/haive-prebuilt/README.md` |

## 🔗 External Resources

- **API Documentation**: `http://localhost:8000/docs` (when running)
- **Sphinx Docs**: `file:///docs/build/html/index.html` (after building)
- **Project Repository**: Check `.git/config` for remote URL

## 🎓 Learning Paths

### For New Developers

1. Start with `/docs/source/guides/quickstart.rst`
2. Read `/QUICK_TEST.md` for testing basics
3. Explore `/packages/haive-core/README.md`
4. Try examples in `/docs/source/agents/showcase.rst`

### For Agent Developers

1. Read `/CLAUDE_AGENTS.md` for overview
2. Choose agent group from documentation above
3. Study examples in `/packages/haive-agents/`
4. Follow patterns in showcase agents

### For Integrators

1. Start with `/FRONTEND_INTEGRATION_GUIDE.md`
2. Review `/docs/source/api/` for endpoints
3. Check WebSocket docs for real-time features
4. Test with examples in root directory

---

**Remember**: Always use `poetry run` for command execution and check package-specific README files for detailed information.
