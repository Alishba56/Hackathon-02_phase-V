"""
Dapr HTTP Client Wrapper
Purpose: Provide a simple interface for publishing events via Dapr Pub/Sub API
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

class DaprClient:
    """
    Dapr HTTP client for event publishing and state management.

    Communicates with Dapr sidecar via localhost:3500 (default Dapr HTTP port).
    """

    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize Dapr client.

        Args:
            dapr_http_port: Dapr sidecar HTTP port (default: 3500)
        """
        self.base_url = f"http://localhost:{dapr_http_port}"
        self.pubsub_name = "kafka-pubsub"

    def publish_event(
        self,
        topic: str,
        event_type: str,
        data: Dict[str, Any],
        source: str = "backend",
        trace_id: Optional[str] = None
    ) -> bool:
        """
        Publish event to Kafka topic via Dapr Pub/Sub.

        Args:
            topic: Kafka topic name (e.g., "task-events", "task-updates", "reminders")
            event_type: CloudEvents type (e.g., "com.todo.task.created")
            data: Event payload data
            source: Event source identifier
            trace_id: Optional trace ID for distributed tracing

        Returns:
            True if event published successfully, False otherwise
        """
        event_id = str(uuid4())

        # CloudEvents 1.0 format
        cloud_event = {
            "specversion": "1.0",
            "type": event_type,
            "source": source,
            "id": event_id,
            "time": datetime.utcnow().isoformat() + "Z",
            "datacontenttype": "application/json",
            "data": data
        }

        url = f"{self.base_url}/v1.0/publish/{self.pubsub_name}/{topic}"

        headers = {
            "Content-Type": "application/json"
        }

        # Add trace context if provided
        if trace_id:
            headers["traceparent"] = f"00-{trace_id}-{event_id[:16]}-01"

        try:
            logger.info(
                f"Publishing event to topic '{topic}'",
                extra={
                    "event_id": event_id,
                    "event_type": event_type,
                    "topic": topic,
                    "trace_id": trace_id
                }
            )

            response = requests.post(
                url,
                json=cloud_event,
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                logger.info(
                    f"Event published successfully",
                    extra={
                        "event_id": event_id,
                        "topic": topic,
                        "status_code": response.status_code
                    }
                )
                return True
            else:
                logger.error(
                    f"Failed to publish event",
                    extra={
                        "event_id": event_id,
                        "topic": topic,
                        "status_code": response.status_code,
                        "response": response.text
                    }
                )
                return False

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error publishing event to Dapr",
                extra={
                    "event_id": event_id,
                    "topic": topic,
                    "error": str(e)
                },
                exc_info=True
            )
            return False

    def get_state(self, store_name: str, key: str) -> Optional[Dict[str, Any]]:
        """
        Get state from Dapr state store.

        Args:
            store_name: State store component name (e.g., "statestore")
            key: State key

        Returns:
            State value as dictionary, or None if not found
        """
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"

        try:
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 204:
                # No content - key doesn't exist
                return None
            else:
                logger.error(
                    f"Failed to get state",
                    extra={
                        "store_name": store_name,
                        "key": key,
                        "status_code": response.status_code
                    }
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error getting state from Dapr",
                extra={
                    "store_name": store_name,
                    "key": key,
                    "error": str(e)
                },
                exc_info=True
            )
            return None

    def save_state(
        self,
        store_name: str,
        key: str,
        value: Dict[str, Any]
    ) -> bool:
        """
        Save state to Dapr state store.

        Args:
            store_name: State store component name (e.g., "statestore")
            key: State key
            value: State value as dictionary

        Returns:
            True if state saved successfully, False otherwise
        """
        url = f"{self.base_url}/v1.0/state/{store_name}"

        state_data = [
            {
                "key": key,
                "value": value
            }
        ]

        try:
            response = requests.post(
                url,
                json=state_data,
                timeout=5
            )

            if response.status_code == 204:
                logger.info(
                    f"State saved successfully",
                    extra={
                        "store_name": store_name,
                        "key": key
                    }
                )
                return True
            else:
                logger.error(
                    f"Failed to save state",
                    extra={
                        "store_name": store_name,
                        "key": key,
                        "status_code": response.status_code
                    }
                )
                return False

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error saving state to Dapr",
                extra={
                    "store_name": store_name,
                    "key": key,
                    "error": str(e)
                },
                exc_info=True
            )
            return False

    def get_secret(self, secret_store: str, secret_key: str) -> Optional[str]:
        """
        Get secret from Dapr secrets store.

        Args:
            secret_store: Secret store component name (e.g., "kubernetes-secrets")
            secret_key: Secret key

        Returns:
            Secret value as string, or None if not found
        """
        url = f"{self.base_url}/v1.0/secrets/{secret_store}/{secret_key}"

        try:
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                secret_data = response.json()
                return secret_data.get(secret_key)
            else:
                logger.error(
                    f"Failed to get secret",
                    extra={
                        "secret_store": secret_store,
                        "secret_key": secret_key,
                        "status_code": response.status_code
                    }
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error getting secret from Dapr",
                extra={
                    "secret_store": secret_store,
                    "secret_key": secret_key,
                    "error": str(e)
                },
                exc_info=True
            )
            return None
