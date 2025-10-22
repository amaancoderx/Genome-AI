"""
Simple startup script for Market Genome
No reload, production mode
"""
import uvicorn
from config import settings

if __name__ == "__main__":
    print("=" * 60)
    print("PIXARO MARKET GENOME")
    print("=" * 60)
    print(f"\nStarting server on http://127.0.0.1:{settings.api_port}")
    print(f"Open in browser: http://127.0.0.1:{settings.api_port}/")
    print(f"API docs: http://127.0.0.1:{settings.api_port}/docs")
    print("\nPress CTRL+C to stop\n")
    print("=" * 60)

    uvicorn.run(
        "market_genome_main:app",
        host="127.0.0.1",  # localhost only
        port=settings.api_port,
        reload=False,  # Disable reload for stability
        log_level="info"
    )
