"""
AI Provider Abstraction Layer
Supports multiple AI providers with automatic fallback:
- Grok (xAI, free, internet-connected, smart)
- Groq (free, fast, internet-connected)
- Ollama (local, free, offline)
"""

import sys
from pathlib import Path
from typing import Optional

import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config


class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass


class GrokProvider:
    """Grok AI Provider (xAI) - Internet-Connected, Smart"""
    
    @staticmethod
    def generate(system_prompt: str, user_prompt: str) -> str:
        """
        Generate text using Grok API (xAI) via OpenAI-compatible client.
        
        Args:
            system_prompt: System instructions for the AI
            user_prompt: User's actual prompt
            
        Returns:
            Generated text response
            
        Raises:
            AIProviderError: If generation fails
        """
        if not Config.GROK_API_KEY:
            raise AIProviderError("GROK_API_KEY not configured. Get one at https://x.ai")
        
        try:
            from openai import OpenAI
        except ImportError:
            raise AIProviderError("OpenAI package not installed. Run: pip install openai")
        
        try:
            # Grok uses OpenAI-compatible API
            client = OpenAI(
                api_key=Config.GROK_API_KEY,
                base_url=Config.GROK_API_BASE
            )
            
            response = client.chat.completions.create(
                model=Config.GROK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=Config.GROK_TEMPERATURE,
                max_tokens=Config.GROK_MAX_TOKENS
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise AIProviderError(f"Grok generation failed: {str(e)}")


class GroqProvider:
    """Groq AI Provider - Free, Fast, Internet-Connected"""
    
    @staticmethod
    def generate(system_prompt: str, user_prompt: str) -> str:
        """
        Generate text using Groq API.
        
        Args:
            system_prompt: System instructions for the AI
            user_prompt: User's actual prompt
            
        Returns:
            Generated text response
            
        Raises:
            AIProviderError: If generation fails
        """
        if not Config.GROQ_API_KEY:
            raise AIProviderError("GROQ_API_KEY not configured. Get one at https://console.groq.com")
        
        try:
            from groq import Groq
            
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            response = client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=Config.GROQ_TEMPERATURE,
                max_tokens=Config.GROQ_MAX_TOKENS
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            raise AIProviderError("Groq package not installed. Run: pip install groq")
        except Exception as e:
            raise AIProviderError(f"Groq generation failed: {e}")


class OllamaProvider:
    """Ollama AI Provider - Local, Free, Offline"""
    
    @staticmethod
    def generate(system_prompt: str, user_prompt: str) -> str:
        """
        Generate text using local Ollama.
        
        Args:
            system_prompt: System instructions for the AI
            user_prompt: User's actual prompt
            
        Returns:
            Generated text response
            
        Raises:
            AIProviderError: If generation fails
        """
        ollama_url = f"{Config.OLLAMA_HOST}/api/generate"
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "keep_alive": "30m",
            "options": {
                "temperature": getattr(Config, "OLLAMA_TEMPERATURE", 0.8),
                "top_p": getattr(Config, "OLLAMA_TOP_P", 0.9),
                "top_k": getattr(Config, "OLLAMA_TOP_K", 40),
                "repeat_penalty": getattr(Config, "OLLAMA_REPEAT_PENALTY", 1.15),
                "num_ctx": min(getattr(Config, "OLLAMA_CONTEXT_TOKENS", 4096), 2048),
                "num_predict": 300,
            },
        }
        
        try:
            response = requests.post(
                ollama_url, 
                json=payload, 
                timeout=Config.OLLAMA_GENERATION_TIMEOUT
            )
            response.raise_for_status()
            
            ollama_response = response.json()
            return ollama_response.get("response", "")
            
        except requests.exceptions.ConnectionError:
            raise AIProviderError(
                f"Cannot connect to Ollama at {Config.OLLAMA_HOST}. "
                "Make sure Ollama is running: ollama serve"
            )
        except Exception as e:
            raise AIProviderError(f"Ollama generation failed: {e}")


def generate_with_ai(system_prompt: str, user_prompt: str, logger=None) -> str:
    """
    Generate text using configured AI provider with automatic fallback.
    
    Args:
        system_prompt: System instructions for the AI
        user_prompt: User's actual prompt
        logger: Optional logger instance for status messages
        
    Returns:
        Generated text response
        
    Raises:
        AIProviderError: If all providers fail
    """
    provider = Config.AI_PROVIDER.lower()
    
    # Define provider order with fallback
    if provider == "grok":
        providers = [
            ("Grok (xAI)", GrokProvider),
            ("Groq (fallback)", GroqProvider),
            ("Ollama (fallback)", OllamaProvider)
        ]
    elif provider == "groq":
        providers = [
            ("Groq", GroqProvider),
            ("Grok (fallback)", GrokProvider),
            ("Ollama (fallback)", OllamaProvider)
        ]
    elif provider == "ollama":
        providers = [
            ("Ollama", OllamaProvider),
            ("Grok (fallback)", GrokProvider),
            ("Groq (fallback)", GroqProvider)
        ]
    else:
        raise AIProviderError(f"Unknown AI provider: {provider}. Use 'grok', 'groq', or 'ollama'")
    
    # Try each provider in order
    last_error = None
    for provider_name, provider_class in providers:
        try:
            if logger:
                logger.info(f"Attempting generation with {provider_name}...")
            
            result = provider_class.generate(system_prompt, user_prompt)
            
            if result and len(result.strip()) > 0:
                if logger:
                    logger.info(f"[SUCCESS] Generated with {provider_name}")
                return result
            else:
                if logger:
                    logger.warning(f"[EMPTY] {provider_name} returned empty response")
                    
        except AIProviderError as e:
            last_error = e
            if logger:
                logger.warning(f"[FAILED] {provider_name} failed: {e}")
            continue
        except Exception as e:
            last_error = e
            if logger:
                logger.warning(f"[ERROR] {provider_name} unexpected error: {e}")
            continue
    
    # All providers failed
    error_msg = f"All AI providers failed. Last error: {last_error}"
    if logger:
        logger.error(error_msg)
    raise AIProviderError(error_msg)


# Convenience functions for direct provider access
def generate_with_grok(system_prompt: str, user_prompt: str) -> str:
    """Direct access to Grok provider"""
    return GrokProvider.generate(system_prompt, user_prompt)


def generate_with_groq(system_prompt: str, user_prompt: str) -> str:
    """Direct access to Groq provider"""
    return GroqProvider.generate(system_prompt, user_prompt)


def generate_with_ollama(system_prompt: str, user_prompt: str) -> str:
    """Direct access to Ollama provider"""
    return OllamaProvider.generate(system_prompt, user_prompt)


if __name__ == "__main__":
    # Test the AI providers
    print("Testing AI Providers...")
    print(f"Current provider: {Config.AI_PROVIDER}")
    print()
    
    test_system = "You are a helpful assistant. Respond in JSON format."
    test_user = 'Say: {"test": "success", "message": "Hello from AI!"}'
    
    try:
        result = generate_with_ai(test_system, test_user)
        print("[SUCCESS] AI Provider Test Successful!")
        print(f"Response: {result[:200]}...")
    except AIProviderError as e:
        print(f"[FAILED] AI Provider Test Failed: {e}")
        print("\nTroubleshooting:")
        print("- For Grok: Set GROK_API_KEY in .env file")
        print("- For Groq: Set GROQ_API_KEY in .env file")
        print("- For Ollama: Make sure Ollama is running (ollama serve)")

