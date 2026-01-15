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

# Model groups configuration - easily extensible for future groups
# Groups are tried in order: azure (GPT) first, then aws-q (Claude) as fallback
MODEL_GROUPS = [
    {
        "name": "azure",
        "key": "sk-3EmK8sw89BeHZ0sJdQYOAQq5IiGLzc884tekMnQ9PuMpLWm5",
        "endpoint": "https://www.packyapi.com/v1",
        "models": [
            "gpt-5.2-chat",
            "gpt-5.1-chat",
            "gpt-5.1",
            "gpt-5-chat",
            "gpt-5"
        ]
    },
    {
        "name": "aws-q",
        "key": "sk-lVSvpyVQvPsJ2jVVt9JXDayinlIZB3ZoSRTMK4rZPNxLDFtg",
        "endpoint": "https://www.packyapi.com/v1",
        "models": [
            "claude-sonnet-4-5-20250929",
            "claude-opus-4-5-20251101",
            "claude-haiku-4-5-20251001"
        ]
    }
]


class PackyGPT(Base):
    """
    PackyAPI GPT translator using OpenAI-compatible API format
    Supports multiple model groups with automatic fallback
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

        # Use model groups for organized fallback
        self.model_groups = MODEL_GROUPS
        self.current_group_index = 0
        self.current_model_index = 0

        # Set initial group and model
        self._update_current_config()

    def _update_current_config(self):
        """Update current API configuration based on group and model indices"""
        if self.current_group_index < len(self.model_groups):
            current_group = self.model_groups[self.current_group_index]
            self.api_base = current_group["endpoint"]
            self.api_key = current_group["key"]
            if self.current_model_index < len(current_group["models"]):
                self.model = current_group["models"][self.current_model_index]
            else:
                self.model = current_group["models"][0]
        else:
            # Fallback to first group if index out of range
            self.current_group_index = 0
            self.current_model_index = 0
            self._update_current_config()

    def _try_next_model(self):
        """Try next model in current group, or move to next group"""
        current_group = self.model_groups[self.current_group_index]

        # Try next model in current group
        if self.current_model_index < len(current_group["models"]) - 1:
            self.current_model_index += 1
            self._update_current_config()
            return True

        # Try next group
        if self.current_group_index < len(self.model_groups) - 1:
            self.current_group_index += 1
            self.current_model_index = 0
            self._update_current_config()
            return True

        # No more options
        return False

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

        # Clean text for Windows console output
        try:
            safe_text = text.encode('gbk', errors='replace').decode('gbk')
        except:
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
        print(re.sub("\n{3,}", "\n\n", safe_text))

        # Calculate total models across all groups
        total_models = sum(len(group["models"]) for group in self.model_groups)
        max_attempts = total_models + 5  # Extra attempts for retries

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
                    "Authorization": f"Bearer {self.api_key}",
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

                    # Handle model_not_found error - try next model/group
                    if response.status_code == 503 and "model_not_found" in error_msg:
                        current_group = self.model_groups[self.current_group_index]
                        print(f"[yellow]Model {self.model} not found in group '{current_group['name']}'[/yellow]")

                        if self._try_next_model():
                            new_group = self.model_groups[self.current_group_index]
                            print(f"[yellow]Switching to group '{new_group['name']}', model: {self.model}[/yellow]")
                            continue
                        else:
                            print(f"[red]All model groups exhausted, no more fallback options[/red]")

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
