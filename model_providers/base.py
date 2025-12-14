"""
Base Model Provider Interface

This module defines the abstract interface that all model providers must implement.
This allows for a unified API across different AI providers (Anthropic, OpenAI, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class ProviderType(Enum):
    """Supported AI provider types"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


@dataclass
class ModelResponse:
    """
    Standardized response from any model provider

    Attributes:
        content: The generated text content
        model: The model ID that was used
        provider: The provider type (anthropic, openai, etc.)
        usage: Token usage statistics
        finish_reason: Why the generation stopped
        raw_response: Original provider-specific response (for debugging)
    """
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    raw_response: Optional[Any] = None

    @property
    def input_tokens(self) -> int:
        """Get input token count"""
        return self.usage.get('input_tokens', 0) or self.usage.get('prompt_tokens', 0)

    @property
    def output_tokens(self) -> int:
        """Get output token count"""
        return self.usage.get('output_tokens', 0) or self.usage.get('completion_tokens', 0)

    @property
    def total_tokens(self) -> int:
        """Get total token count"""
        return self.usage.get('total_tokens', self.input_tokens + self.output_tokens)


@dataclass
class ModelConfig:
    """
    Configuration for a specific model

    Attributes:
        name: User-friendly model name (e.g., "claude-sonnet-4.5")
        model_id: Provider-specific model ID (e.g., "claude-sonnet-4-5-20250929")
        provider: The provider type
        max_tokens: Maximum output tokens
        description: Human-readable description
        supports_system_prompt: Whether model supports system prompts
        supports_vision: Whether model supports image inputs
        default_temperature: Default temperature setting
    """
    name: str
    model_id: str
    provider: ProviderType
    max_tokens: int = 8192
    description: str = ""
    supports_system_prompt: bool = True
    supports_vision: bool = False
    default_temperature: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'model_id': self.model_id,
            'provider': self.provider.value,
            'max_tokens': self.max_tokens,
            'description': self.description,
            'supports_system_prompt': self.supports_system_prompt,
            'supports_vision': self.supports_vision,
            'default_temperature': self.default_temperature
        }


class ModelProvider(ABC):
    """
    Abstract base class for AI model providers

    All provider implementations must inherit from this class and implement
    the required abstract methods. This ensures a consistent interface across
    different AI providers.

    Usage:
        provider = get_provider("claude-sonnet-4.5")
        response = provider.generate("Your prompt here")
        print(response.content)
    """

    def __init__(self, model_config: ModelConfig, api_key: Optional[str] = None):
        """
        Initialize the provider

        Args:
            model_config: Configuration for the model to use
            api_key: API key (if not provided, will try to load from environment)
        """
        self.model_config = model_config
        self.api_key = api_key
        self._client = None

    @property
    def model_name(self) -> str:
        """Get the user-friendly model name"""
        return self.model_config.name

    @property
    def model_id(self) -> str:
        """Get the provider-specific model ID"""
        return self.model_config.model_id

    @property
    def provider_type(self) -> ProviderType:
        """Get the provider type"""
        return self.model_config.provider

    @abstractmethod
    def _initialize_client(self) -> None:
        """
        Initialize the provider's API client

        This method should set up self._client with the appropriate SDK client.
        Called lazily on first generate() call.
        """
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a response from the model

        Args:
            prompt: The user prompt to send to the model
            system_prompt: Optional system prompt for context/instructions
            max_tokens: Maximum tokens to generate (uses model default if not specified)
            temperature: Sampling temperature (uses model default if not specified)
            **kwargs: Additional provider-specific parameters

        Returns:
            ModelResponse with the generated content and metadata

        Raises:
            ProviderError: If the API call fails
        """
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate that the API key is configured and working

        Returns:
            True if API key is valid, False otherwise
        """
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model

        Returns:
            Dictionary with model configuration details
        """
        return self.model_config.to_dict()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"


class ProviderError(Exception):
    """
    Exception raised when a provider operation fails

    Attributes:
        message: Error description
        provider: The provider that raised the error
        original_error: The underlying exception (if any)
    """

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.provider:
            return f"[{self.provider}] {self.message}"
        return self.message
