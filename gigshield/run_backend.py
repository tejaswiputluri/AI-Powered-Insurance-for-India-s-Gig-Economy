#!/usr/bin/env python3
import sys
import os
# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))
import uvicorn
from backend.main import app

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8002, reload=True)