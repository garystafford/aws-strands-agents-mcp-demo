"""
This script demonstrates how to create a multi-agent orchestration system using Strands Agents and integrate with an MCP server.
It integrates with an external MCP server using STDIO transport protocol to search for images on Shutterstock.com.
It also uses the 'Agents as Tools' architectural pattern to retrieve weather information from the National Weather Service API.
It also uses a Bedrock model for natural language processing and a conversation manager to handle interactions.

Author: Gary Stafford
Date: 2025-06-03
"""

import os
from mcp import stdio_client, StdioServerParameters
from strands import Agent, tool
from strands_tools import http_request, shell
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient

# Create an MCP client that connects to a local MCP server via stdio transport.
# This MCP server is expected to be running a Node.js application that implements the MCP protocol.
API_KEY = os.environ.get("API_KEY")
SHUTTERSTOCK_API_TOKEN = os.environ.get("SHUTTERSTOCK_API_TOKEN")
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set.")
if not SHUTTERSTOCK_API_TOKEN:
    raise ValueError("SHUTTERSTOCK_API_TOKEN environment variable is not set.")

# Update StdioServerParameters to reflect your environment
stdio_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="/usr/local/bin/node",
            args=["/Users/garystaf/Documents/Projects/mcp-server-node/mcp-server.js"],
            env={
                "API_KEY": API_KEY,
                "SHUTTERSTOCK_API_TOKEN": SHUTTERSTOCK_API_TOKEN,
            },
        )
    )
)

# Create a conversation manager to handle the conversation state
# This manager uses a sliding window approach to keep track of the last 10 interactions.
conversation_manager = SlidingWindowConversationManager(
    window_size=20,
)

# Create a Bedrock model instance for natural language processing
bedrock_model = BedrockModel(
    model_config={
        "model_id": "us.amazon.nova-micro-v1:0",
        "max_tokens": 512,
        "temperature": 0.5,
    },
)

# Define a weather-focused system prompt
WEATHER_SYSTEM_PROMPT = """You are a weather assistant with HTTP capabilities. You can:

1. Make HTTP requests to the National Weather Service API
2. Process and display weather forecast data
3. Provide weather information for locations in the United States

When retrieving weather information:
1. Based on the city and state, get the latitude and longitude coordinates.
2. Use those coordinates with the following URL template: https://api.weather.gov/points/{latitude},{longitude}
3. Then use the returned forecast URL to get the actual forecast

When displaying weather responses:
- Provide a single, concise sentence summarizing the actual current weather in that location.
- Do not include numerical details like temperature, wind speed, or humidity.
- Do not include the city or state name in the response; focus on the weather conditions only.
- Do not start with "The weather is" or similar phrases.
- Use natural language to describe the weather, e.g., "It is sunny with a chance of rain later."
- Example responses: "Cloudy with a chance of showers" or "Sunny and the sky is clear"
"""


@tool
def weather_assistant(query: str) -> str:
    """
    A weather assistant tool that retrieves weather information for a given city and state.
    This tool uses the National Weather Service API to get the current weather conditions.
    It processes the user's query to extract the city and state, retrieves the latitude and longitude, and then fetches the weather data.

    Args:
        query: A string containing the user's query about the weather, typically in the format "City, State".

    Returns:
        A string summarizing the current weather conditions in natural language, without numerical details or location names.
        If an error occurs, it returns an error message.
    """
    try:
        # Create an agent with HTTP capabilities
        weather_agent = Agent(system_prompt=WEATHER_SYSTEM_PROMPT, tools=[http_request])

        # Call the agent and return its response
        response = weather_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in weather assistant: {str(e)}"


with stdio_mcp_client:
    # Get the tools from the MCP server
    tools = stdio_mcp_client.list_tools_sync()

    # Define a system prompt for the agent
    MAIN_SYSTEM_PROMPT = (
        "You are a helpful assistant that can use various tools to answer questions. "
        "You can use tools like weather_forecast, search_shutterstock, echo, greet, calculate_area, and get_api_key. "
        "Use the tools to get the weather forecast, find images from Shutterstock, calculate areas, retrieve API keys, and more."
    )

    # Create an agent with these tools
    orchestrator_agent = Agent(
        system_prompt=MAIN_SYSTEM_PROMPT,
        tools=[
            *tools,
            weather_assistant,
            http_request,
            shell,
        ],  # Combine tools from MCP server and local tools
        model=bedrock_model,
        conversation_manager=conversation_manager,
    )

    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    RESET = "\033[0m"

    print(f"\n{BLUE}Strands Agents Demonstration{RESET}")
    print(f"\n{BLUE}Type your request (or 'exit' to quit):{RESET}")

    # Interactive loop
    while True:
        try:
            user_input = input(f"\n{BLUE}> {RESET}")

            if user_input.lower() == "exit" or user_input.lower() == "quit":
                print(f"\n{BLUE}Goodbye! 👋{RESET}")
                break

            # Call the weather agent
            response = orchestrator_agent(user_input)
        except KeyboardInterrupt:
            print(f"\n\n{RED}Execution interrupted. Exiting...{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}An error occurred: {str(e)}{RESET}")
            print(f"{RED}Please try a different request.{RESET}")
