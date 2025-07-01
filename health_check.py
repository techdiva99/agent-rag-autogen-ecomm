#!/usr/bin/env python3
"""
Health Check Service for CMS Data Agent

Simple HTTP endpoint for monitoring agent health in containerized environments.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from cms_agent import create_cms_agent
from agent_integration import RAGDataManager


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks"""
    
    def __init__(self, *args, **kwargs):
        self.agent = create_cms_agent()
        self.rag_manager = RAGDataManager(self.agent)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            self._handle_health_check()
        elif self.path == "/status":
            self._handle_status()
        elif self.path == "/metrics":
            self._handle_metrics()
        else:
            self._send_response(404, {"error": "Not found"})
    
    def _handle_health_check(self):
        """Basic health check"""
        try:
            # Quick validation
            validation = self.agent.validate_data()
            
            if validation.get('valid', False):
                self._send_response(200, {
                    "status": "healthy",
                    "timestamp": time.time(),
                    "records": validation.get('record_count', 0)
                })
            else:
                self._send_response(503, {
                    "status": "unhealthy",
                    "error": validation.get('error', 'Data validation failed'),
                    "timestamp": time.time()
                })
        
        except Exception as e:
            self._send_response(503, {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            })
    
    def _handle_status(self):
        """Detailed status information"""
        try:
            status = self.agent.get_status()
            validation = self.agent.validate_data()
            
            response = {
                "agent_status": status,
                "data_validation": validation,
                "timestamp": time.time()
            }
            
            self._send_response(200, response)
        
        except Exception as e:
            self._send_response(500, {
                "error": str(e),
                "timestamp": time.time()
            })
    
    def _handle_metrics(self):
        """Prometheus-style metrics"""
        try:
            status = self.agent.get_status()
            validation = self.agent.validate_data()
            
            metrics = f"""# HELP cms_data_records Total number of CMS records
# TYPE cms_data_records gauge
cms_data_records {status['current_record_count']}

# HELP cms_data_age_hours Age of data in hours
# TYPE cms_data_age_hours gauge
cms_data_age_hours {status['data_age_hours']}

# HELP cms_data_valid Data validation status (1=valid, 0=invalid)
# TYPE cms_data_valid gauge
cms_data_valid {1 if validation.get('valid', False) else 0}

# HELP cms_data_file_size_mb Size of data file in MB
# TYPE cms_data_file_size_mb gauge
cms_data_file_size_mb {validation.get('file_size_mb', 0)}
"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(metrics.encode())
        
        except Exception as e:
            self._send_response(500, {"error": str(e)})
    
    def _send_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def start_health_server(port=8080):
    """Start the health check server"""
    server = HTTPServer(('', port), HealthCheckHandler)
    print(f"Health check server running on port {port}")
    print(f"Endpoints: /health, /status, /metrics")
    server.serve_forever()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_health_server(port)
