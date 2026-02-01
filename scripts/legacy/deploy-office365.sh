#!/bin/bash
# ============================================================
# deploy-office365.sh
# Office 365 Integration を Kibana Fleet API で登録する
#
# 使い方:
#   1. .env ファイルに必要な値を設定
#   2. ./deploy-office365.sh
#
# 前提条件:
#   - Entra ID にアプリ登録済み (Elastic-SIEM-Integration)
#   - API アクセス許可: ActivityFeed.Read, ActivityFeed.ReadDlp
#   - 管理者の同意を付与済み
# ============================================================

set -euo pipefail

# .env ファイルの読み込み
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: .env file not found at $ENV_FILE"
  echo "Copy .env.example to .env and fill in the values."
  exit 1
fi

source "$ENV_FILE"

# 必須変数のチェック
for var in KIBANA_URL ELASTIC_USER ELASTIC_PASSWORD AGENT_POLICY_ID \
           AZURE_TENANT_ID O365_CLIENT_ID O365_CLIENT_SECRET; do
  if [ -z "${!var:-}" ]; then
    echo "ERROR: $var is not set in .env"
    exit 1
  fi
done

# テンプレートの変数を置換
JSON_TEMPLATE="${SCRIPT_DIR}/office365-integration.json"
JSON_BODY=$(cat "$JSON_TEMPLATE" \
  | sed "s|\${AGENT_POLICY_ID}|${AGENT_POLICY_ID}|g" \
  | sed "s|\${AZURE_TENANT_ID}|${AZURE_TENANT_ID}|g" \
  | sed "s|\${O365_CLIENT_ID}|${O365_CLIENT_ID}|g" \
  | sed "s|\${O365_CLIENT_SECRET}|${O365_CLIENT_SECRET}|g"
)

echo "=== Deploying Office 365 Integration ==="
echo "Kibana URL: ${KIBANA_URL}"
echo "Agent Policy: ${AGENT_POLICY_ID}"
echo ""

# API リクエスト
RESPONSE=$(curl -sk -w "\n%{http_code}" \
  -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
  -X POST "${KIBANA_URL}/api/fleet/package_policies" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d "$JSON_BODY"
)

# レスポンスの解析
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  echo "SUCCESS: Office 365 Integration deployed."
  echo "$BODY" | python3 -m json.tool 2>/dev/null | head -20
else
  echo "ERROR: HTTP ${HTTP_CODE}"
  echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
fi
