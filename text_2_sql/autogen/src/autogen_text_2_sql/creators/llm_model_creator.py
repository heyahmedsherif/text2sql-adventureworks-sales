# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
import dotenv

dotenv.load_dotenv()


class LLMModelCreator:
    @classmethod
    def get_model(
        cls, model_name: str, structured_output=None
    ) -> OpenAIChatCompletionClient:
        """Retrieves the model based on the model name.

        Args:
        ----
            model_name (str): The name of the model to retrieve.

        Returns:
            OpenAIChatCompletionClient: The model client."""
        if model_name == "4o-mini":
            return cls.gpt_4o_mini_model(structured_output=structured_output)
        elif model_name == "4o":
            return cls.gpt_4o_model(structured_output=structured_output)
        else:
            raise ValueError(f"Model {model_name} not found")

    @classmethod
    def get_authentication_properties(cls) -> tuple:
        """Get API key and provider - supports OpenAI or Claude"""
        provider = os.environ.get("LLM_PROVIDER", "openai").lower()

        if provider in ["claude", "anthropic"]:
            api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY or CLAUDE_API_KEY environment variable is required for Claude")
            # AutoGen uses OpenAI SDK, so we use OpenAI compatibility mode via base_url
            # Claude SDK doesn't work with AutoGen directly - use OpenAI API instead
            # For Claude, user should use OPENAI_API_KEY
            raise ValueError(
                "AutoGen multi-agent system currently only supports OpenAI API. "
                "Please set LLM_PROVIDER=openai and OPENAI_API_KEY. "
                "For main Text2SQL queries, Claude will still be used."
            )
        else:
            api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OpenAI__ApiKey")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")

        return api_key, provider

    @classmethod
    def gpt_4o_mini_model(
        cls, structured_output=None
    ) -> OpenAIChatCompletionClient:
        api_key, provider = cls.get_authentication_properties()
        model_name = os.environ.get("OpenAI__MiniCompletionDeployment", "gpt-4o-mini")

        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=api_key,
            model_capabilities={
                "vision": False,
                "function_calling": True,
                "json_output": True,
            },
            temperature=0,
            response_format=structured_output,
        )

    @classmethod
    def gpt_4o_model(cls, structured_output=None) -> OpenAIChatCompletionClient:
        api_key, provider = cls.get_authentication_properties()
        model_name = os.environ.get("OpenAI__CompletionDeployment", "gpt-4o")

        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=api_key,
            model_capabilities={
                "vision": False,
                "function_calling": True,
                "json_output": True,
            },
            temperature=0,
            response_format=structured_output,
        )
