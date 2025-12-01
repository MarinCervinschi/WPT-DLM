import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.models.mcp import (
    ToolDiscoveryResponse,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ToolExecutionStatus,
    ToolSchema,
)
from app.services.mcp_registry import MCPToolRegistry, get_mcp_registry

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/tools",
    response_model=ToolDiscoveryResponse,
    summary="Discover Available Tools",
    description="List all available MCP tools with their schemas",
)
async def discover_tools(
    mcp_registry: MCPToolRegistry = Depends(get_mcp_registry),
) -> ToolDiscoveryResponse:
    """Discover all available MCP tools."""
    logger.info("Tool discovery requested")
    schemas = mcp_registry.list_tool_schemas()

    return ToolDiscoveryResponse(
        tools=schemas, server_version=settings.VERSION, protocol_version="1.0"
    )


@router.get(
    "/tools/{tool_name}",
    response_model=ToolSchema,
    summary="Get Tool Schema",
    description="Get detailed schema for a specific tool",
)
async def get_tool_schema(
    tool_name: str, mcp_registry: MCPToolRegistry = Depends(get_mcp_registry)
) -> ToolSchema:
    """
    Get schema for a specific tool.

    Args:
        tool_name: Name of the tool

    Returns:
        ToolSchema: Tool schema definition

    Raises:
        HTTPException: If tool not found
    """
    logger.debug(f"Schema requested for tool: {tool_name}")
    tool = mcp_registry.get_tool_schema(tool_name)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_name}' not found",
        )

    return tool


@router.post(
    "/tools/execute",
    response_model=ToolExecutionResponse,
    summary="Execute Tool",
    description="Execute an MCP tool with given parameters",
)
async def execute_tool(
    request: ToolExecutionRequest,
    mcp_registry: MCPToolRegistry = Depends(get_mcp_registry),
) -> ToolExecutionResponse:
    """
    Execute an MCP tool.

    Args:
        request: Tool execution request with parameters

    Returns:
        ToolExecutionResponse: Execution result

    Raises:
        HTTPException: If tool not found or execution fails
    """
    logger.info(f"Executing tool: {request.tool}")
    start_time = time.time()

    try:
        result = await mcp_registry.execute_tool(request.tool, request.parameters)

        execution_time = time.time() - start_time

        return ToolExecutionResponse(
            status=ToolExecutionStatus.SUCCESS,
            tool=request.tool,
            result=result,
            execution_time=execution_time,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time

        return ToolExecutionResponse(
            status=ToolExecutionStatus.ERROR,
            tool=request.tool,
            error=str(e),
            execution_time=execution_time,
        )


@router.get(
    "/health",
    summary="MCP Health Check",
    description="Check MCP service health and registered tools",
)
async def mcp_health(mcp_registry: MCPToolRegistry = Depends(get_mcp_registry)) -> dict:
    """
    MCP service health check.

    Returns:
        dict: Health status with tool count
    """
    tools = mcp_registry.list_tools()

    return {
        "status": "healthy",
        "tools_registered": len(tools),
        "protocol_version": "1.0",
        "server_version": settings.VERSION,
    }
