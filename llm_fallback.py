import os
from typing import Optional

from config_loader import load_config


class LLMFallback:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.cfg = load_config()
        llm_def = self.cfg.get("llm_defaults", {})
        self.provider = (provider or os.environ.get("LLM_PROVIDER") or llm_def.get("provider", "ollama")).lower()
        if model:
            self.model = model
        elif self.provider == "openai":
            self.model = llm_def.get("openai_model", "gpt-3.5-turbo")
        else:
            self.model = llm_def.get("ollama_model", "llama2")

        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass
        self.api_key = os.getenv("OPENAI_API_KEY", "")

        prompt_path = self.cfg["paths"].get("llm_system_prompt_file")
        if prompt_path and os.path.isfile(prompt_path):
            with open(prompt_path, encoding="utf-8") as f:
                self._system_prompt_base = f.read().strip()
        else:
            self._system_prompt_base = "You are a helpful assistant."

        self._llm = self.cfg.get("llm", {})

    def get_response(self, query, context=None):
        system_prompt = self._system_prompt_base
        if context:
            system_prompt += f"\n\nPrevious conversation context: {context}"

        if self.provider == "openai":
            return self._get_openai_response(query, system_prompt)
        if self.provider == "ollama":
            return self._get_ollama_response(query, system_prompt)
        return "I apologize, but I'm having trouble processing your query. Please try rephrasing your question."

    def _get_openai_response(self, query, system_prompt):
        try:
            from openai import OpenAI

            if not self.api_key:
                return "OpenAI API key not found. Please set OPENAI_API_KEY environment variable or use Ollama instead."

            client = OpenAI(api_key=self.api_key)
            max_tokens = int(self._llm.get("max_tokens", 200))
            temperature = float(self._llm.get("temperature", 0.7))

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content.strip()

        except ImportError:
            return "OpenAI library not installed. Install it with: pip install openai"
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please check your API key and connection."

    def _get_ollama_response(self, query, system_prompt):
        try:
            import requests

            base = self._llm.get("ollama_base_url", "http://localhost:11434").rstrip("/")
            path = self._llm.get("ollama_generate_path", "/api/generate")
            url = base + path
            timeout = int(self._llm.get("request_timeout_seconds", 30))
            payload = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\nUser: {query}\n\nAssistant:",
                "stream": False,
            }

            response = requests.post(url, json=payload, timeout=timeout)

            if response.status_code == 200:
                return response.json().get("response", "I couldn't generate a response. Please try again.")
            return "Ollama server not accessible. Make sure Ollama is running on localhost:11434"

        except ImportError:
            return "Requests library not installed. Install it with: pip install requests"
        except requests.exceptions.ConnectionError:
            return "Cannot connect to Ollama. Please make sure Ollama is running locally."
        except Exception as e:
            return f"I encountered an error: {str(e)}"

    def is_available(self):
        if self.provider == "openai":
            return bool(self.api_key)
        if self.provider == "ollama":
            try:
                import requests

                base = self._llm.get("ollama_base_url", "http://localhost:11434").rstrip("/")
                path = self._llm.get("ollama_tags_path", "/api/tags")
                timeout = int(self._llm.get("ollama_health_timeout_seconds", 5))
                response = requests.get(base + path, timeout=timeout)
                return response.status_code == 200
            except Exception:
                return False
        return False
