# MCPServer

An MCP (Model Context Protocol) server that exposes tools for retrieving real-time and historical stock data, statistics, and metadata using publicly available market data sources (e.g., Yahoo Finance via `yfinance`).

This server is designed to be consumed by MCP-compatible clients such as Claude Desktop, Cursor, or custom MCP clients. It is **not a REST API by default**; tools are invoked through the MCP protocol rather than direct HTTP endpoints.

---

## Overview

This server provides programmatic access to stock market information through structured MCP tools. Each tool represents a function that can be called by an MCP client with typed arguments.

Core capabilities:

- Fetch current stock price  
- Retrieve recent historical price data  
- Get company metadata (sector, industry, market cap, etc.)  
- Retrieve key financial metrics  
- Support structured input via typed parameters  

The server runs locally and communicates over MCP using SSE or Streamable HTTP transport.

---

## Architecture

### Components

| Component | Role |
|------------|------|
| `FastMCP` | Core MCP runtime that registers tools and handles transport |
| `LoggerSingleton` | Centralized logging for all server activity |
| `yfinance` | Data provider for market and company information |
| `requests` | Used for auxiliary HTTP requests if needed |
| MCP Client | External application that calls tools (e.g., Claude Desktop) |

### Execution Flow

1. The server starts and initializes `FastMCP`.
2. Stock tools are registered with the MCP runtime.
3. An MCP client connects using SSE or HTTP transport.
4. The client calls a tool with structured arguments.
5. The server executes the corresponding Python function.
6. Results are returned to the client in structured form.

---

## Installation

### Requirements

- Python 3.10+
- `pip`

### Install dependencies

```bash
pip install fastmcp yfinance requests
```
### Sample Folder Structure
```
your_project/
├──src/
│   └── logger.py
│   ├── main.py
├──logs/
├──dockerfile
├──README.md
├──requirements.txt
```
### Running the Server

## Start the MCP server:
```python
python server.py
```

#### By default, the server runs on:
- http://127.0.0.1:8000


## Transport: SSE
- Logs will be written to:
- logs/mcp_server.log