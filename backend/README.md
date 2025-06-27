# AI Wave Optimization Agent - Backend

This directory contains the Python backend for the AI Wave Optimization Agent, providing constraint programming optimization for mid-market warehouse workflows.

## Features

- **Constraint Programming Optimization**: Uses Google OR-Tools CP-SAT solver
- **Synthetic Data Generation**: Creates realistic warehouse scenarios with embedded inefficiencies
- **REST API**: FastAPI-based endpoints for optimization and data generation
- **Real-time Streaming**: Live optimization progress updates
- **Multiple Scenarios**: Bottleneck, deadline pressure, and inefficient workflow demos

## Quick Start

### Prerequisites

- Python 3.11+ (tested with Python 3.13)
- C++ Build Tools (for OR-Tools compilation)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
# Option 1: Using uvicorn directly
cd backend
uvicorn api.main:app --reload

# Option 2: Using the startup script
cd backend
python start_server.py
```

### API Endpoints

The server will be available at `http://127.0.0.1:8000`

- **GET /** - API information and available endpoints
- **GET /health** - Health check
- **GET /scenarios** - List available demo scenarios
- **POST /optimize** - Run optimization with custom input
- **GET /optimize/scenario/{scenario_type}** - Run optimization with demo scenario
- **GET /optimize/stream/{scenario_type}** - Stream optimization progress
- **GET /generate/data** - Generate synthetic warehouse data

### API Documentation

- Interactive API docs: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Demo Scenarios

1. **Bottleneck** - Equipment bottleneck with too many orders requiring packing stations
2. **Deadline** - High-priority orders with tight shipping deadlines
3. **Inefficient** - Suboptimal worker assignments and equipment utilization

## Testing

Run the test suite:
```bash
cd backend
python test_optimization.py
```

Run the demo script:
```bash
cd backend
python demo.py
```

## Project Structure

```
backend/
├── api/
│   ├── main.py              # FastAPI application and endpoints
│   └── __init__.py
├── models/
│   ├── warehouse.py         # Data models for warehouse entities
│   ├── optimization.py      # Optimization result models
│   └── __init__.py
├── optimizer/
│   ├── wave_optimizer.py    # Core constraint programming optimizer
│   └── __init__.py
├── data_generator/
│   ├── generator.py         # Synthetic data generation
│   └── __init__.py
├── test_optimization.py     # Test suite
├── demo.py                  # Demo script
├── start_server.py          # Server startup script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Optimization Engine

The core optimization engine uses Google OR-Tools CP-SAT solver to optimize:

- **Worker Assignments**: Optimal worker-to-stage assignments based on skills
- **Equipment Utilization**: Efficient use of packing stations, dock doors, etc.
- **Stage Sequencing**: Proper precedence constraints between workflow stages
- **Deadline Compliance**: Minimize shipping deadline violations
- **Cost Optimization**: Balance labor costs with equipment efficiency

## Performance

- **Optimization Time**: 10-second time limit (configurable)
- **Problem Size**: Handles 100+ orders with 15+ workers and 40+ equipment items
- **Efficiency Gains**: Targets 15-20% improvement over baseline workflows 