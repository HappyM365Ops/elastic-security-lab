#!/usr/bin/env python3
"""
Integration 削除

API 呼び出し:
  POST /api/fleet/package_policies/delete
  Body: {"packagePolicyIds": ["<full_id>"]}

処理の流れ:
  1. .env 読み込み
  2. 削除対象の ID を引数から取得
  3. 確認プロンプト表示
  4. POST で削除実行（apply）
  5. レスポンスボディの success フィールドで結果判定（verify）

注意:
  Fleet API は HTTP 200 を返しつつ body 内で失敗を返すことがある。
  必ず body の success フィールドを確認する。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_env, kibana_api, print_json


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 delete_integration.py <package_policy_id>")
        print()
        print("Get the full ID from: python3 list_integrations.py")
        sys.exit(1)

    policy_id = sys.argv[1]
    env = load_env()

    # --- plan: 削除対象を表示 ---
    print(f"=== Deleting Integration ===")
    print(f"  Target ID: {policy_id}")
    print()

    confirm = input("Are you sure? (y/N): ")
    if confirm.lower() != "y":
        print("Cancelled.")
        sys.exit(0)

    # --- apply: POST で削除実行 ---
    status, body = kibana_api(
        "POST",
        "/api/fleet/package_policies/delete",
        env,
        body={"packagePolicyIds": [policy_id]},
    )

    # --- verify: レスポンスを確認 ---
    # Fleet API は HTTP 200 でも body 内に失敗情報を返すことがある
    if status != 200:
        print(f"ERROR: HTTP {status}")
        print_json(body)
        sys.exit(1)

    # body はリスト形式 [{"id": "...", "success": true/false, ...}]
    if isinstance(body, list) and len(body) > 0:
        result = body[0]
        if result.get("success"):
            name = result.get("name", "unknown")
            print(f"SUCCESS: Integration '{name}' (ID: {policy_id}) deleted.")
        else:
            print(f"ERROR: Deletion failed.")
            print_json(result)
            sys.exit(1)
    else:
        print("WARNING: Unexpected response format.")
        print_json(body)


if __name__ == "__main__":
    main()
