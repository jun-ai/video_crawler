import requests
import json
import base64
import os

def main():
    # 从环境变量或直接设置
    api_key = os.getenv("BAIDU_API_KEY", "c3z2ATVHIvPNQcXROhi6I4sm")
    secret_key = os.getenv("BAIDU_SECRET_KEY", "MzubQrW4akF2Iyt2n5NtTTZKHbE23Tkz")

    # 1. 获取 access token
    print("=" * 50)
    print("步骤1: 获取 Access Token")
    print("=" * 50)

    token_url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "client_id": api_key,
        "client_secret": secret_key,
        "grant_type": "client_credentials"
    }

    response = requests.post(token_url, params=params)
    print("Status Code:", response.status_code)

    if response.status_code != 200:
        print("获取Token失败:", response.text)
        return

    data = response.json()
    access_token = data.get("access_token")
    print("Access Token 获取成功!")
    print("Token:", access_token[:50] + "...")
    print("Expires In:", data.get("expires_in"), "秒")

    # 2. 测试语音识别API
    print("\n" + "=" * 50)
    print("步骤2: 测试语音识别 API")
    print("=" * 50)

    # 创建一个简单的测试PCM音频（静音，仅测试API连通性）
    test_audio = b'\x00' * 32000  # 1秒的静音PCM (16000Hz, 16bit, mono)

    # 测试不同的API端点
    endpoints = [
        {
            "name": "标准版 (server_api)",
            "url": f"https://vop.baidu.com/server_api?access_token={access_token}"
        },
        {
            "name": "极速版 (pro_api)",
            "url": f"https://vop.baidu.com/pro_api?access_token={access_token}"
        }
    ]

    cuid = "VideoCrawlerApp01"

    for endpoint in endpoints:
        print(f"\n测试端点: {endpoint['name']}")
        print("-" * 40)

        payload = {
            "format": "pcm",
            "rate": 16000,
            "channel": 1,
            "cuid": cuid,
            "token": access_token,
            "dev_pid": 1737,  # 英语
            "speech": base64.b64encode(test_audio).decode('utf-8'),
            "len": len(test_audio)
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(endpoint['url'], json=payload, headers=headers)
        result = response.json()

        err_no = result.get("err_no", -1)
        err_msg = result.get("err_msg", "未知错误")

        if err_no == 0:
            print("✓ 成功! 识别结果:", result.get("result", []))
            break
        elif err_no == 3301:
            print("✓ API连通正常!")
            print("  (错误3301: 音频质量过差/静音，但说明API调用成功)")
            break
        else:
            print(f"✗ 错误{err_no}: {err_msg}")
            print(f"  完整响应: {json.dumps(result, ensure_ascii=False)}")

    # 3. 测试不带dev_pid的方式
    print("\n" + "=" * 50)
    print("步骤3: 测试简化参数")
    print("=" * 50)

    simple_url = f"https://vop.baidu.com/server_api?access_token={access_token}"

    # 极简参数
    simple_payload = {
        "format": "pcm",
        "rate": 16000,
        "channel": 1,
        "cuid": "test001",
        "token": access_token,
        "speech": base64.b64encode(test_audio).decode('utf-8'),
        "len": len(test_audio)
    }

    response = requests.post(simple_url, json=simple_payload, headers=headers)
    result = response.json()
    print("响应:", json.dumps(result, ensure_ascii=False))

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == '__main__':
    main()
