# Database Setup - AI Wave Optimization Agent

This directory contains the PostgreSQL database setup for the AI Wave Optimization Agent, including schema definition and demo data.

## Overview

The database stores all warehouse optimization data including:
- **Warehouse Configuration**: Workers, equipment, SKUs, and operational parameters
- **Orders**: Customer orders with items, priorities, and deadlines
- **Optimization Results**: Complete optimization runs with schedules and metrics
- **Historical Data**: Past optimization runs for analysis and improvement

## Database Schema

### Core Tables

#### `warehouses`
- Warehouse configuration and operational parameters
- Shift hours, capacity limits, cost parameters

#### `workers`
- Worker information with skills, rates, and efficiency factors
- Links to `worker_skills` for many-to-many skill relationships

#### `equipment`
- Equipment inventory with types, capacity, and costs
- Packing stations, dock doors, pick carts, conveyors, label printers

#### `skus` (Stock Keeping Units)
- Product catalog with 50 SKUs across 5 zones
- Pick/pack times, volume, weight for optimization

#### `customers`
- Customer information for order management

#### `orders`
- Customer orders with priorities and shipping deadlines
- Links to `order_items` for order contents

### Optimization Tables

#### `optimization_runs`
- Records of optimization executions
- Performance metrics and solver status

#### `optimization_order_schedules`
- Optimized schedules for each order
- Links to detailed stage schedules

#### `optimization_stage_schedules`
- Detailed timing for each workflow stage
- Worker and equipment assignments

#### `optimization_worker_schedules`
- Worker utilization and assignment summaries

#### `optimization_equipment_schedules`
- Equipment utilization and assignment summaries

## Demo Data

The demo data includes:

### Warehouse Configuration
- **1 Warehouse**: MidWest Distribution Co (85K sqft, 5 zones)
- **15 Workers**: Mix of multi-skilled, specialized, and mixed-skill workers
- **41 Equipment**: 8 packing stations, 6 dock doors, 20 pick carts, 3 conveyors, 4 label printers
- **50 SKUs**: Electronics, clothing, home, sports, and books across 5 zones
- **10 Customers**: Various business types

### Orders
- **20 Orders**: Mix of high, medium, and low priority
- **High Priority (5)**: 2-4 hour deadlines (deadline pressure scenario)
- **Medium Priority (10)**: 6-10 hour deadlines (bottleneck scenario)
- **Low Priority (5)**: 12-16 hour deadlines (inefficient scenario)

### Embedded Inefficiencies
- **Bottleneck**: 50 orders requiring packing vs 8 packing stations
- **Deadline Pressure**: High-priority orders with tight deadlines
- **Skill Mismatch**: Specialized workers vs multi-skilled requirements

## Setup Instructions

### Prerequisites

1. **PostgreSQL**: Install PostgreSQL 12+ on your system
2. **Python Dependencies**: Install psycopg2 for database connectivity
   ```bash
   pip install psycopg2-binary
   ```

### Quick Setup

1. **Run the setup script**:
   ```bash
   cd database
   python setup.py --password YOUR_POSTGRES_PASSWORD
   ```

2. **Custom configuration**:
   ```bash
   python setup.py \
     --host localhost \
     --port 5432 \
     --user postgres \
     --password YOUR_PASSWORD \
     --database wave_opt
   ```

3. **Skip options** (if needed):
   ```bash
   # Skip schema creation (if already exists)
   python setup.py --password YOUR_PASSWORD --skip-schema
   
   # Skip demo data (schema only)
   python setup.py --password YOUR_PASSWORD --skip-data
   ```

### Manual Setup

1. **Create database**:
   ```sql
   CREATE DATABASE wave_opt;
   ```

2. **Run schema**:
   ```bash
   psql -h localhost -U postgres -d wave_opt -f schema.sql
   ```

3. **Load demo data**:
   ```bash
   psql -h localhost -U postgres -d wave_opt -f demo_data.sql
   ```

## Database Connection

### Environment Variables
Set these in your application:
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/wave_opt
# or individual variables:
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=wave_opt
```

### Connection String Format
```
postgresql://username:password@host:port/database
```

## Schema Features

### Performance Optimizations
- **Indexes**: Created on foreign keys and frequently queried columns
- **Constraints**: Proper foreign key relationships and data validation
- **Triggers**: Automatic `updated_at` timestamp updates

### Data Types
- **Custom ENUMs**: For stage types, skill types, equipment types
- **Timestamps**: All tables include created_at/updated_at
- **Decimal Precision**: Proper precision for monetary and time values

### Relationships
- **Cascade Deletes**: Proper cleanup when parent records are deleted
- **Many-to-Many**: Worker skills and order items use junction tables
- **Hierarchical**: Optimization results link back to source data

## Verification

After setup, verify the database with:

```bash
# Test connection and data counts
python setup.py --password YOUR_PASSWORD --skip-schema --skip-data
```

Expected output:
```
🔍 Testing database connection and data...
   - Warehouses: 1
   - Workers: 15
   - Equipment: 41
   - SKUs: 50
   - Orders: 20
   - Customers: 10
✅ Database connection and queries successful
```

## Integration with Backend

The backend API can be configured to use this database by:

1. **Adding database dependencies** to `backend/requirements.txt`:
   ```
   psycopg2-binary==2.9.7
   sqlalchemy==2.0.23
   alembic==1.12.1
   ```

2. **Creating database models** that map to the schema
3. **Adding database connection** to the FastAPI application
4. **Implementing data access layer** for optimization input/output

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure PostgreSQL is running
2. **Authentication Failed**: Check username/password
3. **Database Not Found**: Run setup script to create database
4. **Permission Denied**: Ensure user has CREATE DATABASE privileges

### PostgreSQL Installation

**Windows**:
- Download from https://www.postgresql.org/download/windows/
- Use default port 5432 and remember the password

**macOS**:
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Next Steps

1. **Backend Integration**: Connect the Python backend to this database
2. **Data Access Layer**: Create ORM models and repository classes
3. **API Enhancement**: Add database-backed endpoints
4. **Frontend Integration**: Connect React dashboard to database data 