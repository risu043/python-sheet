import os

# Cookie ファイルの保存先
cookie_path = os.path.join(os.getcwd(), "cookies.pkl")

def delete_cookies():
    if os.path.exists(cookie_path):
        try:
            os.remove(cookie_path)
            print("✅ Cookie ファイルを削除しました")
        except Exception as e:
            print(f"❌ Cookie ファイル削除エラー: {e}")
    else:
        print("⚠️ Cookie ファイルが見つかりません")

if __name__ == "__main__":
    delete_cookies()