"""
LLM Fallback Module
Handles fallback to LLM when answer is not found in knowledge base.
Supports OpenAI API and local Ollama.
"""

import os
from typing import Optional


class LLMFallback:
    """Handles LLM fallback responses."""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-3.5-turbo"):
        """
        Initialize LLM fallback.
        
        Args:
            provider: "openai" or "ollama"
            model: Model name (e.g., "gpt-3.5-turbo" or "llama2")
        """
        self.provider = provider.lower()
        self.model = model
        # Try to load from .env file if python-dotenv is available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # python-dotenv not installed, use environment variables only
        self.api_key = os.getenv("OPENAI_API_KEY", "")
    
    def get_response(self, query: str, context: Optional[str] = None) -> str:
        """
        Get LLM response for query.
        
        Args:
            query: User query
            context: Optional context from conversation history
        
        Returns:
            LLM response string
        """
        system_prompt = "You are a college helpdesk assistant. Answer in short and simple language. Be helpful and concise."
        
        if context:
            system_prompt += f"\n\nPrevious conversation context: {context}"
        
        if self.provider == "openai":
            return self._get_openai_response(query, system_prompt)
        elif self.provider == "ollama":
            return self._get_ollama_response(query, system_prompt)
        else:
            return "I apologize, but I'm having trouble processing your query. Please try rephrasing your question."
    
    def _get_openai_response(self, query: str, system_prompt: str) -> str:
        """Get response from OpenAI API."""
        try:
            from openai import OpenAI
            
            if not self.api_key:
                return "OpenAI API key not found. Please set OPENAI_API_KEY environment variable or use Ollama instead."
            
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except ImportError:
            return "OpenAI library not installed. Install it with: pip install openai"
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please check your API key and connection."
    
    def _get_ollama_response(self, query: str, system_prompt: str) -> str:
        """Get response from Ollama (local LLM)."""
        try:
            import requests
            
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\nUser: {query}\n\nAssistant:",
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json().get("response", "I couldn't generate a response. Please try again.")
            else:
                return "Ollama server not accessible. Make sure Ollama is running on localhost:11434"
        
        except ImportError:
            return "Requests library not installed. Install it with: pip install requests"
        except requests.exceptions.ConnectionError:
            return "Cannot connect to Ollama. Please make sure Ollama is running locally."
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if LLM provider is available."""
        if self.provider == "openai":
            return bool(self.api_key)
        elif self.provider == "ollama":
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                return response.status_code == 200
            except:
                return False
        return False
