# Stockholm Traffic Planner MCP Server

A Model Context Protocol (MCP) server for planning public transport journeys in Stockholm, Sweden. This server provides AI assistants with the ability to search for stops and plan optimal routes using Stockholm's public transport system.

## Features

- **Stop Lookup**: Find stops and stations by name with detailed information
- **Journey Planning**: Plan routes between stops with multiple options
- **Real-time Information**: Uses real-time departure/arrival data when available
- **Smart Filtering**: Exclude walking routes, filter transport types, control walking distances
- **Stockholm Time**: All times converted to local Stockholm timezone
- **Simplified Responses**: Clean, structured data optimized for AI consumption

## Tools Available

### `stop_lookup(name: str)`
Search for stops and stations by name in Stockholm's public transport system.

**Parameters:**
- `name`: Name of the stop/station to search for

**Returns:**
- List of matching stops with IDs, names, coordinates, and match quality

### `plan_journey(origin_id, destination_id, ...)`
Plan a journey between two stops with advanced filtering options.

**Parameters:**
- `origin_id`: Origin stop ID (from stop_lookup)
- `destination_id`: Destination stop ID (from stop_lookup)
- `trips`: Number of alternative routes (default: 3)
- `exclude_walking`: Exclude walking-only routes (default: True)
- `exclude_transport_types`: List of transport types to exclude: ['bus', 'metro', 'train', 'tram', 'ship']
- `departure_time`: Departure time in HH:MM format (default: now)
- `max_walking_distance`: Maximum walking distance in meters (default: 500)

**Returns:**
- Simplified journey information with times, transport types, and transfers

## Installation

### Prerequisites
- Python 3.8+
- uv (recommended) or pip

### Using uv (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-username/stockholm-traffic-mcp.git
cd stockholm-traffic-mcp

# Install dependencies
uv sync

# Run the server
uv run mcp dev server.py
```

### Using pip
```bash
# Clone the repository
git clone https://github.com/your-username/stockholm-traffic-mcp.git
cd stockholm-traffic-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

## Usage Examples

### Basic Journey Planning
```python
# 1. Find origin stop
stops = stop_lookup("Odenplan")
origin_id = stops[0]["id"]  # Get the best match

# 2. Find destination stop
stops = stop_lookup("Slussen")
destination_id = stops[0]["id"]

# 3. Plan journey
journey = plan_journey(origin_id, destination_id)
```

### Advanced Filtering
```python
# Metro and bus only, departing at 2 PM
journey = plan_journey(
    origin_id="9091001000009117",
    destination_id="9091001000009192",
    exclude_transport_types=["train", "tram", "ship"],
    departure_time="14:00",
    max_walking_distance=300
)
```

### Sample Response
```json
{
  "journeys": [
    {
      "duration_minutes": 23,
      "interchanges": 1,
      "legs": [
        {
          "origin": "Stockholm, Odenplan",
          "destination": "Stockholm, T-Centralen",
          "departure_time": "14:05",
          "arrival_time": "14:12",
          "transport_type": "Metro",
          "line": "17",
          "direction": "Skarpnäck"
        },
        {
          "origin": "Stockholm, T-Centralen",
          "destination": "Stockholm, Slussen",
          "departure_time": "14:15",
          "arrival_time": "14:18",
          "transport_type": "Metro",
          "line": "19",
          "direction": "Hagsätra"
        }
      ]
    }
  ]
}
```

## MCP Client Configuration

### Claude Desktop
Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "stockholm-traffic": {
      "command": "uv",
      "args": ["run", "mcp", "dev", "server.py"],
      "cwd": "/path/to/stockholm-traffic-mcp"
    }
  }
}
```

### Other MCP Clients
The server follows the standard MCP protocol and should work with any MCP-compatible client.

## API Reference

This server uses the [SL Journey Planner API](https://www.trafiklab.se/api/our-apis/sl/journey-planner-2/) from Trafiklab.

### Data Sources
- **Stop Lookup**: `/v2/stop-finder` endpoint
- **Journey Planning**: `/v2/trips` endpoint
- **Real-time Data**: Integrated real-time departure/arrival information

### Time Handling
- All API responses are in UTC
- Server automatically converts to Stockholm local time (Europe/Stockholm)
- Handles daylight saving time transitions
- Returns user-friendly HH:MM format

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone and setup
git clone https://github.com/your-username/stockholm-traffic-mcp.git
cd stockholm-traffic-mcp
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run black --check .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Trafiklab](https://www.trafiklab.se/) for providing the Stockholm public transport API
- [SL (Storstockholms Lokaltrafik)](https://sl.se/) for the underlying transport data
- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/your-username/stockholm-traffic-mcp/issues)
- **Discussions**: Join the conversation on [GitHub Discussions](https://github.com/your-username/stockholm-traffic-mcp/discussions)
- **API Issues**: For SL API problems, contact [Trafiklab Support](https://www.trafiklab.se/kontakt)

## Changelog

### v1.0.0
- Initial release
- Stop lookup functionality
- Journey planning with advanced filtering
- Real-time data integration
- Stockholm timezone conversion
- Simplified response format