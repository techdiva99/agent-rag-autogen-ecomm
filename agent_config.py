#!/usr/bin/env python3
"""
Agent Deployment Configuration

Configuration for deploying the CMS Data Agent in different environments
and integration with Agent-RAG-AutoGen workflows.
"""

import os
import json
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class AgentConfig:
    """Configuration for CMS Data Agent deployment"""
    
    # Basic configuration
    output_dir: str = "cms_data"
    check_interval_hours: int = 24
    auto_update: bool = True
    max_retries: int = 3
    
    # RAG configuration
    embedding_model: str = "text-embedding-ada-002"
    vector_db_type: str = "chromadb"  # chromadb, pinecone, weaviate
    vector_db_config: Dict[str, Any] = None
    
    # Monitoring configuration
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_metrics: bool = False
    metrics_endpoint: str = None
    
    # AutoGen integration
    agent_name: str = "cms_data_agent"
    enable_autogen: bool = True
    enable_langchain: bool = False
    
    # Data validation
    enable_validation: bool = True
    validation_rules: Dict[str, Any] = None
    
    # Notification settings
    enable_notifications: bool = False
    notification_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.vector_db_config is None:
            self.vector_db_config = self._default_vector_config()
        
        if self.validation_rules is None:
            self.validation_rules = self._default_validation_rules()
        
        if self.notification_config is None:
            self.notification_config = self._default_notification_config()
    
    def _default_vector_config(self) -> Dict[str, Any]:
        """Default vector database configuration"""
        return {
            "chromadb": {
                "path": "./chroma_db",
                "collection_name": "cms_providers"
            },
            "pinecone": {
                "api_key": os.getenv("PINECONE_API_KEY"),
                "environment": os.getenv("PINECONE_ENV", "us-west1-gcp"),
                "index_name": "cms-providers"
            }
        }
    
    def _default_validation_rules(self) -> Dict[str, Any]:
        """Default data validation rules"""
        return {
            "min_records": 10000,
            "required_fields": [
                "cms_certification_number_ccn",
                "hhcahps_survey_summary_star_rating"
            ],
            "valid_ratings": ["1", "2", "3", "4", "5", ""],
            "max_file_age_hours": 48
        }
    
    def _default_notification_config(self) -> Dict[str, Any]:
        """Default notification configuration"""
        return {
            "email": {
                "enabled": False,
                "smtp_server": os.getenv("SMTP_SERVER"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "username": os.getenv("SMTP_USERNAME"),
                "password": os.getenv("SMTP_PASSWORD"),
                "recipients": []
            },
            "slack": {
                "enabled": False,
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL")
            },
            "webhook": {
                "enabled": False,
                "url": os.getenv("NOTIFICATION_WEBHOOK_URL")
            }
        }
    
    def save_config(self, filepath: str):
        """Save configuration to file"""
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load_config(cls, filepath: str) -> 'AgentConfig':
        """Load configuration from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)


# Environment-specific configurations
def get_development_config() -> AgentConfig:
    """Configuration for development environment"""
    return AgentConfig(
        output_dir="./dev_data",
        check_interval_hours=1,  # Check every hour in dev
        auto_update=True,
        enable_logging=True,
        log_level="DEBUG",
        enable_validation=True,
        enable_notifications=False
    )


def get_production_config() -> AgentConfig:
    """Configuration for production environment"""
    return AgentConfig(
        output_dir="/data/cms_data",
        check_interval_hours=6,  # Check every 6 hours in prod
        auto_update=True,
        enable_logging=True,
        log_level="INFO",
        enable_metrics=True,
        enable_validation=True,
        enable_notifications=True,
        metrics_endpoint=os.getenv("METRICS_ENDPOINT")
    )


def get_testing_config() -> AgentConfig:
    """Configuration for testing environment"""
    return AgentConfig(
        output_dir="./test_data",
        check_interval_hours=0.1,  # Check every 6 minutes for testing
        auto_update=False,  # Manual control in testing
        enable_logging=True,
        log_level="DEBUG",
        enable_validation=True,
        enable_notifications=False
    )


# Docker deployment configuration
DOCKER_CONFIG = {
    "image": "cms-data-agent:latest",
    "environment": {
        "CMS_AGENT_ENV": "production",
        "CMS_OUTPUT_DIR": "/data/cms_data",
        "CMS_CHECK_INTERVAL": "6",
        "CMS_AUTO_UPDATE": "true",
        "CMS_LOG_LEVEL": "INFO"
    },
    "volumes": [
        "/data/cms_data:/data/cms_data",
        "/logs:/app/logs"
    ],
    "ports": [
        "8080:8080"  # For health check endpoint
    ]
}

# Kubernetes deployment configuration
KUBERNETES_CONFIG = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": "cms-data-agent",
        "labels": {"app": "cms-data-agent"}
    },
    "spec": {
        "replicas": 1,
        "selector": {"matchLabels": {"app": "cms-data-agent"}},
        "template": {
            "metadata": {"labels": {"app": "cms-data-agent"}},
            "spec": {
                "containers": [{
                    "name": "cms-data-agent",
                    "image": "cms-data-agent:latest",
                    "env": [
                        {"name": "CMS_AGENT_ENV", "value": "production"},
                        {"name": "CMS_OUTPUT_DIR", "value": "/data/cms_data"},
                        {"name": "CMS_CHECK_INTERVAL", "value": "6"}
                    ],
                    "volumeMounts": [{
                        "name": "data-volume",
                        "mountPath": "/data"
                    }],
                    "resources": {
                        "requests": {"memory": "256Mi", "cpu": "100m"},
                        "limits": {"memory": "512Mi", "cpu": "500m"}
                    }
                }],
                "volumes": [{
                    "name": "data-volume",
                    "persistentVolumeClaim": {"claimName": "cms-data-pvc"}
                }]
            }
        }
    }
}


def create_deployment_files():
    """Create deployment configuration files"""
    
    # Create config files for different environments
    configs = {
        "development": get_development_config(),
        "production": get_production_config(),
        "testing": get_testing_config()
    }
    
    os.makedirs("deploy/config", exist_ok=True)
    
    for env, config in configs.items():
        config.save_config(f"deploy/config/{env}.json")
    
    # Create Docker files
    os.makedirs("deploy/docker", exist_ok=True)
    
    with open("deploy/docker/docker-compose.yml", "w") as f:
        f.write("""version: '3.8'
services:
  cms-data-agent:
    build: .
    environment:
      - CMS_AGENT_ENV=production
      - CMS_OUTPUT_DIR=/data/cms_data
      - CMS_CHECK_INTERVAL=6
      - CMS_AUTO_UPDATE=true
    volumes:
      - ./data:/data/cms_data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
""")
    
    # Create Dockerfile
    with open("deploy/docker/Dockerfile", "w") as f:
        f.write("""FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY *.py ./
COPY cms_data/ ./cms_data/

# Create data directory
RUN mkdir -p /data/cms_data

# Health check endpoint
COPY deploy/health_check.py ./

# Start the agent
CMD ["python", "cms_agent.py", "--run-scheduler"]

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD python health_check.py
""")
    
    # Create Kubernetes manifests
    os.makedirs("deploy/k8s", exist_ok=True)
    
    with open("deploy/k8s/deployment.yaml", "w") as f:
        json.dump(KUBERNETES_CONFIG, f, indent=2)
    
    print("✅ Deployment files created in deploy/ directory")


if __name__ == "__main__":
    create_deployment_files()
