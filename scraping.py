import os
import time
import pickle
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# .env 読み込み
load_dotenv()

# メールアドレス・パスワード取得
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

# ChromeDriverのパス
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# Cookie ファイルの保存先
cookie_path = os.path.join(os.getcwd(), "cookies.pkl")

# URL
base_url = "https://site3.sbisec.co.jp"
login_url = f"{base_url}/ETGate"


def init_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--ignore-certificate-errors")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def load_cookies(driver):
    if os.path.exists(cookie_path):
        print("✅ Cookie 読み込み中...")
        driver.get(base_url)
        time.sleep(3)
        
        try:
            with open(cookie_path, "rb") as cookie_file:
                cookies = pickle.load(cookie_file)
                valid_cookies = 0
                
                for cookie in cookies:
                    if "domain" in cookie and "sbisec.co.jp" in cookie["domain"]:
                        try:
                            driver.add_cookie(cookie)
                            valid_cookies += 1
                        except Exception as e:
                            print(f"Cookie 追加エラー: {e}")
                
                print(f"✅ {valid_cookies}個の Cookie を読み込みました")
                
            driver.get(login_url)
            time.sleep(8)
            
        except Exception as e:
            print(f"Cookie 読み込みエラー: {e}")
            os.remove(cookie_path)
            print("❌ 破損した Cookie ファイルを削除しました")


def save_cookies(driver):
    with open(cookie_path, "wb") as cookie_file:
        pickle.dump(driver.get_cookies(), cookie_file)
    print("✅ Cookie を保存しました")


def login_with_credentials(driver):
    try:
        user_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "user_id"))
        )
        user_field.send_keys(USER)

        password_field = driver.find_element(By.NAME, "user_password")
        password_field.send_keys(PASSWORD)

        login_button = driver.find_element(By.NAME, "ACT_login")
        login_button.click()

        # メール認証待機
        print("⚠️ パスコードを手動で入力してください...")
        time.sleep(50)

        if check_login_success(driver):
            save_cookies(driver)
        else:
            print("❌ ログイン失敗。Cookie は保存されません。")

    except Exception as e:
        print(f"ログインエラー: {e}")


def check_login_success(driver):
    try:
        alt_logout = driver.find_elements(By.XPATH, "//img[@alt='ログアウト']")
        if alt_logout:
            print(f"✅ alt='ログアウト'の画像が {len(alt_logout)} 個見つかりました")
            return True
    except Exception as e:
        print(f"ログイン確認エラー: {e}")
        return False


def main():
    driver = init_driver()
    driver.get(login_url)
    time.sleep(3)
    load_cookies(driver)
    driver.get(login_url)
    time.sleep(10)

    if check_login_success(driver):
        print("✅ Cookie で自動ログイン成功！")
    else:
        print("📝 通常ログインを試行します...")
        login_with_credentials(driver)

    # 処理終了
    time.sleep(10)
    driver.quit()


if __name__ == "__main__":
    main()