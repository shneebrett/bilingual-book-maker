"""
PackyGPT translator for PackyAPI GPT models
Uses OpenAI-compatible API format via HTTP requests
"""

import re
import time
import requests
from os import environ
from rich import print

from .base_translator import Base

PROMPT_ENV_MAP = {
    "user": "BBM_PACKYGPT_USER_MSG_TEMPLATE",
    "system": "BBM_PACKYGPT_SYS_MSG",
}


class PackyGPT(Base):
    """
    PackyAPI GPT translator using OpenAI-compatible API format
    """

    DEFAULT_PROMPT = "Please help me to translate,`{text}` to {language}, please return only translated content not include the origin text"

    def __init__(
        self,
        key,
        language,
        api_base=None,
        prompt_template=None,
        prompt_sys_msg=None,
        temperature=0.3,
        **kwargs,
    ) -> None:
        super().__init__(key, language)
        self.api_base = api_base or "https://www.packyapi.com/v1"
        self.prompt = (
            prompt_template
            or environ.get(PROMPT_ENV_MAP["user"])
            or self.DEFAULT_PROMPT
        )
        self.prompt_sys_msg = (
            prompt_sys_msg
            or environ.get(PROMPT_ENV_MAP["system"])
            or "You are a professional translator."
        )
        self.temperature = temperature
        self.interval = 1
        # Model fallback list - try GPT models first, then fall back to Claude models
        self.model_list = [
            "gpt-5.1", "gpt-5", "gpt-5.1-chat", "gpt-5.2-chat", "gpt-5-chat",
            "claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001",
            "claude-opus-4-5-20251101", "claude-3-5-haiku-20241022"
        ]
        self.current_model_index = 0
        self.model = self.model_list[self.current_model_index]

    def set_model_list(self, model_list):
        """Set the model to use"""
        if model_list and len(model_list) > 0:
            self.model = model_list[0]

    def set_interval(self, interval):
        """Set request interval"""
        self.interval = interval

    def rotate_key(self):
        """Rotate to next API key"""
        pass

    def translate(self, text):
        delay = 3  # Start with 3 seconds delay
        exponential_base = 2

        # Clean text for Windows console output - use encode/decode to handle all problematic chars
        try:
            safe_text = text.encode('gbk', errors='replace').decode('gbk')
        except:
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
        print(re.sub("\n{3,}", "\n\n", safe_text))

        api_key = next(self.keys)

        # Allow enough attempts to try all models plus retries
        max_attempts = len(self.model_list) + 5

        for attempt in range(max_attempts):
            try:
                prompt_text = self.prompt.format(text=text, language=self.language)

                body = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.prompt_sys_msg},
                        {"role": "user", "content": prompt_text},
                    ],
                    "temperature": self.temperature,
                }

                endpoint = f"{self.api_base}/chat/completions"

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                }

                response = requests.post(
                    endpoint, headers=headers, json=body, timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        choice = result["choices"][0]
                        finish_reason = choice.get("finish_reason")

                        # Handle content filter
                        if finish_reason == "content_filter":
                            print(f"[yellow]Content filtered, returning original text[/yellow]")
                            return text

                        message = choice.get("message", {})
                        if "content" in message:
                            t_text = message["content"].strip()
                            try:
                                safe_output = t_text.encode('gbk', errors='replace').decode('gbk')
                            except:
                                safe_output = t_text.encode('ascii', errors='replace').decode('ascii')
                            print("[bold green]" + re.sub("\n{3,}", "\n\n", safe_output) + "[/bold green]")
                            time.sleep(self.interval)
                            return t_text
                        else:
                            raise Exception(f"No content in message: {result}")
                    else:
                        raise Exception(f"No choices in response: {result}")
                else:
                    error_msg = response.text
                    # Handle rate limit specifically
                    if response.status_code == 429:
                        print(f"[yellow]Rate limit hit on attempt {attempt + 1}, waiting {delay * 2} seconds...[/yellow]")
                        time.sleep(delay * 2)
                        delay *= exponential_base
                        continue

                    # Handle model_not_found error - try fallback models
                    if response.status_code == 503 and "model_not_found" in error_msg:
                        if self.current_model_index < len(self.model_list) - 1:
                            self.current_model_index += 1
                            self.model = self.model_list[self.current_model_index]
                            print(f"[yellow]Model not found, switching to {self.model}...[/yellow]")
                            continue
                        else:
                            print(f"[red]All models failed, no more fallback options[/red]")

                    raise Exception(f"API error {response.status_code}: {error_msg}")

            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}, retrying...")
                time.sleep(delay)
                delay *= exponential_base
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                    delay *= exponential_base
                else:
                    raise

        raise Exception(f"Translation failed after {max_attempts} attempts")
