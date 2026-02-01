#!/usr/bin/env python3
"""
Office 365 Integration デプロイ

API 呼び出し:
  POST /api/fleet/package_policies
  Body: office365-integration.json（プレースホルダー置換済み）

処理の流れ:
  1. .env 読み込み
  2. JSON テンプレートを読み込み、プレースホルダーを .env の値で置換（plan）
  3. POST で Integration を作成（apply）
  4. レスポンスを確認（verify）

プレースホルダー:
  ${AGENT_POLICY_ID}  → .env の AGENT_POLICY_ID
  ${AZURE_TENANT_ID}  → .env の AZURE_TENANT_ID
  ${O365_CLIENT_ID}   → .env の O365_CLIENT_ID
  ${O365_CLIENT_SECRET} → .env の O365_CLIENT_SECRET
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from common import load_env, kibana_api, print_json


def main():
    # .env は 04-m365-integration/.env を優先
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env")
    env = load_env(env_path)

    # --- plan: JSON テンプレート読み込み + プレースホルダー置換 ---
    template_path = os.path.join(script_dir, "office365-integration.json")
    if not os.path.exists(template_path):
        print(f"ERROR: Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    with open(template_path, "r") as f:
        template_text = f.read()

    # プレースホルダーを置換
    replacements = {
        "${AGENT_POLICY_ID}": env.get("AGENT_POLICY_ID", ""),
        "${AZURE_TENANT_ID}": env.get("AZURE_TENANT_ID", ""),
        "${O365_CLIENT_ID}": env.get("O365_CLIENT_ID", ""),
        "${O365_CLIENT_SECRET}": env.get("O365_CLIENT_SECRET", ""),
    }

    json_text = template_text
    for placeholder, value in replacements.items():
        if not value:
            print(f"WARNING: {placeholder} is empty in .env", file=sys.stderr)
        json_text = json_text.replace(placeholder, value)

    try:
        body = json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON after placeholder replacement: {e}", file=sys.stderr)
        sys.exit(1)

    print("=== Deploying Office 365 Integration ===")
    print(f"  Kibana URL: {env.get('KIBANA_URL', '???')}")
    print(f"  Agent Policy: {env.get('AGENT_POLICY_ID', '???')}")
    print()

    # --- apply: POST で Integration 作成 ---
    status, resp = kibana_api("POST", "/api/fleet/package_policies", env, body=body)

    # --- verify: レスポンスを確認 ---
    if status == 200:
        item = resp.get("item", {})
        integration_id = item.get("id", "???")
        name = item.get("name", "???")
        print(f"SUCCESS: Office 365 Integration deployed.")
        print(f"  ID:   {integration_id}")
        print(f"  Name: {name}")
    else:
        print(f"ERROR: HTTP {status}")
        print_json(resp)
        sys.exit(1)


if __name__ == "__main__":
    main()
