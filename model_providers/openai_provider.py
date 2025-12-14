"""
OpenAI Model Provider

Implements the ModelProvider interface for OpenAI's GPT models.
"""

import os
import logging
from typing import Optional, Dict, Any

from .base import (
    ModelProvider,
    ModelConfig,
    ModelResponse,
    ProviderType,
    ProviderError
)

logger = logging.getLogger(__name__)


class OpenAIProvider(ModelProvider):
    """
    Provider implementation for OpenAI's GPT models

    Supports:
    - GPT-4o
    - GPT-4 Turbo
    - GPT-4
    - o1 (reasoning model)
    - o1-mini

    Usage:
        config = ModelConfig(
            name="gpt-4o",
            model_id="gpt-4o",
            provider=ProviderType.OPENAI
        )
        provider = OpenAIProvider(config)
        response = provider.generate("Hello, GPT!")
    """

    # Environment variable for API key
    API_KEY_ENV = "OPENAI_API_KEY"

    # Models that don't support system prompts (reasoning models)
    NO_SYSTEM_PROMPT_MODELS = {"o1", "o1-mini", "o1-preview"}

    # Models that require max_completion_tokens instead of max_tokens
    MAX_COMPLETION_TOKENS_MODELS = {"o1", "o1-mini", "o1-preview", "gpt-5.1", "gpt-5.1-instant"}

    def __init__(self, model_config: ModelConfig, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider

        Args:
            model_config: Configuration for the GPT model
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        """
        super().__init__(model_config, api_key)

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv(self.API_KEY_ENV)

        if not self.api_key:
            logger.warning(
                f"No OpenAI API key provided. Set {self.API_KEY_ENV} environment variable."
            )

    def _initialize_client(self) -> None:
        """Initialize the OpenAI client"""
        if self._client is not None:
            return

        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
            logger.debug(f"Initialized OpenAI client for model {self.model_id}")
        except ImportError:
            raise ProviderError(
                "openai package not installed. Run: pip install openai",
                provider="openai"
            )
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize OpenAI client: {e}",
                provider="openai",
                original_error=e
            )

    def _is_reasoning_model(self) -> bool:
        """Check if the current model is a reasoning model (o1 series)"""
        return self.model_id in self.NO_SYSTEM_PROMPT_MODELS or self.model_id.startswith("o1")

    def _uses_max_completion_tokens(self) -> bool:
        """Check if the model uses max_completion_tokens instead of max_tokens"""
        return (
            self.model_id in self.MAX_COMPLETION_TOKENS_MODELS or
            self.model_id.startswith("o1") or
            self.model_id.startswith("gpt-5")
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a response using OpenAI GPT

        Args:
            prompt: The user message to send
            system_prompt: Optional system instructions (not supported by o1 models)
            max_tokens: Maximum tokens to generate (default: model's max_tokens)
            temperature: Sampling temperature (default: model's default_temperature)
            **kwargs: Additional parameters passed to the API

        Returns:
            ModelResponse with generated content

        Raises:
            ProviderError: If API call fails
        """
        # Initialize client if needed
        self._initialize_client()

        if not self.api_key:
            raise ProviderError(
                f"No API key configured. Set {self.API_KEY_ENV} environment variable.",
                provider="openai"
            )

        # Set defaults
        max_tokens = max_tokens or self.model_config.max_tokens
        temperature = temperature if temperature is not None else self.model_config.default_temperature

        # Build messages
        messages = []

        # Add system prompt if supported and provided
        if system_prompt and not self._is_reasoning_model():
            messages.append({"role": "system", "content": system_prompt})
        elif system_prompt and self._is_reasoning_model():
            # For reasoning models, prepend system prompt to user message
            prompt = f"{system_prompt}\n\n{prompt}"
            logger.debug(f"Model {self.model_id} doesn't support system prompts, prepending to user message")

        messages.append({"role": "user", "content": prompt})

        try:
            # Build API call parameters
            api_kwargs = {
                "model": self.model_id,
                "messages": messages,
            }

            # GPT-5.x and reasoning models use max_completion_tokens instead of max_tokens
            if self._uses_max_completion_tokens():
                api_kwargs["max_completion_tokens"] = max_tokens
                # Only add temperature if not a reasoning model (o1 series doesn't support it)
                if not self._is_reasoning_model() and temperature != 1.0:
                    api_kwargs["temperature"] = temperature
            else:
                api_kwargs["max_tokens"] = max_tokens
                if temperature != 1.0:
                    api_kwargs["temperature"] = temperature

            # Add any additional kwargs (filtered for model compatibility)
            for key, value in kwargs.items():
                if key not in api_kwargs:
                    api_kwargs[key] = value

            logger.debug(f"Calling OpenAI API with model {self.model_id}")
            response = self._client.chat.completions.create(**api_kwargs)

            # Extract content
            content = ""
            if response.choices:
                content = response.choices[0].message.content or ""

            # Build standardized response
            usage_data = {}
            if response.usage:
                usage_data = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens,
                    # Also include Anthropic-style keys for compatibility
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                }

            finish_reason = None
            if response.choices:
                finish_reason = response.choices[0].finish_reason

            return ModelResponse(
                content=content,
                model=response.model,
                provider="openai",
                usage=usage_data,
                finish_reason=finish_reason,
                raw_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"OpenAI API error: {error_msg}")
            raise ProviderError(
                f"API call failed: {error_msg}",
                provider="openai",
                original_error=e
            )

    def validate_api_key(self) -> bool:
        """
        Validate the OpenAI API key

        Returns:
            True if key is valid
        """
        if not self.api_key:
            return False

        try:
            self._initialize_client()
            # Make a minimal API call to validate
            self._client.chat.completions.create(
                model="gpt-4o-mini",  # Use cheapest model for validation
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as e:
            logger.warning(f"API key validation failed: {e}")
            return False

    @staticmethod
    def get_available_models() -> Dict[str, ModelConfig]:
        """
        Get all available OpenAI models

        Returns:
            Dictionary of model name -> ModelConfig
        """
        return {
            "gpt-5.1": ModelConfig(
                name="gpt-5.1",
                model_id="gpt-5.1",
                provider=ProviderType.OPENAI,
                max_tokens=16384,
                description="Latest GPT-5.1 with adaptive thinking - best for complex tasks",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
            "gpt-5.1-instant": ModelConfig(
                name="gpt-5.1-instant",
                model_id="gpt-5.1-instant",
                provider=ProviderType.OPENAI,
                max_tokens=16384,
                description="GPT-5.1 Instant - fast, intelligent everyday model",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
            "gpt-4o": ModelConfig(
                name="gpt-4o",
                model_id="gpt-4o",
                provider=ProviderType.OPENAI,
                max_tokens=4096,
                description="GPT-4o multimodal, fast and capable",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
            "gpt-4o-mini": ModelConfig(
                name="gpt-4o-mini",
                model_id="gpt-4o-mini",
                provider=ProviderType.OPENAI,
                max_tokens=4096,
                description="Smaller, faster, cheaper GPT-4o variant",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
            "o1": ModelConfig(
                name="o1",
                model_id="o1",
                provider=ProviderType.OPENAI,
                max_tokens=32768,
                description="Reasoning model for complex tasks",
                supports_system_prompt=False,
                supports_vision=False,
                default_temperature=1.0
            ),
            "o1-mini": ModelConfig(
                name="o1-mini",
                model_id="o1-mini",
                provider=ProviderType.OPENAI,
                max_tokens=32768,
                description="Smaller reasoning model, faster",
                supports_system_prompt=False,
                supports_vision=False,
                default_temperature=1.0
            ),
        }
