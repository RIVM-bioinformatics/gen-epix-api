#!/usr/bin/env python3
"""
OAuth 2.0 Server Startup Script

This script starts the OAuth 2.0 authorization server with proper configuration.
It can be run directly or imported as a module.

Usage:
    python start_server.py [--host HOST] [--port PORT] [--debug]

Examples:
    python start_server.py                    # Start on localhost:8080
    python start_server.py --port 9000        # Start on localhost:9000
    python start_server.py --host 0.0.0.0     # Listen on all interfaces
    python start_server.py --debug            # Enable debug mode
"""

import argparse
import logging
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from test.test_client.oauth.server import app

    import uvicorn
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please install required packages:")
    print("  pip install fastapi uvicorn oauthlib PyJWT cryptography")
    sys.exit(1)


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def start_server(
    host: str = "127.0.0.1", port: int = 8080, debug: bool = False, reload: bool = False
) -> None:
    """Start the OAuth 2.0 server."""

    setup_logging(debug)
    logger = logging.getLogger(__name__)

    logger.info("🚀 Starting OAuth 2.0 Authorization Server with OIDC support")
    logger.info(f"📍 Server will be available at: http://{host}:{port}")
    logger.info("📚 API documentation available at: http://{host}:{port}/docs")
    logger.info(
        "🔍 OpenID Connect Discovery: http://{host}:{port}/.well-known/openid-configuration"
    )

    print("\n" + "=" * 60)
    print("🔐 OAuth 2.0 Authorization Server with OIDC Support")
    print("=" * 60)
    print(f"🌐 Server URL: http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs")
    print(f"🔍 Discovery: http://{host}:{port}/.well-known/openid-configuration")
    print(f"🔑 JWKS: http://{host}:{port}/.well-known/jwks.json")
    print("\n📋 Pre-configured Demo Clients:")
    print("   • demo-client / demo-secret (scopes: read, write, openid, profile)")
    print("   • test-client / test-secret (scopes: read, openid)")
    print("\n🧪 Test the server:")
    print("   python demo_client.py")
    print("\n⚡ Available endpoints:")
    print("   POST /oauth/token        - Token endpoint")
    print("   POST /oauth/introspect   - Token introspection")
    print("   GET  /oauth/userinfo     - UserInfo endpoint")
    print("   GET  /health             - Health check")
    print("=" * 60)
    print("Press Ctrl+C to stop the server\n")

    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="debug" if debug else "info",
            reload=reload,
            access_log=True,
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
        print("\n👋 OAuth server stopped. Goodbye!")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="OAuth 2.0 Authorization Server with OIDC support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           Start on localhost:8080
  %(prog)s --port 9000               Start on localhost:9000  
  %(prog)s --host 0.0.0.0            Listen on all interfaces
  %(prog)s --debug                   Enable debug mode
  %(prog)s --reload                  Enable auto-reload for development

Test the server:
  python demo_client.py
        """,
    )

    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--port", type=int, default=8080, help="Port to bind to (default: 8080)"
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    start_server(host=args.host, port=args.port, debug=args.debug, reload=args.reload)


if __name__ == "__main__":
    main()
