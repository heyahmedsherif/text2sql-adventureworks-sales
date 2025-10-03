# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License
from openai import AsyncOpenAI
import os
import dotenv

dotenv.load_dotenv()


class OpenAIConnector:
    @classmethod
    def get_authentication_properties(cls) -> dict:
        """Get API key - supports OpenAI or Claude (Anthropic)"""
        # Check for provider type
        provider = os.environ.get("LLM_PROVIDER", "openai").lower()

        if provider == "claude" or provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY or CLAUDE_API_KEY environment variable is required for Claude")
        else:
            api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OpenAI__ApiKey")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")

        return api_key, provider

    async def run_completion_request(
        self,
        messages: list[dict],
        temperature=0,
        max_tokens=2000,
        model="4o-mini",
        response_format=None,
    ) -> str:
        api_key, provider = self.get_authentication_properties()

        # Use Claude/Anthropic
        if provider in ["claude", "anthropic"]:
            return await self._run_claude_completion(
                messages, temperature, max_tokens, model, response_format, api_key
            )

        # Use OpenAI (default)
        return await self._run_openai_completion(
            messages, temperature, max_tokens, model, response_format, api_key
        )

    async def _run_openai_completion(
        self, messages, temperature, max_tokens, model, response_format, api_key
    ):
        """Run completion using OpenAI API"""
        from openai import AsyncOpenAI

        # Map model names to OpenAI API model names
        if model == "4o-mini":
            model_name = os.environ.get("OpenAI__MiniCompletionDeployment", "gpt-4o-mini")
        elif model == "4o":
            model_name = os.environ.get("OpenAI__CompletionDeployment", "gpt-4o")
        else:
            model_name = model

        async with AsyncOpenAI(api_key=api_key) as open_ai_client:
            if response_format is not None:
                response = await open_ai_client.beta.chat.completions.parse(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
            else:
                response = await open_ai_client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        message = response.choices[0].message
        if response_format is not None and message.parsed is not None:
            return message.parsed
        elif response_format is not None:
            return message.refusal
        else:
            return message.content

    async def _run_claude_completion(
        self, messages, temperature, max_tokens, model, response_format, api_key
    ):
        """Run completion using Claude/Anthropic API"""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        # Map model names to Claude models
        model_map = {
            "4o-mini": os.environ.get("CLAUDE_MINI_MODEL", "claude-3-5-haiku-20241022"),
            "4o": os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
        }
        model_name = model_map.get(model, model)

        # Convert OpenAI message format to Claude format
        claude_messages = []
        system_message = None

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        async with AsyncAnthropic(api_key=api_key) as client:
            kwargs = {
                "model": model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": claude_messages,
            }

            if system_message:
                kwargs["system"] = system_message

            response = await client.messages.create(**kwargs)

            # Extract text from response
            return response.content[0].text

    async def run_embedding_request(self, batch: list[str]):
        """Generate embeddings for text - uses OpenAI (Claude doesn't have embeddings API)"""
        api_key, provider = self.get_authentication_properties()

        # For embeddings, we always use OpenAI even if main provider is Claude
        # You'll need both API keys if using Claude for completions
        if provider in ["claude", "anthropic"]:
            # Try to get OpenAI key for embeddings
            openai_key = os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError(
                    "OPENAI_API_KEY required for embeddings (Claude doesn't support embeddings). "
                    "Set both ANTHROPIC_API_KEY and OPENAI_API_KEY in your .env file."
                )
            api_key = openai_key

        model = os.environ.get("OpenAI__EmbeddingModel", "text-embedding-3-small")

        async with AsyncOpenAI(api_key=api_key) as open_ai_client:
            embeddings = await open_ai_client.embeddings.create(
                model=model,
                input=batch,
            )

        return embeddings
