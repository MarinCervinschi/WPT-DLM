import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "edge.gateway.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info",
    )