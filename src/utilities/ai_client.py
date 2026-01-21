"""
AI Client for Brewery Management System
Handles interactions with AI providers (Google Gemini, Anthropic Claude, OpenAI ChatGPT)
"""

import json
import logging
import requests
from typing import Optional, Dict, Any, List

# Import providers (try/except to allow running even if libs missing)
try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

logger = logging.getLogger(__name__)

class AIClient:
    """Client for interacting with multiple AI providers"""
    
    PROVIDERS = {
        "gemini": "Google Gemini",
        "anthropic": "Anthropic Claude",
        "openai": "OpenAI ChatGPT"
    }

    def __init__(self, cache_manager):
        self.cache = cache_manager
        self.provider = "gemini" # Default
        self.api_key = None
        self.client = None
        self.model_name = None
        
        # Load initial config
        self.reload_config()
        
    def reload_config(self):
        """Reload configuration from database"""
        try:
            self.cache.connect()
            
            # 1. Get Provider
            p_record = self.cache.get_record('system_settings', 'ai_provider', 'setting_key')
            self.provider = p_record.get('setting_value', 'gemini') if p_record else 'gemini'
            
            # 2. Get API Key
            k_record = self.cache.get_record('system_settings', 'ai_api_key', 'setting_key')
            self.api_key = k_record.get('setting_value') if k_record else None
            
            # 3. Get Saved Model Name (Optional, auto-detect otherwise)
            m_record = self.cache.get_record('system_settings', 'ai_model', 'setting_key')
            self.model_name = m_record.get('setting_value') if m_record else None
            
            self.cache.close()
            
            if self.api_key:
                self._configure_client()
            else:
                logger.info("AI Client initialized but no API Key found.")
                
        except Exception as e:
            logger.error(f"Failed to load AI config: {e}")
            if self.cache.connection:
                self.cache.close()

    def _configure_client(self):
        """Initialize the specific backend client based on provider"""
        self.client = None
        
        try:
            if self.provider == "gemini":
                if not HAS_GEMINI:
                    raise ImportError("google-genai library not installed")
                
                # Auto-detect best model if not saved
                # Auto-detect best model if not saved, or specific legacy fix
                if not self.model_name or self.model_name in ["gemini-flash-latest", "gemini-1.5-flash", "gemini-1.5-flash-001"]:
                    self.model_name = "gemini-2.5-flash" # Safe default for 2026
                
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Configured Gemini (google-genai) with model: {self.model_name}")
                
            elif self.provider == "anthropic":
                if not HAS_ANTHROPIC:
                    raise ImportError("anthropic library not installed")
                self.client = Anthropic(api_key=self.api_key)
                if not self.model_name:
                    self.model_name = "claude-3-5-sonnet-20241022" # Current best
                logger.info(f"Configured Claude with model: {self.model_name}")
                
            elif self.provider == "openai":
                if not HAS_OPENAI:
                    raise ImportError("openai library not installed")
                self.client = OpenAI(api_key=self.api_key)
                if not self.model_name:
                    self.model_name = "gpt-4o" # Current best
                logger.info(f"Configured OpenAI with model: {self.model_name}")
                
        except Exception as e:
            logger.error(f"Failed to configure {self.provider}: {e}")
            self.client = None

    def save_settings(self, provider: str, api_key: str, model: Optional[str] = None):
        """Save new settings to DB and re-configure"""
        try:
            self.provider = provider
            self.api_key = api_key.strip()
            self.model_name = model

            # Auto-detect model if not provided
            if not self.model_name:
                self.model_name = self._detect_best_model()

            settings_to_save = {
                'ai_provider': self.provider,
                'ai_api_key': self.api_key,
                'ai_model': self.model_name
            }
            
            self.cache.connect()
            for key, value in settings_to_save.items():
                setting_data = {
                    'setting_key': key,
                    'setting_value': value,
                    'sync_status': 'synced'
                }
                existing = self.cache.get_record('system_settings', key, 'setting_key')
                if existing:
                    self.cache.update_record('system_settings', key, setting_data, 'setting_key')
                else:
                    self.cache.insert_record('system_settings', setting_data)
            self.cache.close()
            
            self._configure_client()
            return True
            
        except Exception as e:
            logger.error(f"Error saving AI settings: {e}")
            if self.cache.connection:
                self.cache.close()
            return False

    def _detect_best_model(self) -> str:
        """Smart logic to pick the best model for the given key"""
        # TODO: Implement actual API calls to list_models() here for robust checking
        # For now, return safe, high-quality defaults
        if self.provider == "gemini":
            return "gemini-2.5-flash" 
        elif self.provider == "anthropic":
            return "claude-3-5-sonnet-20241022"
        elif self.provider == "openai":
            return "gpt-4o"
        return "unknown"

    def query(self, user_prompt: str, context: Optional[str] = None) -> str:
        """Send query to the configured provider"""
        if not self.api_key or not self.client:
            return ("⚠️ **AI Not Configured**\n\n"
                    "Click the settings icon or type to setup your AI Provider.\n"
                    "(Supports: Gemini, Claude, OpenAI)")

        system_instruction = (
            "You are an expert Brewery Assistant for the BreweryManager application.\n"
            "Your role is to help the brewer, sales staff, and admin manage the brewery.\n"
            "Keep answers concise, helpful, and professional.\n\n"
        )
        
        full_system_prompt = system_instruction
        if context:
            full_system_prompt += f"CONTEXT:\n{context}\n"
            
        try:
            if self.provider == "gemini":
                # specific call for Google (google-genai SDK)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_system_prompt + "\nUSER: " + user_prompt
                )
                return response.text
                
            elif self.provider == "anthropic":
                # specific call for Claude
                message = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=1024,
                    system=full_system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                return message.content[0].text

            elif self.provider == "openai":
                # specific call for OpenAI
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": full_system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return completion.choices[0].message.content
                
        except Exception as e:
            logger.error(f"AI Query Error ({self.provider}): {e}")
            return f"❌ **Error ({self.provider})**\n\n{str(e)}"
