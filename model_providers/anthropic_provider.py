"""
Anthropic (Claude) Model Provider

Implements the ModelProvider interface for Anthropic's Claude models.
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


class AnthropicProvider(ModelProvider):
    """
    Provider implementation for Anthropic's Claude models

    Supports:
    - Claude Sonnet 4.5
    - Claude Opus 4.5
    - Claude Haiku 3.5
    - Other Claude models

    Usage:
        config = ModelConfig(
            name="claude-sonnet-4.5",
            model_id="claude-sonnet-4-5-20250929",
            provider=ProviderType.ANTHROPIC
        )
        provider = AnthropicProvider(config)
        response = provider.generate("Hello, Claude!")
    """

    # Environment variable for API key
    API_KEY_ENV = "ANTHROPIC_API_KEY"

    def __init__(self, model_config: ModelConfig, api_key: Optional[str] = None):
        """
        Initialize Anthropic provider

        Args:
            model_config: Configuration for the Claude model
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
        """
        super().__init__(model_config, api_key)

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv(self.API_KEY_ENV)

        if not self.api_key:
            logger.warning(
                f"No Anthropic API key provided. Set {self.API_KEY_ENV} environment variable."
            )

    def _initialize_client(self) -> None:
        """Initialize the Anthropic client"""
        if self._client is not None:
            return

        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
            logger.debug(f"Initialized Anthropic client for model {self.model_id}")
        except ImportError:
            raise ProviderError(
                "anthropic package not installed. Run: pip install anthropic",
                provider="anthropic"
            )
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize Anthropic client: {e}",
                provider="anthropic",
                original_error=e
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
        Generate a response using Claude

        Args:
            prompt: The user message to send
            system_prompt: Optional system instructions
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
                provider="anthropic"
            )

        # Set defaults
        max_tokens = max_tokens or self.model_config.max_tokens
        temperature = temperature if temperature is not None else self.model_config.default_temperature

        # Build messages
        messages = [{"role": "user", "content": prompt}]

        try:
            # Make API call
            api_kwargs = {
                "model": self.model_id,
                "max_tokens": max_tokens,
                "messages": messages,
            }

            # Add system prompt if provided
            if system_prompt:
                api_kwargs["system"] = system_prompt

            # Add temperature if not default
            if temperature != 1.0:
                api_kwargs["temperature"] = temperature

            # Add any additional kwargs
            api_kwargs.update(kwargs)

            logger.debug(f"Calling Anthropic API with model {self.model_id}")
            response = self._client.messages.create(**api_kwargs)

            # Extract content
            content = ""
            if response.content:
                content = response.content[0].text

            # Build standardized response
            return ModelResponse(
                content=content,
                model=response.model,
                provider="anthropic",
                usage={
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                },
                finish_reason=response.stop_reason,
                raw_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Anthropic API error: {error_msg}")
            raise ProviderError(
                f"API call failed: {error_msg}",
                provider="anthropic",
                original_error=e
            )

    def validate_api_key(self) -> bool:
        """
        Validate the Anthropic API key

        Returns:
            True if key is valid
        """
        if not self.api_key:
            return False

        try:
            self._initialize_client()
            # Make a minimal API call to validate
            self._client.messages.create(
                model=self.model_id,
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
        Get all available Anthropic models

        Returns:
            Dictionary of model name -> ModelConfig
        """
        return {
            "claude-sonnet-4.5": ModelConfig(
                name="claude-sonnet-4.5",
                model_id="claude-sonnet-4-5-20250929",
                provider=ProviderType.ANTHROPIC,
                max_tokens=8192,
                description="Fast, balanced performance - recommended for most tasks",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
            "claude-opus-4.5": ModelConfig(
                name="claude-opus-4.5",
                model_id="claude-opus-4-5-20251101",
                provider=ProviderType.ANTHROPIC,
                max_tokens=8192,
                description="Most capable model, best for complex tasks",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
            "claude-haiku-3.5": ModelConfig(
                name="claude-haiku-3.5",
                model_id="claude-3-5-haiku-20241022",
                provider=ProviderType.ANTHROPIC,
                max_tokens=8192,
                description="Fastest and most economical",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
        }
