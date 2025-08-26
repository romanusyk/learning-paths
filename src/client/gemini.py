import argparse
import json
import os
from typing import Any, Optional, Dict

from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai


def generate_gemini(
    prompt: str,
    model: str = "gemini-1.5-pro",
    structured: bool = False,
    schema: Optional[Dict[str, Any]] = None,
    temperature: Optional[float] = None,
) -> Any:
    """Generate content from Gemini with optional structured output.

    - prompt: user prompt text
    - model: Gemini model name (e.g., 'gemini-1.5-pro', 'gemini-1.5-flash')
    - structured: if True, request JSON output
    - schema: optional JSON Schema dict for structured output
    - temperature: optional sampling temperature
    """

    # Load .env from current or parent directories
    load_dotenv(find_dotenv())
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to your environment or .env file.")

    genai.configure(api_key=api_key)

    generation_config: Dict[str, Any] = {}
    if temperature is not None:
        generation_config["temperature"] = temperature

    if structured:
        # Ask Gemini to return JSON; include schema when provided
        generation_config["response_mime_type"] = "application/json"
        if schema is not None:
            generation_config["response_schema"] = schema

    model_client = genai.GenerativeModel(model_name=model, generation_config=generation_config)
    response = model_client.generate_content(prompt)

    text = getattr(response, "text", None)
    if text is None:
        # Fallback to raw structure
        return response

    if structured:
        try:
            return json.loads(text)
        except Exception:
            return text
    return text


def _parse_schema(schema_arg: Optional[str]) -> Optional[Dict[str, Any]]:
    if not schema_arg:
        return None
    # If schema_arg is a path to a file, load it; else treat as JSON string
    if os.path.exists(schema_arg):
        with open(schema_arg, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(schema_arg)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gemini client test")
    parser.add_argument("--prompt", required=True, help="Prompt to send to Gemini")
    parser.add_argument("--model", default="gemini-1.5-pro")
    parser.add_argument("--structured", action="store_true")
    parser.add_argument("--schema", help="Path to JSON schema file or JSON string", default=None)
    parser.add_argument("--temperature", type=float, default=None)
    args = parser.parse_args()

    result = generate_gemini(
        prompt=args.prompt,
        model=args.model,
        structured=bool(args.structured),
        schema=_parse_schema(args.schema),
        temperature=args.temperature,
    )
    if isinstance(result, (dict, list)):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


