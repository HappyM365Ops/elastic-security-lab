#!/bin/bash
# ============================================================
# list-integrations.sh
# Fleet に登録済みの Integration 一覧を表示する
#
# 使い方:
#   ./list-integrations.sh
#   ./list-integrations.sh | jq '.items[].name'
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# .env を探す（scripts/ から実行された場合は親ディレクトリも探す）
if [ -f "${SCRIPT_DIR}/.env" ]; then
  source "${SCRIPT_DIR}/.env"
elif [ -f "${SCRIPT_DIR}/../04-m365-integration/.env" ]; then
  source "${SCRIPT_DIR}/../04-m365-integration/.env"
else
  # デフォルト値
  KIBANA_URL="${KIBANA_URL:-https://192.168.50.200:5601}"
  ELASTIC_USER="${ELASTIC_USER:-elastic}"
  ELASTIC_PASSWORD="${ELASTIC_PASSWORD:-elasticpass2026}"
fi

echo "=== Registered Integrations ==="
echo ""

curl -sk \
  -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
  "${KIBANA_URL}/api/fleet/package_policies" \
  -H "kbn-xsrf: true" \
  | python3 -m json.tool \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data.get('items', []):
    pkg = item.get('package', {})
    print(f\"  [{item.get('id', 'N/A')[:8]}] {item.get('name', 'N/A'):30s} {pkg.get('name', 'N/A'):20s} v{pkg.get('version', '?')}\")
"
