"""
共通モジュール: Kibana API への HTTP 実行と .env 読み込み

責務（これだけ）:
  - .env ファイルから接続情報を読み込む
  - Kibana API への HTTP リクエストを実行する
  - 自己署名証明書の検証スキップ（verify=False）

抽象化はここだけに留める（api-first-code-policy に準拠）。
"""

import json
import os
import sys
import urllib3

import requests

# 自己署名証明書の警告を抑制
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_env(env_path=None):
    """
    .env ファイルを読み込んで辞書で返す。

    探索順:
      1. 引数で指定されたパス
      2. ../04-m365-integration/.env（スクリプトからの相対パス）
      3. 環境変数から直接取得（CI 等で .env がない場合）
    """
    if env_path and os.path.exists(env_path):
        path = env_path
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.join(script_dir, "..", "04-m365-integration", ".env")
        if os.path.exists(candidate):
            path = candidate
        else:
            # .env が見つからない場合は環境変数から取得
            return {
                "KIBANA_URL": os.environ.get("KIBANA_URL", "https://192.168.50.200:5601"),
                "ELASTIC_USER": os.environ.get("ELASTIC_USER", "elastic"),
                "ELASTIC_PASSWORD": os.environ.get("ELASTIC_PASSWORD", ""),
            }

    env = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
    return env


def kibana_api(method, endpoint, env, body=None):
    """
    Kibana API を呼び出して (status_code, response_body) を返す。

    API 呼び出しを隠さない方針のため、endpoint はフルパスで渡す。
    例: "/api/fleet/package_policies"
    """
    url = env["KIBANA_URL"].rstrip("/") + endpoint
    auth = (env["ELASTIC_USER"], env["ELASTIC_PASSWORD"])
    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.request(
            method=method,
            url=url,
            auth=auth,
            headers=headers,
            json=body,
            verify=False,
            timeout=30,
        )
        try:
            resp_body = resp.json()
        except ValueError:
            resp_body = {"raw": resp.text}
        return resp.status_code, resp_body

    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Cannot connect to {url}", file=sys.stderr)
        print(f"  Detail: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"ERROR: Request timed out: {url}", file=sys.stderr)
        sys.exit(1)


def print_json(data):
    """JSON を整形して表示する。"""
    print(json.dumps(data, indent=2, ensure_ascii=False))
