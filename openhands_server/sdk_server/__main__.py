import argparse

import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run the OpenHands Local FastAPI app")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--no-reload",
        dest="reload",
        default=True,
        action="store_false",
        help="Disable auto-reload (enabled by default for development)",
    )

    args = parser.parse_args()

    print(f"🚀 Starting OpenHands SDK Server on {args.host}:{args.port}")
    print(f"📖 API docs will be available at http://{args.host}:{args.port}/docs")
    print(f"🔄 Auto-reload: {'enabled' if args.reload else 'disabled'}")
    print()

    uvicorn.run(
        "openhands_server.sdk_server.api:api",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
