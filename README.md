# AWS Strands Agents: Building and Connecting Your First Model Context Protocol (MCP) Server

## Overview

**Deploy an MCP server that searches for stock photography based on your current location and conditions using third-party APIs, and orchestrate it with Strands Agents and the Amazon Q Developer CLI.**

The Model Context Protocol (MCP) provides a standardized interface that enables AI agents to interact seamlessly with external services. In this post, we’ll demonstrate how to build an MCP server that integrates with Shutterstock — my favorite platform for high-quality licensed images, videos, music, and creative tools — using their robust API. We’ll then show how to expose these rich media search capabilities to agents developed with Strands Agents, AWS’s code-first framework for building production-ready AI agents. By orchestrating multiple agents, we’ll enable them to access the National Weather Service (NWS) API, intelligently select contextually relevant photos based on current weather conditions, and deliver results that showcase the power of reasoning and context-aware automation.

JavaScript MCP Servers are based on [https://github.com/lucianoayres/mcp-server-node](https://github.com/lucianoayres/mcp-server-node).

## Prerequisites

```bash
npm install -g corepack # if using yarn

git clone https://github.com/garystafford/aws-strands-agents-mcp-demo.git
cd aws-strands-agents-mcp-demo

yarn install
```

## Installation

1. **Start MCP Agents**

```bash
# terminal window 1: STDIO transport
# environment variables are set by MCP server with STDIO
export API_KEY=abc-1234567890
export SHUTTERSTOCK_API_TOKEN=<YOUR_SHUTTERSTOCK_API_TOKEN>
node mcp-server.js

# terminal window 2: Streamable HTTP transport
# environmental variables are set by agent with Streamable HTTP
node mcp-server-remote.js
```

2. **Install Strands Agents**

```bash
python -m pip install virtualenv -Uqqq
python -m venv .venv
source .venv/bin/activate

python -m pip install pip -Uqqq
python -m pip install -r requirements.txt -Uqqq
```

3. **Start Strands Agents**

```bash
export API_KEY=abc-1234567890
export SHUTTERSTOCK_API_TOKEN=<YOUR_SHUTTERSTOCK_API_TOKEN>

python agent_stdio_multi_agent.py
```
