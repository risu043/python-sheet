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


def wait_for_login_success(driver, timeout=30):
    try:
        print("✅ ログイン状態をチェック中...")
        WebDriverWait(driver, timeout).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, '//*[@id="logout"]')),
                EC.presence_of_element_located((By.XPATH, '//*[@id="skipMsg"]/button')),
                EC.presence_of_element_located((By.XPATH, '//*[@id="mymenuSec"]/div/div[2]/div/div[2]/div[1]/div[2]/a[1]'))
            )
        )
        print("✅ ログイン成功を確認しました")
        return True
    except Exception as e:
        print(f"❌ ログイン確認タイムアウト: {e}")
        return False
        

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

        if wait_for_login_success(driver, timeout=30):
            save_cookies(driver)
        else:
            print("❌ ログイン失敗。Cookie は保存されません。")

    except Exception as e:
        print(f"ログインエラー: {e}")


def main():
    driver = init_driver()
    driver.get(login_url)
    time.sleep(5)
    
    login_with_credentials(driver)
    time.sleep(5)

    driver.quit()


if __name__ == "__main__":
    main()