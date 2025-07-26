#!/usr/bin/env python3
"""
MCP Server runner for ZoteroDB Analyzer.

This script creates a proper MCP server that can be connected to by LLM agents.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zoterodb_analyzer.mcp_server import ZoteroMCPServer
from zoterodb_analyzer.auth_config import ZOTERO_LIBRARY_ID, ZOTERO_API_KEY


class MCPServerRunner:
    """Runs the ZoteroDB Analyzer MCP server with proper MCP protocol."""

    def __init__(self):
        # Get credentials from environment
        library_id = os.getenv('ZOTERO_LIBRARY_ID')
        api_key = os.getenv('ZOTERO_API_KEY')
        library_type = os.getenv('ZOTERO_LIBRARY_TYPE', 'user')
        if ZOTERO_LIBRARY_ID:
            library_id = ZOTERO_LIBRARY_ID
        if ZOTERO_API_KEY:
            api_key = ZOTERO_API_KEY

        self.server = ZoteroMCPServer(
            default_library_id=library_id,
            default_library_type=library_type,
            default_api_key=api_key
        )

    async def handle_request(self, request: dict) -> dict:
        """Handle incoming MCP requests."""
        method = request.get('method')
        params = request.get('params', {})

        if method == 'tools/list':
            tools = await self.server.list_tools()
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {"tools": tools}
            }

        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})

            result = await self.server.call_tool(tool_name, arguments)

            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            }

        elif method == 'initialize':
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "zoterodb-analyzer",
                        "version": "0.1.0"
                    }
                }
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    async def run_stdio(self):
        """Run the MCP server using stdio transport."""
        print("ZoteroDB Analyzer MCP Server starting...", file=sys.stderr)

        while True:
            try:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                request = json.loads(line.strip())
                response = await self.handle_request(request)

                # Write response to stdout
                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {e}"
                    }
                }
                print(json.dumps(error_response), flush=True)

            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {e}"
                    }
                }
                print(json.dumps(error_response), flush=True)


async def main():
    """Main entry point."""
    runner = MCPServerRunner()
    await runner.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
