import io
import logging
from typing import Optional

import qrcode
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/qr")


@router.get(
    "/node/{node_id}",
    summary="Generate Node Charging QR Code",
    description="Generate a QR code for a specific charging node endpoint and download it",
    response_class=StreamingResponse,
)
async def generate_node_qr_code(
    node_id: str,
    base_url: Optional[str] = Query(
        "http://127.0.0.1:8000",
        description="Base URL of the API",
    ),
    size: int = Query(10, ge=1, le=50, description="Size of each box in pixels"),
    download: bool = Query(
        True,
        description="Download the image directly instead of displaying inline",
    ),
) -> StreamingResponse:
    """
    Generate a QR code for a node charging endpoint.

    Args:
        node_id: The ID of the charging node
        base_url: Base URL of the API
        size: Size of each box in pixels
        download: If True, download directly; if False, display inline

    Returns:
        PNG image of the QR code
    """
    try:
        endpoint_url = f"{base_url}/nodes/{node_id}/charge"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )

        qr.add_data(endpoint_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")  # type: ignore
        img_buffer.seek(0)

        logger.info(f"Generated QR code for node {node_id}: {endpoint_url}")

        disposition = "attachment" if download else "inline"
        filename = f"qr_{node_id}.png"

        return StreamingResponse(
            img_buffer,
            media_type="image/png",
            headers={
                "Content-Disposition": f'{disposition}; filename="{filename}"',
                "Cache-Control": "no-cache",
            },
        )

    except Exception as e:
        logger.error(f"Error generating QR code for node {node_id}: {e}")
        raise
