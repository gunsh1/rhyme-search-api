#!/usr/bin/env python3
"""
OpenAI API設定確認スクリプト
"""
import os
import openai
import requests

def check_openai_api_key():
    """OpenAI API Keyの設定状況を確認"""
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY環境変数が設定されていません")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ OPENAI_API_KEYの形式が正しくありません")
        return False
    
    print(f"✅ OPENAI_API_KEY設定済み: {api_key[:10]}...")
    
    # API接続テスト
    try:
        openai.api_key = api_key
        # 簡単なテスト呼び出し
        response = openai.models.list()
        print("✅ OpenAI API接続成功")
        return True
    except Exception as e:
        print(f"❌ OpenAI API接続エラー: {e}")
        return False

def check_railway_deployment():
    """Railwayデプロイメントの状況確認"""
    url = "https://web-production-96e2c.up.railway.app/"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Railway API正常動作中")
            return True
        else:
            print(f"⚠️ Railway API応答エラー: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Railway接続エラー: {e}")
        return False

def test_rap_generation():
    """ラップ生成機能のテスト"""
    url = "https://web-production-96e2c.up.railway.app/api/generate-rap-suggestions"
    data = {"theme": "希望", "style": "modern"}
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ 完全なAI機能で動作中")
            else:
                print("⚠️ モック実装で動作中（OpenAI API未設定）")
            return True
        else:
            print(f"❌ ラップ生成エラー: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ラップ生成テストエラー: {e}")
        return False

def main():
    print("🔍 OpenAI API設定状況の確認\n")
    
    print("1. OpenAI API Key確認")
    openai_ok = check_openai_api_key()
    
    print("\n2. Railway デプロイメント確認")
    railway_ok = check_railway_deployment()
    
    print("\n3. ラップ生成機能テスト")
    rap_ok = test_rap_generation()
    
    print("\n" + "="*50)
    if openai_ok and railway_ok and rap_ok:
        print("🎉 すべて正常に動作しています！")
        print("ChatGPT Custom GPTで完全なAI機能が利用可能です。")
    elif railway_ok:
        print("⚠️ 基本機能は動作していますが、完全なAI機能には")
        print("   OpenAI API Keyの設定が必要です。")
        print("\n設定手順:")
        print("1. https://platform.openai.com でAPI Keyを取得")
        print("2. RailwayのVariablesタブでOPENAI_API_KEYを設定")
        print("3. デプロイメントを再起動")
    else:
        print("❌ 問題が発生しています。ログを確認してください。")

if __name__ == "__main__":
    main()
