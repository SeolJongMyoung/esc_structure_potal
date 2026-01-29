import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

// Create server instance
const server = new Server(
    {
        name: "civil-engineer-tools",
        version: "1.0.0",
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

// Define tool schemas
const Tools = {
    CALCULATE_BEAM_LOAD: "calculate_beam_load",
};

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: Tools.CALCULATE_BEAM_LOAD,
                description: "Calculate the distributed load on a beam given density and dimensions.",
                inputSchema: zodToJsonSchema(
                    z.object({
                        density: z.number().describe("Density of material (kg/m^3)"),
                        width: z.number().describe("Width of beam (m)"),
                        depth: z.number().describe("Depth of beam (m)"),
                    })
                ),
            },
        ],
    };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    if (name === Tools.CALCULATE_BEAM_LOAD) {
        const { density, width, depth } = args;
        const load = density * width * depth * 9.81; // Load in N/m (Gravity 9.81 m/s^2)

        return {
            content: [
                {
                    type: "text",
                    text: `The distributed load is ${load.toFixed(2)} N/m.`,
                },
            ],
        };
    }

    throw new Error(`Tool not found: ${name}`);
});

// Helper to convert Zod schema to JSON Schema (simplified for this demo)
function zodToJsonSchema(zodObj) {
    // In a real app we might use 'zod-to-json-schema' package, 
    // but here we'll manually construct for simplicity or just generic object.
    // For exact MCP spec, it requires standard JSON Schema.
    // Let's use a simplified manual definition for this demo to avoid extra deps.
    return {
        type: "object",
        properties: {
            density: { type: "number", description: "Density of material (kg/m^3)" },
            width: { type: "number", description: "Width of beam (m)" },
            depth: { type: "number", description: "Depth of beam (m)" }
        },
        required: ["density", "width", "depth"]
    };
}

// Start server
async function run() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Civil Engineer MCP Server running on stdio");
}

run().catch((error) => {
    console.error("Server error:", error);
    process.exit(1);
});
