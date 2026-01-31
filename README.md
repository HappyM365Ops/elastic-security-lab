# Elastic Security Lab

自宅環境で Elastic Security (SIEM/EDR) を学ぶための検証環境です。

## 🎯 プロジェクトの目的

- プログラム未経験者が AI（Claude / ChatGPT）の力を借りて IaC エンジニアを目指す
- Elastic Security の実践的な知識を身につける
- 学習過程をブログとして公開し、同じ境遇の人の役に立つ

## 🏠 検証環境

| 項目 | 値 |
|------|-----|
| ホスト OS | Debian 13 (trixie) |
| CPU | Intel N100 |
| メモリ | 16GB |
| Docker | 27.x |
| Elastic Stack | 8.17.0 |

### ネットワーク構成
```
インターネット
      │
  [HGW] 192.168.0.1
      │
[Wi-Fi ルータ] 192.168.50.1
      │
      ├── Debian 13 (192.168.50.200) ← Elastic Stack
      ├── Windows 11 PC
      ├── Windows 10 PC
      └── その他デバイス
```

## 📁 ディレクトリ構成
```
elastic-security-lab/
├── README.md
├── LICENSE
├── .gitignore
└── 02-elastic-stack-setup/     # Elastic Stack 環境構築
    ├── .env.example            # 環境変数のサンプル
    ├── docker-compose.yml      # コンテナ定義
    └── kibana.yml              # Kibana + Fleet 設定
```

## 🚀 セットアップ手順

### 1. 事前準備（Docker ホスト側）
```bash
# vm.max_map_count の設定（Elasticsearch 8.16+ で必須）
sudo sysctl -w vm.max_map_count=1048576
echo "vm.max_map_count=1048576" | sudo tee /etc/sysctl.d/99-elasticsearch.conf
```

### 2. ファイルの配置
```bash
# リポジトリをクローン
git clone https://github.com/HappyM365Ops/elastic-security-lab.git
cd elastic-security-lab/02-elastic-stack-setup

# 環境変数ファイルを作成
cp .env.example .env

# 必要に応じて .env を編集
# - HOST_IP: Docker ホストの IP アドレス
# - ELASTIC_PASSWORD: elastic ユーザのパスワード
# - KIBANA_PASSWORD: kibana_system ユーザのパスワード
```

### 3. 初回起動（CA 証明書の取得）
```bash
# コンテナを起動（setup が証明書を生成）
docker compose up -d

# setup コンテナが完了するまで待機（1-2分）
docker compose logs -f setup

# CA 証明書を取得
docker run --rm \
  -v 02-elastic-stack-setup_certs:/certs \
  alpine cat /certs/ca/ca.crt
```

### 4. kibana.yml に CA 証明書を設定

取得した CA 証明書を `kibana.yml` の `certificate_authorities` セクションに貼り付けます。

### 5. 再起動
```bash
# kibana.yml 更新後、再起動
docker compose down
docker compose up -d
```

### 6. 動作確認

- Kibana: https://<HOST_IP>:5601
- ユーザー: `elastic`
- パスワード: `.env` で設定した `ELASTIC_PASSWORD`

Fleet → Agents で Fleet Server が「Healthy」と表示されれば完了です。

## 📝 ブログ記事

- **第0章**: 環境構築編（執筆中）

## 📚 参考リンク

- [Elastic 公式ドキュメント](https://www.elastic.co/guide/index.html)
- [Fleet and Elastic Agent Guide](https://www.elastic.co/guide/en/fleet/current/index.html)
- [Getting started with Docker Compose](https://www.elastic.co/blog/getting-started-with-the-elastic-stack-and-docker-compose)

## 📄 ライセンス

MIT License