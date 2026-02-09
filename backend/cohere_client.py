"""
Cohere API client wrapper for AI chatbot integration.
Provides a singleton client instance for making Cohere API calls.
"""
import os
from typing import Optional
from dotenv import load_dotenv
import cohere

# Load environment variables
load_dotenv()


class CohereClientWrapper:
    """Wrapper for Cohere API client with configuration management"""

    _instance: Optional[cohere.Client] = None

    @classmethod
    def get_client(cls) -> cohere.Client:
        """
        Get or create Cohere client instance (singleton pattern).

        Returns:
            cohere.Client: Configured Cohere client

        Raises:
            ValueError: If COHERE_API_KEY is not set
        """
        if cls._instance is None:
            api_key = os.getenv("COHERE_API_KEY")
            if not api_key:
                raise ValueError("COHERE_API_KEY environment variable is not set")

            cls._instance = cohere.Client(api_key=api_key)

        return cls._instance

    @classmethod
    def reset_client(cls):
        """Reset the client instance (useful for testing)"""
        cls._instance = None


# Convenience function for getting client
def get_cohere_client() -> cohere.Client:
    """
    Get configured Cohere client instance.

    Returns:
        cohere.Client: Configured Cohere client
    """
    return CohereClientWrapper.get_client()
