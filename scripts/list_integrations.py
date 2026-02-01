#!/usr/bin/env python3
"""
Integration 一覧表示

API 呼び出し:
  GET /api/fleet/package_policies

処理の流れ:
  1. .env 読み込み
  2. GET でIntegration一覧を取得
  3. 一覧を整形表示（フルID）
"""

import os
import sys

# common.py を同ディレクトリからインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_env, kibana_api, print_json


def main():
    env = load_env()

    # --- GET: Integration 一覧取得 ---
    print("=== Registered Integrations ===")
    print()

    status, body = kibana_api("GET", "/api/fleet/package_policies", env)

    if status != 200:
        print(f"ERROR: HTTP {status}")
        print_json(body)
        sys.exit(1)

    items = body.get("items", [])
    if not items:
        print("No integrations found.")
        return

    # ヘッダー
    print(f"  {'ID':<40} {'Name':<35} {'Package':<20} {'Version'}")
    print(f"  {'-'*40} {'-'*35} {'-'*20} {'-'*10}")

    for item in items:
        policy_id = item.get("id", "???")
        name = item.get("name", "???")
        pkg = item.get("package", {})
        pkg_name = pkg.get("name", "???")
        pkg_version = pkg.get("version", "???")

        print(f"  {policy_id:<40} {name:<35} {pkg_name:<20} {pkg_version}")

    print()
    print(f"  Total: {len(items)} integration(s)")


if __name__ == "__main__":
    main()
