#!/usr/bin/env python3
import http.server
import socketserver
import argparse

def run_server(port=8000, bind="0.0.0.0"):
    """Run a simple HTTP server that can be accessed from other machines."""
    # Change to the website directory
    import os
    from pathlib import Path
    os.chdir(Path(__file__).parent)
    
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer((bind, port), handler) as httpd:
        print(f"Server running at http://{bind}:{port}/")
        print("To access from other machines, use your computer's IP address")
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on (default: 8000)")
    parser.add_argument("--bind", default="0.0.0.0", help="Address to bind to (default: 0.0.0.0)")
    
    args = parser.parse_args()
    run_server(args.port, args.bind)