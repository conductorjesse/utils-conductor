import os
import time
from typing import List, Dict, Any, Optional
import openai
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple model definitions for easier reference
MODELS = {
    # OpenAI models
    "openai": {
        "o1-mini": "o1-mini",
        "o1": "o1",
        "gpt-4o": "gpt-4o",
        "gpt-3.5-turbo": "gpt-3.5-turbo"
    },
    # Claude models
    "claude": {
        "sonnet": "claude-3-7-sonnet-20250219",
        "opus": "claude-3-opus-20240229",
        "haiku": "claude-3-haiku-20240307"
    }
}

def get_api_key(provider: str) -> str:
    """Get API key for the specified provider from environment variables."""
    if provider.lower() == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
        return api_key
    elif provider.lower() in ["anthropic", "claude"]:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("Claude API key not found. Please set ANTHROPIC_API_KEY in your environment.")
        return api_key
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def call_openai(
    prompt: str,
    model: str = "o1-mini",
    temperature: float = 1,
    previous_messages: Optional[List[Dict[str, str]]] = None,
    retries: int = 3,
    retry_delay: int = 5
) -> str:
    """Call OpenAI API with the specified parameters."""
    api_key = get_api_key("openai")
    
    # Resolve model shorthand if needed
    if model in MODELS["openai"]:
        model = MODELS["openai"][model]
    
    # Set up messages
    if previous_messages is None:
        previous_messages = []
    
    messages = previous_messages + [{"role": "user", "content": prompt}]
    
    # Retry mechanism for API calls
    for attempt in range(retries):
        try:
            response = openai.Client(api_key=api_key).chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < retries - 1:
                print(f"OpenAI API call failed: {str(e)}. Retrying in {retry_delay} seconds... (Attempt {attempt+1}/{retries})")
                time.sleep(retry_delay)
            else:
                return f"Error calling OpenAI API: {str(e)}"

def call_claude(
    prompt: str,
    model: str = "sonnet",
    temperature: float = 1,
    max_tokens: int = 4096,
    previous_messages: Optional[List[Dict[str, str]]] = None,
    retries: int = 3,
    retry_delay: int = 5
) -> str:
    """Call Claude API with the specified parameters."""
    api_key = get_api_key("claude")
    
    # Resolve model shorthand if needed
    if model in MODELS["claude"]:
        model = MODELS["claude"][model]
    
    # Set up messages
    if previous_messages is None:
        previous_messages = []
    
    # Convert OpenAI message format to Claude format
    claude_messages = []
    for msg in previous_messages:
        claude_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add the current prompt
    claude_messages.append({"role": "user", "content": prompt})
    
    # Retry mechanism for API calls
    for attempt in range(retries):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model,
                messages=claude_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=1.0
            )
            return response.content[0].text
        except Exception as e:
            if attempt < retries - 1:
                print(f"Claude API call failed: {str(e)}. Retrying in {retry_delay} seconds... (Attempt {attempt+1}/{retries})")
                time.sleep(retry_delay)
            else:
                return f"Error calling Claude API: {str(e)}" 