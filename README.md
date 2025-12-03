# Cycling Trip Planner AI Agent

## Project Contents

```
cycling-trip-planner/
│   └── src/
│       ├── agent/             # Agent orchestration + Claude integration
│       ├── api/               # FastAPI endpoints
│       ├── models/            # Pydantic data models
│       └── tools/             # Tool implementations (5 tools)
│
├── Tests
│   ├── test_api.py            # API endpoint tests
│   └── test_tools.py          # Tool tests
│
└── Configuration
    ├── requirements.txt       # Python dependencies
    ├── .env.example          # Configuration template
    ├── pytest.ini            # Test configuration
    └── .gitignore            # Git ignore rules
```

## Architecture Overview

```
User Message → FastAPI → Agent → Claude API
                            ↓
                        Tool System
                            ↓
                    get_route, find_accommodation,
                    get_weather, get_elevation, etc.
                            ↓
                      Response with
                    tool results integrated
```

The agent autonomously decides which tools to use based on the conversation!


## Getting Started

### 1. Install Dependencies
```bash
cd cycling-trip-planner
pip install -r requirements.txt
```

### 2. Set Your API Key
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Run It!
```bash
python main.py
# Visit http://localhost:8000/docs for interactive API
```
### Run Tests
```bash
pytest -v
```

## Available Tools

The agent can use these 5 tools automatically:

1. **get_route** - Calculate distances and waypoints
2. **find_accommodation** - Search for camping, hostels, hotels
3. **get_weather** - Get typical weather for planning
4. **get_elevation_profile** - Understand terrain difficulty
5. **get_points_of_interest** - Discover attractions

## Key Features

- **Conversational Planning**: Natural language interface
- **Agentic Tool Use**: Claude decides which tools to use
- **Session Management**: Maintains context across messages
- **Type Safety**: Full Pydantic validation
- **Production Ready**: Clean architecture, comprehensive tests

### Development
```bash
python main.py
```

### Short-term Improvements Checklist
- [ ] Add authentication (JWT)
- [ ] User storage and RAG
- [ ] Replace in-memory sessions with Redis
- [ ] Add real API integrations
    - [ ] Integration with bike rental services
    - [ ] Real-time weather updates
- [ ] Rate limiting
- [ ] Add request/response logging
- [ ] Implement a simple UI/chat interface

### Long-term
- [ ] Multi-language support
- [ ] Social features (share trips)
- [ ] ML-based route recommendations

```bash
python main.py
```