#!/bin/bash
# ============================================================
# delete-integration.sh
# Fleet から指定した Integration を削除する
#
# 使い方:
#   ./delete-integration.sh <package_policy_id>
#
# ID は list-integrations.sh で確認できる
# ============================================================

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <package_policy_id>"
  echo ""
  echo "Get the ID from: ./list-integrations.sh"
  exit 1
fi

POLICY_ID="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# .env を探す
if [ -f "${SCRIPT_DIR}/.env" ]; then
  source "${SCRIPT_DIR}/.env"
elif [ -f "${SCRIPT_DIR}/../04-m365-integration/.env" ]; then
  source "${SCRIPT_DIR}/../04-m365-integration/.env"
else
  KIBANA_URL="${KIBANA_URL:-https://192.168.50.200:5601}"
  ELASTIC_USER="${ELASTIC_USER:-elastic}"
  ELASTIC_PASSWORD="${ELASTIC_PASSWORD:-elasticpass2026}"
fi

echo "=== Deleting Integration: ${POLICY_ID} ==="
echo ""
read -p "Are you sure? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
  echo "Cancelled."
  exit 0
fi

RESPONSE=$(curl -sk -w "\n%{http_code}" \
  -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
  -X POST "${KIBANA_URL}/api/fleet/package_policies/delete" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d "{\"packagePolicyIds\":[\"${POLICY_ID}\"]}"
)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  echo "SUCCESS: Integration deleted."
else
  echo "ERROR: HTTP ${HTTP_CODE}"
  echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
fi
