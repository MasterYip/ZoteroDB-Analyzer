#!/usr/bin/env python3
"""
Test client for ZoteroDB Analyzer MCP Server.

This demonstrates how to interact with the MCP server directly.
"""

import asyncio
import json
import os
from pathlib import Path
import sys
from zoterodb_analyzer.mcp_server import ZoteroMCPServer
from zoterodb_analyzer.auth_config import ZOTERO_LIBRARY_ID, ZOTERO_API_KEY


async def test_mcp_server():
    """Test the MCP server functionality directly."""
    print("🔄 Testing ZoteroDB Analyzer MCP Server...")
    
    # Initialize server with environment variables
    library_id = os.getenv('ZOTERO_LIBRARY_ID')
    api_key = os.getenv('ZOTERO_API_KEY')
    if ZOTERO_LIBRARY_ID:
        library_id = ZOTERO_LIBRARY_ID
    if ZOTERO_API_KEY:
        api_key = ZOTERO_API_KEY
    
    if not library_id or not api_key:
        print("❌ Please set ZOTERO_LIBRARY_ID and ZOTERO_API_KEY environment variables")
        return
    
    server = ZoteroMCPServer(
        default_library_id=library_id,
        default_api_key=api_key
    )
    
    try:
        # Test 1: List available tools
        print("\n📋 Test 1: Listing available tools...")
        tools = await server.list_tools()
        print(f"✅ Found {len(tools)} available tools:")
        for tool in tools:
            print(f"   • {tool['name']}: {tool['description']}")
        
        # Test 2: Fetch literature
        print("\n📚 Test 2: Fetching literature...")
        fetch_args = {
            "limit": 10,
            "keywords": ["machine learning", "AI"]
        }
        
        result = await server.call_tool("fetch_literature", fetch_args)
        if result.get("success"):
            print(f"✅ Successfully fetched {result['count']} items")
            if result['count'] > 0:
                sample_item = result['items'][0]
                print(f"   Sample: {sample_item['title']} ({sample_item.get('year', 'No year')})")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        # Test 3: Get collections
        print("\n🗂️  Test 3: Getting collections...")
        collections_result = await server.call_tool("get_collections", {})
        if collections_result.get("success"):
            collections = collections_result['collections']
            print(f"✅ Found {len(collections)} collections:")
            for name, key in list(collections.items())[:5]:  # Show first 5
                print(f"   • {name}")
        else:
            print(f"❌ Error: {collections_result.get('error', 'Unknown error')}")
        
        # Test 4: Search literature
        print("\n🔍 Test 4: Searching literature...")
        search_args = {
            "query": "neural network",
            "limit": 5
        }
        
        search_result = await server.call_tool("search_literature", search_args)
        if search_result.get("success"):
            print(f"✅ Found {search_result['count']} items for '{search_args['query']}'")
            for item in search_result['items'][:3]:  # Show first 3
                print(f"   • {item['title']}")
        else:
            print(f"❌ Error: {search_result.get('error', 'Unknown error')}")
        
        # Test 5: Categorize literature
        print("\n🏷️  Test 5: Categorizing literature...")
        categories = [
            {
                "name": "Machine Learning",
                "description": "Papers on machine learning and AI",
                "keywords": ["machine learning", "neural network", "deep learning", "AI"]
            },
            {
                "name": "Robotics",
                "description": "Papers on robotics and automation",
                "keywords": ["robot", "robotics", "automation", "control"]
            }
        ]
        
        categorize_args = {
            "categories": categories,
            "filter_criteria": {
                "keywords": ["machine learning", "robot"]
            },
            "export_format": "markdown",
            "context_type": "related_works"
        }
        
        categorize_result = await server.call_tool("categorize_literature", categorize_args)
        if categorize_result.get("success"):
            print(f"✅ Successfully categorized {categorize_result['total_items']} items")
            print(f"   Categories created:")
            for name, category in categorize_result['categories'].items():
                print(f"     • {name}: {category['item_count']} items")
            
            if 'llm_context_file' in categorize_result:
                print(f"   📄 LLM context file: {categorize_result['llm_context_file']}")
        else:
            print(f"❌ Error: {categorize_result.get('error', 'Unknown error')}")
        
        print("\n✅ MCP Server testing completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")


async def test_json_rpc_format():
    """Test the server with proper JSON-RPC format."""
    print("\n🔧 Testing JSON-RPC format...")
    
    server = ZoteroMCPServer(
        default_library_id=os.getenv('ZOTERO_LIBRARY_ID'),
        default_api_key=os.getenv('ZOTERO_API_KEY')
    )
    
    # Test initialize request
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    
    # Test tools/list request
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    # Test tools/call request
    call_tool_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "fetch_literature",
            "arguments": {
                "limit": 5,
                "keywords": ["AI"]
            }
        }
    }
    
    print("📤 Example JSON-RPC requests that an agent would send:")
    print(f"   Initialize: {json.dumps(initialize_request, indent=2)}")
    print(f"   List Tools: {json.dumps(list_tools_request, indent=2)}")
    print(f"   Call Tool: {json.dumps(call_tool_request, indent=2)}")


if __name__ == "__main__":
    print("ZoteroDB Analyzer MCP Server Test Client")
    print("=" * 50)
    
    asyncio.run(test_mcp_server())
    asyncio.run(test_json_rpc_format())