# AI Wave Optimization Agent

An intelligent constraint programming solution for mid-market warehouse workflow optimization.

## Overview

This system optimizes the entire warehouse workflow from picking through shipping, targeting 15-20% efficiency improvements for mid-market warehouses (85K sqft, 2500 orders/day).

### Key Features

- **Multi-stage Optimization**: Pick → Consolidate → Pack → Label → Stage → Ship
- **Multi-skilled Workforce**: Optimizes worker assignments across all stages
- **Constraint Programming**: Uses Google OR-Tools CP-SAT solver for optimal solutions
- **Real-time Performance**: Solves complex scenarios in <10 seconds
- **Synthetic Dataset**: "MidWest Distribution Co" with embedded inefficiencies

### Architecture

- **Database**: PostgreSQL with synthetic warehouse data
- **Optimization Engine**: Python + OR-Tools constraint programming
- **API**: FastAPI with streaming responses
- **Frontend**: React dashboard (planned)

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and update `.env` file

3. Generate synthetic dataset:
```bash
python -m backend.data_generator
```

4. Run the optimization API:
```bash
uvicorn backend.api.main:app --reload
```

5. Access the API at `http://localhost:8000`

## Core Components

- `backend/optimizer/` - Constraint programming models
- `backend/data_generator/` - Synthetic dataset creation
- `backend/api/` - FastAPI endpoints
- `backend/models/` - Data models and schemas

## Optimization Model

**Decision Variables:**
- `start_time[i]`