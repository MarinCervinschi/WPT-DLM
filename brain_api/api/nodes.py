from fastapi import APIRouter, HTTPException, status

from ..repositories.base import NotFoundError
from ..schemas import NodeCreate, NodeListResponse, NodeResponse, NodeUpdate
from .dependencies import NodeServiceDep

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.get(
    "",
    response_model=NodeListResponse,
    summary="List all nodes",
)
def list_nodes(
    service: NodeServiceDep,
    hub_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> NodeListResponse:
    """List all nodes with optional pagination and filtering by hub."""
    return service.list(hub_id=hub_id, skip=skip, limit=limit)


@router.get(
    "/{node_id}",
    response_model=NodeResponse,
    summary="Get a node by ID",
)
def get_node(node_id: str, service: NodeServiceDep) -> NodeResponse:
    """Get a specific node by its ID."""
    try:
        return service.get(node_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "",
    response_model=NodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new node",
)
def create_node(data: NodeCreate, service: NodeServiceDep) -> NodeResponse:
    """Create a new node. The associated hub must exist."""
    try:
        return service.create(data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{node_id}",
    response_model=NodeResponse,
    summary="Update a node",
)
def update_node(
    node_id: str, data: NodeUpdate, service: NodeServiceDep
) -> NodeResponse:
    """Update an existing node."""
    try:
        return service.update(node_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a node",
)
def delete_node(node_id: str, service: NodeServiceDep) -> None:
    """Delete a node by its ID."""
    if not service.delete(node_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found",
        )


@router.post(
    "/{node_id}/maintenance",
    response_model=NodeResponse,
    summary="Set node maintenance mode",
)
def set_maintenance(
    node_id: str,
    maintenance: bool,
    service: NodeServiceDep,
) -> NodeResponse:
    """Enable or disable maintenance mode for a node."""
    try:
        return service.set_maintenance(node_id, maintenance)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
