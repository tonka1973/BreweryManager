"""
AI Client for Brewery Management System
Handles interactions with AI providers (e.g. OpenAI/Gemini)
"""

import json
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AIClient:
    """Client for interacting with AI APIs"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
        self.api_key = None
        self.provider = "openai" # or 'gemini'
        self.reload_config()
        
    def reload_config(self):
        """Reload configuration from settings table"""
        try:
            self.cache.connect()
            # We will implement the settings retrieval once the Settings module update is done
            # For now, we'll look for specific keys in system_settings if we were fully implemented
            # or just default to None
            
            # Placeholder for future settings fetch
            # self.api_key = result['ai_api_key'] 
            self.cache.close()
        except Exception as e:
            logger.error(f"Failed to load AI config: {e}")
            if self.cache.connection:
                self.cache.close()

    def query(self, user_prompt: str, context: Optional[str] = None) -> str:
        """
        Send a query to the AI assistant.
        
        Args:
            user_prompt: The user's question
            context: Optional context string (e.g. current screen data)
            
        Returns:
            The plain text response
        """
        if not self.api_key:
            # For now, return a mock response so the UI can be tested
            return (f"**AI Mock Response**\n\n"
                    f"I received your question: '{user_prompt}'\n\n"
                    f"Context provided: {context}\n\n"
                    f"*(Real AI integration will require an API Key to be configured in Settings)*")

        # TODO: Implement actual API call to OpenAI/Gemini here
        return "Thinking..."
