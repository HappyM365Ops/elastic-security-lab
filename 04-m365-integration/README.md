# 04 - Microsoft 365 Integration

Elastic Agent に Microsoft 365 関連の Integration を追加するための設定ファイル群です。

## 前提条件

- Elastic Stack が稼働中（02-elastic-stack-setup 参照）
- Debian ホストに Elastic Agent がインストール済み
- Microsoft Entra ID でアプリ登録が完了していること

## Entra ID アプリ登録

### 1. アプリの登録

- Entra 管理センター → アプリの登録 → 新規登録
- 名前: `Elastic-SIEM-Integration`
- サポートされているアカウントの種類: シングルテナント

### 2. API アクセス許可

| API | 許可 | 種類 |
|-----|------|------|
| Office 365 Management APIs | ActivityFeed.Read | アプリケーション |
| Office 365 Management APIs | ActivityFeed.ReadDlp | アプリケーション |

※ 管理者の同意を付与すること

### 3. クライアントシークレット

- 証明書とシークレット → 新しいクライアントシークレット
- 有効期限: 24 か月
- **値（Value）を必ず控えること**（画面を離れると再表示不可）

## ファイル構成

```
04-m365-integration/
├── README.md
├── .env.example          # 環境変数サンプル
├── office365-integration.json  # Integration テンプレート
└── deploy-office365.sh   # デプロイスクリプト
```

## 使い方

```bash
# 1. 環境変数ファイルを作成
cp .env.example .env
# .env を編集して Client Secret 等を入力

# 2. Integration をデプロイ
chmod +x deploy-office365.sh
./deploy-office365.sh

# 3. 確認
../scripts/list-integrations.sh
```

## 収集されるログ

| Content Type | 内容 |
|-------------|------|
| Audit.AzureActiveDirectory | Entra ID のサインイン・管理操作 |
| Audit.Exchange | Exchange Online の操作ログ |
| Audit.SharePoint | SharePoint / OneDrive の操作ログ |
| Audit.General | その他の M365 サービスのログ |
| DLP.All | DLP ポリシーイベント |

## トラブルシューティング

```bash
# Agent のログを確認（Debian ホスト上で実行）
sudo journalctl -u elastic-agent -f --since "5 minutes ago"

# Discover で検索
# data_stream.dataset : "o365.audit"
```

## 注意事項

- Client Secret は `.env` に記載し、Git にコミットしないこと（.gitignore で除外済み）
- 初回取得は最大7日前（167h55m）からのデータを取得
- ポーリング間隔はデフォルト 3 分
