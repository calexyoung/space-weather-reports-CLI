"""
Model Provider Factory

Provides factory functions for creating model providers and querying available models.
Supports loading configuration from YAML files.
"""

import os
import logging
from typing import Optional, Dict, Any, List

import yaml

from .base import ModelProvider, ModelConfig, ProviderType, ProviderError
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider
from .google_provider import GoogleProvider

logger = logging.getLogger(__name__)

# Registry of provider classes by type
PROVIDER_CLASSES = {
    ProviderType.ANTHROPIC: AnthropicProvider,
    ProviderType.OPENAI: OpenAIProvider,
    ProviderType.GOOGLE: GoogleProvider,
}


def _get_all_builtin_models() -> Dict[str, ModelConfig]:
    """
    Get all built-in models from all providers

    Returns:
        Dictionary of model name -> ModelConfig
    """
    models = {}
    models.update(AnthropicProvider.get_available_models())
    models.update(OpenAIProvider.get_available_models())
    models.update(GoogleProvider.get_available_models())
    return models


def _load_models_from_config(config_path: str) -> Dict[str, ModelConfig]:
    """
    Load model configurations from a YAML config file

    Args:
        config_path: Path to the config.yaml file

    Returns:
        Dictionary of model name -> ModelConfig
    """
    models = {}

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        if not config or 'models' not in config:
            return models

        models_config = config['models']
        providers_config = models_config.get('providers', {})

        for provider_name, provider_data in providers_config.items():
            # Map provider name to ProviderType
            try:
                provider_type = ProviderType(provider_name.lower())
            except ValueError:
                logger.warning(f"Unknown provider type: {provider_name}")
                continue

            # Process each model in this provider
            for model_name, model_data in provider_data.get('models', {}).items():
                models[model_name] = ModelConfig(
                    name=model_name,
                    model_id=model_data.get('model_id', model_name),
                    provider=provider_type,
                    max_tokens=model_data.get('max_tokens', 8192),
                    description=model_data.get('description', ''),
                    supports_system_prompt=model_data.get('supports_system_prompt', True),
                    supports_vision=model_data.get('supports_vision', False),
                    default_temperature=model_data.get('default_temperature', 1.0)
                )

    except FileNotFoundError:
        logger.debug(f"Config file not found: {config_path}")
    except yaml.YAMLError as e:
        logger.warning(f"Error parsing config file: {e}")
    except Exception as e:
        logger.warning(f"Error loading models from config: {e}")

    return models


def get_default_model(config_path: Optional[str] = None) -> str:
    """
    Get the default model name from config

    Args:
        config_path: Path to config file (defaults to ./config.yaml)

    Returns:
        Default model name
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        if config and 'models' in config:
            return config['models'].get('default', 'claude-sonnet-4.5')
    except Exception:
        pass

    return 'claude-sonnet-4.5'


def list_available_models(
    config_path: Optional[str] = None,
    include_builtin: bool = True
) -> Dict[str, ModelConfig]:
    """
    List all available models

    Args:
        config_path: Path to config file (defaults to ./config.yaml)
        include_builtin: Include built-in model definitions

    Returns:
        Dictionary of model name -> ModelConfig
    """
    models = {}

    # Start with built-in models
    if include_builtin:
        models.update(_get_all_builtin_models())

    # Override/extend with config file models
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

    config_models = _load_models_from_config(config_path)
    models.update(config_models)

    return models


def get_model_info(
    model_name: str,
    config_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific model

    Args:
        model_name: Name of the model
        config_path: Path to config file

    Returns:
        Dictionary with model info, or None if not found
    """
    models = list_available_models(config_path)

    if model_name in models:
        return models[model_name].to_dict()

    return None


def get_provider(
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    config_path: Optional[str] = None
) -> ModelProvider:
    """
    Get a model provider instance for the specified model

    This is the main factory function for creating providers.

    Args:
        model_name: Name of the model (e.g., "claude-sonnet-4.5", "gpt-4o")
                   If None, uses default from config
        api_key: API key (if not provided, uses environment variable)
        config_path: Path to config file (defaults to ./config.yaml)

    Returns:
        ModelProvider instance for the requested model

    Raises:
        ProviderError: If model is not found or provider cannot be created

    Usage:
        # Use default model
        provider = get_provider()

        # Use specific model
        provider = get_provider("gpt-4o")

        # Use specific model with custom API key
        provider = get_provider("claude-sonnet-4.5", api_key="sk-...")

        # Generate response
        response = provider.generate("Hello!")
        print(response.content)
    """
    # Get default model if not specified
    if model_name is None:
        model_name = get_default_model(config_path)
        logger.debug(f"Using default model: {model_name}")

    # Get all available models
    models = list_available_models(config_path)

    # Find the model config
    if model_name not in models:
        available = ", ".join(sorted(models.keys()))
        raise ProviderError(
            f"Unknown model: {model_name}. Available models: {available}"
        )

    model_config = models[model_name]

    # Get the provider class
    provider_type = model_config.provider
    if provider_type not in PROVIDER_CLASSES:
        raise ProviderError(
            f"No provider implementation for type: {provider_type.value}"
        )

    provider_class = PROVIDER_CLASSES[provider_type]

    # Create and return the provider instance
    try:
        provider = provider_class(model_config, api_key=api_key)
        logger.debug(f"Created provider: {provider}")
        return provider
    except Exception as e:
        raise ProviderError(
            f"Failed to create provider for {model_name}: {e}",
            provider=provider_type.value,
            original_error=e
        )


def get_providers_status(config_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Get status of all configured providers

    Returns information about which providers are available and configured.

    Args:
        config_path: Path to config file

    Returns:
        Dictionary with provider status information
    """
    status = {}

    # Check Anthropic
    anthropic_key = os.getenv(AnthropicProvider.API_KEY_ENV)
    status['anthropic'] = {
        'configured': bool(anthropic_key),
        'api_key_env': AnthropicProvider.API_KEY_ENV,
        'models': list(AnthropicProvider.get_available_models().keys())
    }

    # Check OpenAI
    openai_key = os.getenv(OpenAIProvider.API_KEY_ENV)
    status['openai'] = {
        'configured': bool(openai_key),
        'api_key_env': OpenAIProvider.API_KEY_ENV,
        'models': list(OpenAIProvider.get_available_models().keys())
    }

    # Check Google
    google_key = os.getenv(GoogleProvider.API_KEY_ENV)
    status['google'] = {
        'configured': bool(google_key),
        'api_key_env': GoogleProvider.API_KEY_ENV,
        'models': list(GoogleProvider.get_available_models().keys())
    }

    return status


# Convenience function for quick testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("=" * 60)
    print("Model Provider Factory Test")
    print("=" * 60)

    # List available models
    print("\nAvailable Models:")
    models = list_available_models()
    for name, config in sorted(models.items()):
        print(f"  - {name} ({config.provider.value}): {config.description}")

    # Check provider status
    print("\nProvider Status:")
    status = get_providers_status()
    for provider, info in status.items():
        configured = "Yes" if info['configured'] else f"No (set {info['api_key_env']})"
        print(f"  - {provider}: Configured={configured}")

    # Get default model
    default = get_default_model()
    print(f"\nDefault Model: {default}")

    # Try to create a provider
    print("\nTesting provider creation...")
    try:
        provider = get_provider()
        print(f"  Created: {provider}")
        print(f"  Model ID: {provider.model_id}")
    except ProviderError as e:
        print(f"  Error: {e}")
