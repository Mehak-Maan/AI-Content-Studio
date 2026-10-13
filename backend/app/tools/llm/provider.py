import json
import re
import asyncio
from typing import Dict, Any, Optional
from ...config.settings import settings
from ...utils.logger import logger
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "gemini-3.8-flash"
        self.model = None
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            logger.warning(f"[Gemini] Init failed: {e}")
            self.model = None

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.model:
            raise ValueError("Gemini not configured")
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        loop = asyncio.get_event_loop()
        import google.generativeai as genai
        candidates = [self.model_name, "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]
        last_err = None
        for name in dict.fromkeys(candidates):
            try:
                mod = genai.GenerativeModel(name)
                res = await loop.run_in_executor(None, mod.generate_content, full_prompt)
                return res.text
            except Exception as e:
                last_err = e
                logger.warning(f"[Gemini] {name} failed: {e}")
        raise last_err or ValueError("All Gemini models failed")

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        enhanced = f"{prompt}\n\nReturn ONLY valid JSON. No markdown, no explanation."
        text = await self.generate_text(enhanced, system_prompt)
        return _extract_json(text)


class GroqProvider(LLMProvider):
    """
    Groq LLM Provider — primary LLM engine.
    Uses qwen/qwen3.8-27b (or fallback models) via Groq Cloud API.
    """
    MODELS = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "allam-2-7b"]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        try:
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=self.api_key)
        except Exception as e:
            logger.warning(f"[Groq] Init failed: {e}")

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.client:
            raise ValueError("Groq client not initialized")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_err = None
        for model in self.MODELS:
            try:
                resp = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.75,
                    max_tokens=2048
                )
                return resp.choices[0].message.content or ""
            except Exception as e:
                last_err = e
                logger.warning(f"[Groq] {model} text failed: {e}")
        raise last_err or ValueError("All Groq models failed")

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        sys_msg = (
            (system_prompt or "You are a helpful AI assistant.") +
            "\n\nCRITICAL: Respond with ONLY a valid JSON object. No <think> tags, no markdown code fences, "
            "no explanation text. Start your response with { and end with }."
        )
        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ]

        last_err = None
        for model in self.MODELS:
            try:
                resp = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2048
                )
                content = resp.choices[0].message.content or "{}"
                return _extract_json(content)
            except json.JSONDecodeError as e:
                logger.warning(f"[Groq] {model} JSON parse failed: {e}. Raw: {content[:200]}")
                last_err = e
            except Exception as e:
                last_err = e
                logger.warning(f"[Groq] {model} JSON failed: {e}")
        raise last_err or ValueError("All Groq JSON models failed")


def _extract_json(text: str) -> Dict[str, Any]:
    """Robustly extract JSON from LLM output."""
    text = text.strip()
    # Remove <think>...</think> tags (qwen models)
    text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.DOTALL).strip()
    # Try extracting from markdown code block
    m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if m:
        text = m.group(1).strip()
    # Find first { ... } block
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    return json.loads(text)


def get_llm_provider() -> LLMProvider:
    """Return the best available LLM provider. Groq preferred (faster, free)."""
    if settings.GROQ_API_KEY:
        try:
            provider = GroqProvider(settings.GROQ_API_KEY)
            if provider.client:
                logger.info("[LLM] Using Groq provider (qwen3.8-27b)")
                return provider
        except Exception as e:
            logger.warning(f"[LLM] Groq init failed: {e}")

    if settings.GEMINI_API_KEY:
        try:
            provider = GeminiProvider(settings.GEMINI_API_KEY)
            if provider.model:
                logger.info("[LLM] Using Gemini provider")
                return provider
        except Exception as e:
            logger.warning(f"[LLM] Gemini init failed: {e}")

    raise RuntimeError(
        "No LLM provider configured! Please set GROQ_API_KEY or GEMINI_API_KEY in your .env file."
    )
