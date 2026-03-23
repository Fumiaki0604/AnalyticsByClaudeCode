# GA4 Analysis by Claude Code

Claude Code のチャットから GA4 データを取得・分析するツール。

## セットアップ

### 1. リポジトリをクローン
```bash
git clone <このリポジトリのURL>
cd AnalyticsByClaudeCode
```

### 2. ライブラリをインストール
```bash
pip install google-analytics-data google-auth-oauthlib
```

### 3. client_secret.json を配置
管理者から受け取った `client_secret.json` をこのフォルダに置く。

### 4. 認証（ブラウザが開くので各自のGoogleアカウントでログイン）
```bash
python auth.py
```

以上でセットアップ完了。あとは Claude Code のチャットで話しかけるだけ。

## 使い方（Claude Code から）

```
しまむらの先月のPVを教えて
アンククロスのチャネル別セッションを見せて
カドストのモバイル×オーガニックの購入率は？
```

## サイト一覧

| サイト名 | アカウント |
|---------|----------|
| しまむら | f_sato@atoj.co.jp |
| アンククロス | infoatoj3@gmail.com |
| カドスト | kado.ecb@gmail.com |
