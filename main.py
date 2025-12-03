"""Main entry point for the Cycling Trip Planner API."""

if __name__ == "__main__":
    import uvicorn
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Cycling Trip Planner API on {host}:{port}")
    print("API Documentation available at: http://localhost:8000/docs")
    
    # Use import string for proper reload support
    uvicorn.run(
        "src.api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )