#!/usr/bin/env python3
"""Simple development server runner for Cognify."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.simple_main:app",
        host="0.0.0.0",
        port=3001,
        reload=True,
        log_level="info"
    )

