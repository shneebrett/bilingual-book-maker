#!/usr/bin/env python3
"""测试 Gemini 原生 API 格式"""

import requests
import json

API_KEY = "sk-seHxfZz1J3VhyAJsxstWSiQJLZoIIj3WUJpX3NokbZ0cR1KM"
BASE_URL = "https://www.packyapi.com"
MODEL = "gemini-3-flash-preview"

# Gemini 原生 API 格式
endpoint = f"{BASE_URL}/v1beta/models/{MODEL}:generateContent"

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY  # Gemini 使用这个 header
}

# Gemini 原生请求格式
body = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Translate this to Chinese: Mr. Jones, of the Manor Farm, had locked the hen-houses for the night."
                }
            ]
        }
    ]
}

print("=" * 80)
print("Testing Gemini Native API")
print("=" * 80)
print(f"Endpoint: {endpoint}")
print(f"Model: {MODEL}")
print()

try:
    response = requests.post(endpoint, headers=headers, json=body, timeout=30)

    print(f"Status Code: {response.status_code}")
    print()
    print("Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    if response.status_code == 200:
        result = response.json()
        if "candidates" in result and len(result["candidates"]) > 0:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            print()
            print("=" * 80)
            print("Translation Result:")
            print("=" * 80)
            print(text)
        else:
            print()
            print("ERROR: No candidates in response")
    else:
        print()
        print("ERROR: Request failed")

except Exception as e:
    print(f"ERROR: {e}")
