import os
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _extract_retry_delay_seconds(exc: Exception, default: float = 20.0) -> float:
    """
    Best-effort extraction of the server-suggested retry delay from a 429
    error message (Gemini includes 'Please retry in Ns' in its error text).
    Falls back to a sane default if it can't find one.
    """
    match = re.search(r"retry in ([\d.]+)s", str(exc), flags=re.IGNORECASE)
    if match:
        try:
            return float(match.group(1)) + 1.0  # small buffer
        except ValueError:
            pass
    return default


def _is_rate_limit_error(exc: Exception) -> bool:
    text = str(exc)
    return "429" in text or "RESOURCE_EXHAUSTED" in text or "rate limit" in text.lower()


def _parse_json_response(text: str) -> Any:
    """Best-effort JSON parser for LLM responses."""
    if not text:
        raise ValueError("Empty response from LLM")

    cleaned = text.strip()

    # Remove markdown fences if present
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.IGNORECASE | re.DOTALL)
    if match:
        cleaned = match.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    for start_char in ("[", "{"):
        start = cleaned.find(start_char)
        if start == -1:
            continue

        for end in range(len(cleaned), start, -1):
            candidate = cleaned[start:end].strip()
            candidate = re.sub(r",(\s*[}\]])", r"\1", candidate)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

    raise ValueError("Could not parse JSON response from LLM")


class LLMClient(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def _generate_text_impl(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Provider-specific implementation. Subclasses implement this instead
        of generate_text directly, so retry-on-rate-limit applies uniformly."""
        pass

    def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        max_retries: int = 3,
    ) -> str:
        """
        Generate text from a prompt, with automatic retry on rate-limit (429)
        errors using the server-suggested retry delay when available.
        Free-tier quotas (Gemini, Groq, etc.) are shared per-minute limits
        that reset quickly, so a short wait-and-retry is usually all that's
        needed — this matters once running a full daily batch of
        applications instead of one-off test runs.
        """
        last_exc = None
        for attempt in range(max_retries + 1):
            try:
                return self._generate_text_impl(prompt, system_prompt, temperature, max_tokens)
            except Exception as exc:
                last_exc = exc
                if not _is_rate_limit_error(exc) or attempt == max_retries:
                    raise
                delay = _extract_retry_delay_seconds(exc)
                logger.warning(
                    "Rate limited (attempt %d/%d). Waiting %.1fs before retrying...",
                    attempt + 1, max_retries, delay,
                )
                time.sleep(delay)
        raise last_exc  # pragma: no cover — unreachable, satisfies type checkers

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        Generate and parse JSON from a prompt. Shared across all providers so the
        repair-retry logic only has to be maintained in one place.
        """
        json_prompt = (
            f"{prompt}\n\n"
            "Respond ONLY with valid, complete JSON. No markdown code fences, "
            "no commentary before or after, no truncation."
        )
        text = self.generate_text(json_prompt, system_prompt, temperature, max_tokens)

        try:
            return _parse_json_response(text)
        except Exception:
            logger.warning(
                "Initial JSON parse failed (likely truncated or malformed, %d chars returned). "
                "Attempting one repair pass.",
                len(text) if text else 0,
            )
            try:
                repair_prompt = (
                    "The following is supposed to be JSON but is broken, incomplete, "
                    "or was cut off. Return ONLY the corrected, complete, valid JSON "
                    "with no markdown fences and no commentary:\n\n"
                    f"{text}"
                )
                fixed = self.generate_text(repair_prompt, "", temperature=0, max_tokens=max_tokens)
                return _parse_json_response(fixed)
            except Exception as exc:
                logger.error("Failed to parse JSON response even after repair attempt: %s", text)
                raise ValueError("Could not parse JSON response from LLM") from exc


class GeminiClient(LLMClient):
    """Google Gemini API client (uses the current `google-genai` SDK)."""

    def __init__(self):
        try:
            from google import genai
            from google.genai import types
            self.genai = genai
            self.types = types
        except ImportError as exc:
            raise ImportError(
                "google-genai not installed. Run: pip install google-genai"
            ) from exc

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in .env")

        self.client = self.genai.Client(api_key=api_key)
        # gemini-2.5-flash's free tier was cut to 20 req/day (Dec 2025), and
        # gemini-2.5-flash-lite is no longer available to newly-created API
        # keys/projects (Google routes new accounts to the 3.x generation).
        # gemini-3.1-flash-lite is the current cost-efficient, high-throughput
        # model built for exactly this kind of structured/high-frequency task,
        # and remains free-tier eligible with a much more usable daily cap.
        self._model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

    def _generate_text_impl(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = self.client.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
                config=self.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    # Disable "thinking" for these structured tasks. Thinking
                    # tokens count against max_output_tokens, and were silently
                    # eating the budget meant for the actual visible answer,
                    # causing truncation even on short requests like cover letters.
                    thinking_config=self.types.ThinkingConfig(thinking_budget=0),
                ),
            )

            # Detect truncation so failures are diagnosable instead of showing up
            # only as a downstream JSON parse error.
            try:
                candidate = response.candidates[0]
                finish_reason = str(candidate.finish_reason)
                if "MAX_TOKENS" in finish_reason.upper():
                    logger.warning(
                        "Gemini response was truncated at max_tokens=%d. "
                        "Consider raising max_tokens or shortening the prompt's expected output.",
                        max_tokens,
                    )
            except (IndexError, AttributeError):
                pass  # response shape didn't include candidates/finish_reason; ignore

            return response.text
        except Exception as exc:
            logger.error("Gemini API error: %s", exc)
            raise


class AnthropicClient(LLMClient):
    """Anthropic Claude API client."""

    def __init__(self):
        try:
            import anthropic
            self.anthropic = anthropic
        except ImportError as exc:
            raise ImportError("anthropic not installed. Run: pip install anthropic") from exc

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")

        self.client = self.anthropic.Anthropic(api_key=api_key)

    def _generate_text_impl(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else None,
                messages=[{"role": "user", "content": prompt}],
            )
            if response.stop_reason == "max_tokens":
                logger.warning(
                    "Anthropic response was truncated at max_tokens=%d. "
                    "Consider raising max_tokens or shortening the prompt's expected output.",
                    max_tokens,
                )
            return response.content[0].text
        except Exception as exc:
            logger.error("Anthropic API error: %s", exc)
            raise


class GroqClient(LLMClient):
    """Groq API client."""

    # mixtral-8x7b-32768 was decommissioned; llama-3.3-70b-versatile was later
    # deprecated too (June 2026). Current recommended general-purpose model:
    _MODEL = "openai/gpt-oss-120b"

    def __init__(self):
        try:
            from groq import Groq
            self.groq = Groq
        except ImportError as exc:
            raise ImportError("groq not installed. Run: pip install groq") from exc

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in .env")

        self.client = self.groq(api_key=api_key)

    def _generate_text_impl(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self._MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choice = response.choices[0]
            if getattr(choice, "finish_reason", None) == "length":
                logger.warning(
                    "Groq response was truncated at max_tokens=%d. "
                    "Consider raising max_tokens or shortening the prompt's expected output.",
                    max_tokens,
                )
            return choice.message.content
        except Exception as exc:
            logger.error("Groq API error: %s", exc)
            raise


def get_llm_client() -> LLMClient:
    """Factory function to get LLM client based on provider."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        return GeminiClient()
    elif provider == "anthropic":
        return AnthropicClient()
    elif provider == "groq":
        return GroqClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")