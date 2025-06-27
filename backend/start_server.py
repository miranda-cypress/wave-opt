#!/usr/bin/env python3
"""
Startup script for the AI Wave Optimization Agent API server.
"""

import uvicorn
import os
import sys

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting AI Wave Optimization Agent API server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API documentation: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 