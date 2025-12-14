"""
Google (Gemini) Model Provider

Implements the ModelProvider interface for Google's Gemini models.
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


class GoogleProvider(ModelProvider):
    """
    Provider implementation for Google's Gemini models

    Supports:
    - Gemini 2.5 Flash
    - Gemini 2.5 Pro
    - Gemini 2.0 Flash

    Usage:
        config = ModelConfig(
            name="gemini-2.5-flash",
            model_id="gemini-2.5-flash",
            provider=ProviderType.GOOGLE
        )
        provider = GoogleProvider(config)
        response = provider.generate("Hello, Gemini!")
    """

    # Environment variable for API key
    API_KEY_ENV = "GOOGLE_API_KEY"

    def __init__(self, model_config: ModelConfig, api_key: Optional[str] = None):
        """
        Initialize Google provider

        Args:
            model_config: Configuration for the Gemini model
            api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)
        """
        super().__init__(model_config, api_key)

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv(self.API_KEY_ENV)

        if not self.api_key:
            logger.warning(
                f"No Google API key provided. Set {self.API_KEY_ENV} environment variable."
            )

    def _initialize_client(self) -> None:
        """Initialize the Google Generative AI client"""
        if self._client is not None:
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model_id)
            logger.debug(f"Initialized Google client for model {self.model_id}")
        except ImportError:
            raise ProviderError(
                "google-generativeai package not installed. Run: pip install google-generativeai",
                provider="google"
            )
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize Google client: {e}",
                provider="google",
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
        Generate a response using Gemini

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
                provider="google"
            )

        # Set defaults
        max_tokens = max_tokens or self.model_config.max_tokens
        temperature = temperature if temperature is not None else self.model_config.default_temperature

        try:
            import google.generativeai as genai

            # Build generation config
            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )

            # Build the full prompt (Gemini handles system instructions differently)
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt

            logger.debug(f"Calling Google API with model {self.model_id}")
            response = self._client.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            # Extract content
            content = ""
            if response.text:
                content = response.text

            # Build usage data (Gemini provides this in usage_metadata)
            usage_data = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage_data = {
                    'prompt_tokens': response.usage_metadata.prompt_token_count,
                    'completion_tokens': response.usage_metadata.candidates_token_count,
                    'total_tokens': response.usage_metadata.total_token_count,
                    # Also include Anthropic-style keys for compatibility
                    'input_tokens': response.usage_metadata.prompt_token_count,
                    'output_tokens': response.usage_metadata.candidates_token_count,
                }

            # Determine finish reason
            finish_reason = None
            if response.candidates:
                finish_reason = str(response.candidates[0].finish_reason.name)

            return ModelResponse(
                content=content,
                model=self.model_id,
                provider="google",
                usage=usage_data,
                finish_reason=finish_reason,
                raw_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Google API error: {error_msg}")
            raise ProviderError(
                f"API call failed: {error_msg}",
                provider="google",
                original_error=e
            )

    def validate_api_key(self) -> bool:
        """
        Validate the Google API key

        Returns:
            True if key is valid
        """
        if not self.api_key:
            return False

        try:
            self._initialize_client()
            # Make a minimal API call to validate
            self._client.generate_content("Hi")
            return True
        except Exception as e:
            logger.warning(f"API key validation failed: {e}")
            return False

    @staticmethod
    def get_available_models() -> Dict[str, ModelConfig]:
        """
        Get all available Google models

        Returns:
            Dictionary of model name -> ModelConfig
        """
        return {
            "gemini-2.5-flash": ModelConfig(
                name="gemini-2.5-flash",
                model_id="gemini-2.5-flash",
                provider=ProviderType.GOOGLE,
                max_tokens=8192,
                description="Latest Gemini 2.5 Flash - fast and capable",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
            "gemini-2.5-pro": ModelConfig(
                name="gemini-2.5-pro",
                model_id="gemini-2.5-pro",
                provider=ProviderType.GOOGLE,
                max_tokens=8192,
                description="Gemini 2.5 Pro - best for complex tasks",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
            "gemini-2.0-flash": ModelConfig(
                name="gemini-2.0-flash",
                model_id="gemini-2.0-flash",
                provider=ProviderType.GOOGLE,
                max_tokens=8192,
                description="Gemini 2.0 Flash - fast and efficient",
                supports_system_prompt=True,
                supports_vision=True,
                default_temperature=1.0
            ),
        }
