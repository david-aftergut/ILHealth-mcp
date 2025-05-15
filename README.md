# Israel Health Data MCP Server

MCP server providing access to Israeli Ministry of Health data dashboard APIs.</br>
See [Israeli Health Ministry Dashboard](https://datadashboard.health.gov.il/portal/dashboard/health).

## Description

This project provides a FastMCP server that interfaces with Israel's ministry of health data.
Allowing easy access to information about hospitals' quality of service, surveys and much more.</br>
It serves as a bridge between the MOH API and MCP clients.

## Requirements

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
git clone <repository-url>
cd ILHealth-mcp
uv venv
.venv\Scripts\activate
uv pip install -r pyproject.toml
uv lock
```

## Usage

Install and run the server using one of these methods:

1. For use with [Visual Studio Code (using Copilot)](https://code.visualstudio.com/download):</br>
Go to [vscode/mcp.json](/.vscode/mcp.json) and replace {YOUR-LOCAL-PATH} with the path you cloned the repo.</br>
VSCode should discover you server automatically.</br>
If that doesn't work, make sure you enabled MCP & MCP.Discovery in [vscode://settings/mcp](vscode://settings/mcp).</br>
Make sure to enable agent mode in your vscode copilot.</br>
![Agent Mode Enabled](AgentModeEnabled.png)

2. For use with [Claude AI Assistant](https://claude.ai):
```bash
fastmcp install server.py
```

3. For testing with MCP Inspector (Learn how at [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)):
```bash
fastmcp dev server.py
```

## Available health subjects
The following subjects are available:
- Medical Services
- Health Services Quality
- War Casualties
- Child Checkup
- Child Development
- Beaches
- Health Funds (Insurance)

## NCP Tools

### get_available_subjects
Get a list of all available subject areas with descriptions.

### get_metadata
Get metadata about available data endpoints for a specific subject.

### get_data 
Get specific data from an endpoint.

### get_links
Get relevant links and documentation for a subject area.



## Contributing

We welcome contributions to help improve the Israel Health Data MCP server.</br>
Whether you want to add new tools, enhance existing functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see the [Model Context Protocol servers repository](https://github.com/modelcontextprotocol/servers).

## License

MIT License

See the [LICENSE](LICENSE) file for details.
