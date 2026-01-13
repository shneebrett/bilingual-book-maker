#!/usr/bin/env python3
"""测试中转站API的完整追踪脚本"""

import requests
import json
import time
from typing import Dict, Any


def print_separator(title: str = ""):
    """打印分隔线"""
    print("\n" + "=" * 80)
    if title:
        print(f" {title} ".center(80, "="))
        print("=" * 80)


def mask_api_key(key: str) -> str:
    """隐藏API Key的部分字符"""
    if len(key) <= 10:
        return key
    return f"{key[:8]}...{key[-4:]}"


def print_request_info(method: str, url: str, headers: Dict, body: Dict):
    """打印请求信息"""
    print_separator("[REQUEST]")
    print(f"Method: {method}")
    print(f"URL: {url}")
    print(f"\nHeaders:")
    for key, value in headers.items():
        if key.lower() == "authorization":
            print(f"  {key}: Bearer {mask_api_key(value.replace('Bearer ', ''))}")
        else:
            print(f"  {key}: {value}")
    print(f"\nBody:")
    print(json.dumps(body, indent=2, ensure_ascii=False))


def print_response_info(response: requests.Response):
    """打印响应信息"""
    print_separator("[RESPONSE]")
    print(f"Status Code: {response.status_code} {response.reason}")
    print(f"\nHeaders:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    print(f"\nBody:")
    try:
        json_data = response.json()
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(response.text)


def test_chat_completion(api_key: str, base_url: str, model: str, stream: bool = False):
    """测试聊天完成API"""
    endpoint = f"{base_url}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello, this is a test message. Please respond briefly."}
        ],
        "stream": stream
    }

    print_request_info("POST", endpoint, headers, body)

    try:
        start_time = time.time()

        if stream:
            # 流式响应
            response = requests.post(endpoint, headers=headers, json=body, stream=True, timeout=30)

            print_separator("[RESPONSE] (STREAMING)")
            print(f"Status Code: {response.status_code} {response.reason}")
            print(f"\nHeaders:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")

            print(f"\nStreaming Content:")
            print("-" * 80)

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(decoded_line)
                    if decoded_line.startswith("data: ") and decoded_line != "data: [DONE]":
                        try:
                            json_data = json.loads(decoded_line[6:])
                            print(f"  → Parsed: {json.dumps(json_data, ensure_ascii=False)}")
                        except json.JSONDecodeError:
                            pass
        else:
            # 非流式响应
            response = requests.post(endpoint, headers=headers, json=body, timeout=30)
            print_response_info(response)

        elapsed_time = time.time() - start_time
        print_separator("[TIMING]")
        print(f"Request completed in {elapsed_time:.2f} seconds")

        # 检查响应状态
        if response.status_code == 200:
            print_separator("[SUCCESS]")
            print("API call completed successfully!")
        else:
            print_separator("[ERROR]")
            print(f"API call failed with status code: {response.status_code}")

    except requests.exceptions.Timeout:
        print_separator("[ERROR]")
        print("Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError as e:
        print_separator("[ERROR]")
        print(f"Connection error: {e}")
    except requests.exceptions.RequestException as e:
        print_separator("[ERROR]")
        print(f"Request error: {e}")
    except Exception as e:
        print_separator("[ERROR]")
        print(f"Unexpected error: {type(e).__name__}: {e}")


def main():
    """主函数"""
    API_KEY = "sk-X13SEBiTbMjD2bLkkxTpxay6X2lLf4i58yK9xfRb7ZQ6AbXC"
    BASE_URLS = [
        "https://www.packyapi.com",
        "https://api-slb.packyapi.com"
    ]
    MODEL = "gemini-3-pro-preview"

    print_separator("[START] API Testing")
    print(f"Model: {MODEL}")
    print(f"API Key: {mask_api_key(API_KEY)}")
    print(f"\nTesting {len(BASE_URLS)} endpoints:")
    for i, url in enumerate(BASE_URLS, 1):
        print(f"  {i}. {url}")

    for base_url_index, base_url in enumerate(BASE_URLS, 1):
        print("\n\n")
        print("=" * 80)
        print(f" ENDPOINT {base_url_index}: {base_url} ".center(80, "="))
        print("=" * 80)

        # 测试非流式响应
        print("\n")
        print("-" * 80)
        print(" Non-Streaming Request ".center(80, "-"))
        print("-" * 80)
        test_chat_completion(API_KEY, base_url, MODEL, stream=False)

        # 测试流式响应
        print("\n")
        print("-" * 80)
        print(" Streaming Request ".center(80, "-"))
        print("-" * 80)
        test_chat_completion(API_KEY, base_url, MODEL, stream=True)

    print("\n")
    print_separator("[DONE] Testing Complete")


if __name__ == "__main__":
    main()
