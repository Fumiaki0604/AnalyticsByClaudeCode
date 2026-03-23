"""
各Googleアカウントの OAuth 認証を行いトークンを保存するスクリプト。
使い方: python auth.py <サイト名 or メールアドレス>
例:    python auth.py しまむら
       python auth.py f_sato@atoj.co.jp
"""

import json
import sys
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, "accounts.json")
CLIENT_SECRET = os.path.join(BASE_DIR, "client_secret.json")


def load_accounts():
    with open(ACCOUNTS_FILE, encoding="utf-8") as f:
        return json.load(f)["accounts"]


def find_account(keyword):
    accounts = load_accounts()
    for acc in accounts:
        if keyword in acc["email"]:
            return acc
        for prop in acc["properties"]:
            if keyword in prop["name"]:
                return acc
    return None


def authenticate(account):
    token_path = os.path.join(BASE_DIR, account["token_file"])
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print(f"トークンを更新しました: {account['email']}")
        else:
            print(f"\nブラウザで {account['email']} としてログインしてください...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
            print(f"認証成功: {account['email']}")

        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 引数なしの場合は全アカウントを順番に認証
        accounts = load_accounts()
        print(f"{len(accounts)} アカウントを順番に認証します\n")
        for acc in accounts:
            print(f"--- {acc['email']} ---")
            authenticate(acc)
        print("\n全アカウントの認証完了！")
    else:
        keyword = sys.argv[1]
        account = find_account(keyword)
        if not account:
            print(f"アカウントが見つかりません: {keyword}")
            sys.exit(1)
        authenticate(account)
        print(f"\nトークン保存完了: {account['token_file']}")
