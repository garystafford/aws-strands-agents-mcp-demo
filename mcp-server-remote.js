// This is a Model Context Protocol (MCP) server running on Node.js using the Streamable HTTP transport without session management.
// This server provides several tools that can be used to interact with the server, including image search on Shutterstock.
// Reference: https://github.com/modelcontextprotocol/typescript-sdk?tab=readme-ov-file#without-session-management-stateless
//
// Author: Gary Stafford
// Date: 2025-05-31

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import sstk from "shutterstock-api";
import { z } from "zod";
import process from "node:process";


const app = express();
app.use(express.json());

app.post("/mcp", async (req, res) => {
    try {
        const server = new McpServer({
            name: "Shutterstock Image Search MCP Server - Stateless Streamable HTTP Transport",
            description: "This server provides tools for image search and other functionalities using the Model Context Protocol.",
            version: "1.0.0",
        });
        const transport = new StreamableHTTPServerTransport({
            sessionIdGenerator: undefined,
        });
        res.on("close", () => {
            process.stderr.write("Request closed\n");
            transport.close();
            server.close();
        });

        // Simple tool without parameters
        server.tool(
            "echo",
            "Echo back the input text.",
            { text: z.string() },
            async ({ text }) => ({
                content: [{ type: "text", text }],
            }));

        // Tool with optional parameters
        server.tool(
            "greet",
            "Greet a person with a customizable greeting. Both name and greeting are optional.",
            {
                name: z.string().optional(),
                greeting: z.string().optional(),
            },
            async ({ name = "World", greeting = "Hello" }) => ({
                content: [{ type: "text", text: `${greeting}, ${name}!` }],
            })
        );

        // Tool with multiple parameters
        server.tool(
            "calculate_area",
            "Calculate the area of a rectangle given its length and width.",
            {
                length: z.number(),
                width: z.number(),
            },
            async ({ length, width }) => ({
                content: [
                    {
                        type: "text",
                        text: `The area of the rectangle is ${length * width} square units.`,
                    },
                ],
            })
        );

        // Tool to get value from environment variable
        if (!process.env.API_KEY) {
            throw new Error("API_KEY environment variable is not set.");
        }
        server.tool(
            "get_api_key",
            "Retrieve the API key stored in the environment variable.",
            {},
            async ({ }) => ({
                content: [{ type: "text", text: process.env.API_KEY }],
            }));

        // Tool to search for images on Shutterstock
        if (!process.env.SHUTTERSTOCK_API_TOKEN) {
            throw new Error("SHUTTERSTOCK_API_TOKEN environment variable is not set.");
        }
        server.tool(
            "search_shutterstock",
            "Search for images on Shutterstock. Specify the search term and optional image type and orientation.",
            { term: z.string(), image_type: z.string().optional(), orientation: z.string().optional() },
            async ({ term, image_type, orientation }) => {
                const result = await searchShutterstock(term, image_type, orientation);
                return {
                    content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
                };
            }
        );

        await server.connect(transport);
        await transport.handleRequest(req, res, req.body);
    } catch (error) {
        process.stderr.write(`Error handling MCP request: ${error}\n`);
        if (!res.headersSent) {
            res.status(500).json({
                jsonrpc: "2.0",
                error: {
                    code: -32603,
                    message: "Internal server error",
                },
                id: null,
            });
        }
    }
});

app.get("/mcp", async (req, res) => {
    process.stderr.write("Received GET MCP request\n");
    res.writeHead(405).end(JSON.stringify({
        jsonrpc: "2.0",
        error: {
            code: -32000,
            message: "Method not allowed."
        },
        id: null
    }));
});

async function searchShutterstock(term, image_type = "photo", orientation = "vertical") {
    /**
    * Search for images on Shutterstock.
    * @param {string} term - The search term.
    * @param {string} [image_type="photo"] - The type of image to search for.
    * @param {string} [orientation="vertical"] - The orientation of the image.
    * @returns {Promise<string>} - The search results.
    */
    try {
        sstk.setAccessToken(process.env.SHUTTERSTOCK_API_TOKEN);

        const imagesApi = new sstk.ImagesApi();

        const queryParams = {
            "query": term, // Search term
            "image_type": [image_type], // Image type (e.g., photo, vector, illustration)
            "orientation": orientation, // Orientation (e.g., horizontal, vertical)
            "per_page": 5, // Limit results to 5 images
            "page": 1, // Start from the first page
            "sort": "popular", // Sort by popularity
        };

        const response = await imagesApi.searchImages(queryParams);

        if (response && response.data) {
            return JSON.stringify(response.data, null, 2);
        } else {
            return "No results found";
        }
    } catch (error) {
        process.stderr.write(`Shutterstock API error: ${error}\n`);
        return `Error searching for "${term}": ${error.message}`;
    }
}

const PORT = 3000;
app.listen(PORT, () => {
    process.stderr.write(`MCP Stateless Streamable HTTP Server listening on port ${PORT}...\n`);
});
