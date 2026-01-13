"""
Custom Gemini translator for PackyAPI relay station
Uses native Gemini API format via HTTP requests
"""

import re
import time
import requests
from os import environ
from rich import print

from .base_translator import Base

PROMPT_ENV_MAP = {
    "user": "BBM_GEMINIAPI_USER_MSG_TEMPLATE",
    "system": "BBM_GEMINIAPI_SYS_MSG",
}


class PackyGemini(Base):
    """
    PackyAPI Gemini translator using native API format
    """

    DEFAULT_PROMPT = "Please help me to translate,`{text}` to {language}, please return only translated content not include the origin text"

    def __init__(
        self,
        key,
        language,
        api_base=None,
        prompt_template=None,
        prompt_sys_msg=None,
        temperature=1.0,
        **kwargs,
    ) -> None:
        super().__init__(key, language)
        self.api_base = api_base or "https://www.packyapi.com"
        self.prompt = (
            prompt_template
            or environ.get(PROMPT_ENV_MAP["user"])
            or self.DEFAULT_PROMPT
        )
        self.prompt_sys_msg = (
            prompt_sys_msg or environ.get(PROMPT_ENV_MAP["system"]) or None
        )
        self.temperature = temperature
        self.interval = 3
        self.model = "gemini-3-flash-preview"  # Default model

    def set_model_list(self, model_list):
        """Set the model to use"""
        if model_list and len(model_list) > 0:
            self.model = model_list[0]

    def set_geminiflash_models(self):
        """Set flash model"""
        self.model = "gemini-3-flash-preview"

    def set_geminipro_models(self):
        """Set pro model"""
        self.model = "gemini-3-pro-preview"

    def set_interval(self, interval):
        """Set request interval"""
        self.interval = interval

    def rotate_key(self):
        """Rotate to next API key"""
        # Keys are rotated automatically in translate() via next(self.keys)
        # This method is required by base class but no action needed
        pass

    def translate(self, text):
        delay = 1
        exponential_base = 2

        print(re.sub("\n{3,}", "\n\n", text))

        # Get API key once at the start
        api_key = next(self.keys)

        for attempt in range(3):
            try:
                # Format the prompt
                prompt_text = self.prompt.format(text=text, language=self.language)

                # Build request body in Gemini native format
                body = {"contents": [{"parts": [{"text": prompt_text}]}]}

                # Add system instruction if provided
                if self.prompt_sys_msg:
                    body["systemInstruction"] = {"parts": [{"text": self.prompt_sys_msg}]}

                # Add generation config
                body["generationConfig"] = {"temperature": self.temperature}

                # Build endpoint URL
                endpoint = f"{self.api_base}/v1beta/models/{self.model}:generateContent"

                # Make request
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                }

                response = requests.post(
                    endpoint, headers=headers, json=body, timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    if "candidates" in result and len(result["candidates"]) > 0:
                        t_text = result["candidates"][0]["content"]["parts"][0]["text"]
                        print("[bold green]" + re.sub("\n{3,}", "\n\n", t_text) + "[/bold green]")
                        time.sleep(self.interval)
                        return t_text
                    else:
                        raise Exception("No candidates in response")
                else:
                    error_msg = response.text
                    raise Exception(f"API error {response.status_code}: {error_msg}")

            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}, retrying...")
                time.sleep(delay)
                delay *= exponential_base
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt < 2:
                    time.sleep(delay)
                    delay *= exponential_base
                else:
                    raise

        raise Exception("Translation failed after 3 attempts")
