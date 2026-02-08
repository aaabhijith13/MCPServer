import sys
from typing import Optional

import requests
from mcp.server.fastmcp import FastMCP

from src.logger import LoggerSingleton


logger = LoggerSingleton(name="mcp_server", log_file="logs/mcp_server.log").get_logger("INFO")


class MCPServer:
    def __init__(self, port: int = 8000):
        self.port = port
        self.mcp: Optional[FastMCP] = None

    def _register_tools(self) -> None:
        if self.mcp is None:
            raise RuntimeError("FastMCP instance not initialized")

        @self.mcp.tool()
        def get_current_weather(city: str) -> str:
            """Get current weather for a city"""
            logger.info(f"Tool called: get_current_weather(city={city})")
            try:
                resp = requests.get(f"https://wttr.in/{city}", timeout=10)
                resp.raise_for_status()
                return resp.text
            except requests.RequestException:
                logger.exception("Error fetching weather data")
                return "Error fetching weather data"

    def start(self) -> FastMCP:
        logger.info(f"Initializing MCP Server (port={self.port})")
        self.mcp = FastMCP(port=self.port)
        self._register_tools()
        return self.mcp


def main() -> int:
    try:
        server = MCPServer(port=8000)
        mcp = server.start()
        logger.info("Starting MCP Server transport=sse")
        mcp.run(transport="sse")
        return 0
    except Exception:
        logger.exception("Server error")
        return 1
    finally:
        logger.info("Server terminated")


if __name__ == "__main__":
    raise SystemExit(main())
