# AWS Strands Agents: Building and Connecting Your First Model Context Protocol (MCP) Server

## Overview

**Learn to build an MCP server that searches for stock photography based on your current weather conditions using third-party APIs, and connect it to Strands Agents.**

The Model Context Protocol (MCP) enables AI agents to interact with external services in a standardized way. In this post, we'll build an MCP server that connects to Shutterstock's API to search for photos and then expose those capabilities to agents built with Strands Agents - a code-first framework from AWS for building production-ready AI agents. Using multi-agent orchestration, these agents will leverage the National Weather Service (NWS) API to find appropriate photos for you based on your current weather conditions.

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
