#!/usr/bin/env python3
"""
Hermes ACP Network Bridge (SSE/HTTP)
Exposes the internal ACP Agent over the network for peer-to-peer orchestration.
Uses the battle-hardened Hybrid Bridge logic to ensure protocol compatibility.
"""

import os
import sys
import json
import uuid
import logging
import asyncio
import collections
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Dynamic imports for dependencies
try:
    import acp
    from acp_adapter.server import HermesACPAgent
    from acp_adapter.session import SessionManager
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import Response, StreamingResponse
    from starlette.routing import Route
    import uvicorn
except ImportError:
    print("Error: Missing dependencies. Install with: pip install -e '.[acp]' starlette uvicorn")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("hermes.acp_bridge")

# Global instances
agent = HermesACPAgent()
sessions: Dict[str, Any] = {}

async def handle_sse(request: Request):
    """Handle SSE connection for ACP clients."""
    session_id = str(uuid.uuid4())
    logger.info(f"New ACP SSE session started: {session_id}")
    
    async def event_generator():
        # Step 1: Send endpoint URL back to client (required for some ACP clients)
        endpoint_url = f"{request.base_url}message/{session_id}"
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        
        # Step 2: Keep-alive loop or event listener (simplified for now)
        while True:
            await asyncio.sleep(15)
            yield ":\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def handle_message(request: Request):
    """Bridge synchronous POST requests to the internal ACP Agent."""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        req_id = body.get("id")

        logger.debug(f"ACP Bridge: {method} (id={req_id})")

        # 1. Initialize Fast-Path
        if method == "initialize":
            res_payload = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocol_version": 1,
                    "agent_info": {"name": "hermes-agent-mesh", "version": "0.10.0"},
                    "agent_capabilities": {"load_session": True}
                }
            }
            return Response(json.dumps(res_payload), media_type="application/json")

        # 2. Forward other methods to the Agent
        # Note: In a full implementation, we would route to agent.prompt(), etc.
        # For this bridge, we wrap the prompt call specifically.
        
        if method == "prompt":
            session_id = params.get("session_id")
            prompt_data = params.get("prompt", [])
            
            # Run the agent prompt
            result = await agent.prompt(prompt_data, session_id)
            
            res_payload = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "stop_reason": result.stop_reason,
                    "usage": result.usage.dict() if result.usage else None
                }
            }
            return Response(json.dumps(res_payload), media_type="application/json")

        # Fallback for unhandled methods
        return Response(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}), 
                        media_type="application/json", status_code=404)

    except Exception as e:
        logger.exception("ACP Bridge failure")
        return Response(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}), 
                        media_type="application/json", status_code=500)

app = Starlette(
    routes=[
        Route("/sse", handle_sse, methods=["GET"]),
        Route("/message/{session_id}", handle_message, methods=["POST"]),
        Route("/", handle_message, methods=["POST"]), # Standard JSON-RPC path
    ]
)

def serve_acp(host="0.0.0.0", port=8643):
    """Run the ACP Network Bridge."""
    logger.info(f"Starting Hermes ACP Mesh Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    import fire
    fire.Fire(serve_acp)
