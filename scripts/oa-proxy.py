#!/usr/bin/env python3
"""
Simple HTTP proxy for OA Dashboard
Forwards external requests to localhost:8080
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import socket

class ProxyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Forward request to localhost:8080
        self.path = 'http://127.0.0.1:8080' + self.path
        
        try:
            response = urllib.request.urlopen(self.path)
            
            # Copy response headers
            self.send_response(response.status)
            for header, value in response.headers.items():
                if header.lower() == 'transfer-encoding':
                    continue
                self.send_header(header, value)
            self.end_headers()
            
            # Copy response body
            self.wfile.write(response.read())
            
        except Exception as e:
            self.send_error(502, f"Proxy Error: {str(e)}")
    
    def log_message(self, format, *args):
        # Suppress logging
        pass

def run_proxy(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProxyRequestHandler)
    
    print(f"OA Proxy running on port {port}...")
    print(f"Forwarding to: http://127.0.0.1:8080")
    print(f"External access: http://43.134.63.176:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down proxy...")
        httpd.server_close()

if __name__ == '__main__':
    run_proxy(8080)
