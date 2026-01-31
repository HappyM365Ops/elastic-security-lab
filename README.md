# Elastic Security Lab

自宅環境で Elastic Security (SIEM/EDR) を学習するための検証環境です。

## 概要

AI（Claude/ChatGPT）の力を借りながら、プログラム未経験から IaC エンジニアを目指す学習記録。
Docker Compose で Elastic Stack を構築し、セキュリティ監視の基礎を学びます。

## 環境

- ホスト OS: Debian 13 (trixie)
- Elastic Stack: 8.17.0
- ハードウェア: Intel N100 / 16GB RAM

## ネットワーク構成
```
インターネット
      |
   [HGW] 192.168.0.1
      |
[Wi-Fi ルータ] 192.168.50.1
      |
      |── ミニPC (192.168.50.200) ← Elastic Stack
      |── Windows 11 PC
      |── Windows 10 PC
      └── その他デバイス
```

## 注意事項

- **検証環境専用**: 本番環境での利用は非推奨
- **セキュリティ**: `.env` ファイルの取り扱いに注意

## ライセンス

MIT License