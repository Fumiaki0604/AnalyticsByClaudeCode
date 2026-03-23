# GA4 Analysis by Claude Code

Claude Code のチャットから GA4 データを取得・分析するツール。

## セットアップ

### 1. リポジトリをクローン

ターミナル（PowerShell or コマンドプロンプト）を開き、ファイルを置きたい場所に移動してから以下を実行。
クローンすると `AnalyticsByClaudeCode` フォルダが自動で作成されます。

```bash
# 例: Cドライブ直下に置く場合
cd C:\
git clone https://github.com/Fumiaki0604/AnalyticsByClaudeCode.git
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

## 認証が切れた場合

通常はトークンが自動更新されるため何もしなくて大丈夫です。
エラーが出てデータが取得できなくなった場合は、以下を実行してください。

```bash
python auth.py
```

ブラウザが開くので、各自のGoogleアカウントでログインしなおせば復旧します。

## 使い方（Claude Code から）

```
サイトAの先月のPVを教えて
サイトBのチャネル別セッションを見せて
サイトCのモバイル×オーガニックの購入率は？
```
