"""
entry point for AMA
"""

import os
import sys
import argparse
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import uvicorn
from src.logging_config import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Start the AMA Social Media Agent API"
    )
    parser.add_argument(
        "--host",
        default=os.getenv("API_HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("API_PORT", "8000")),
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development only)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes (default: 4)"
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "info").lower(),
        choices=["critical", "error", "warning", "info", "debug"],
        help="Logging level (default: info)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("Starting AMA Social Media Agent")
    logger.info("=" * 70)
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Reload: {args.reload}")
    logger.info(f"Workers: {args.workers if not args.reload else 1}")
    logger.info(f"Log Level: {args.log_level}")
    logger.info("=" * 70)
    
    uvicorn.run(
        "src.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=1 if args.reload else args.workers,
        log_level=args.log_level,
        access_log=True,
    )


if __name__ == "__main__":
    main()