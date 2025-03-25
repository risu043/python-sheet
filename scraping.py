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


def wait_for_page_load(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("✅ ページの読み込み完了")
    except Exception as e:
        print(f"❌ ページ読み込みエラー: {e}")


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


def load_cookies(driver):
    if os.path.exists(cookie_path):
        print("✅ Cookie 読み込み中...")
        driver.get(base_url)
        wait_for_page_load(driver)

        try:
            with open(cookie_path, "rb") as cookie_file:
                cookies = pickle.load(cookie_file)
                valid_cookies = 0

                driver.execute_cdp_cmd("Network.enable", {})
                for cookie in cookies:
                    if "domain" in cookie and "sbisec.co.jp" in cookie["domain"]:
                        try:
                            driver.execute_cdp_cmd("Network.setCookie", cookie)
                            valid_cookies += 1
                        except Exception as e:
                            print(f"Cookie 追加エラー: {e}")

                print(f"✅ {valid_cookies} 個の Cookie を読み込みました")

            driver.refresh()
            wait_for_page_load(driver)

            if wait_for_login_success(driver):
                print("✅ Cookie による自動ログイン成功")
            else:
                print("❌ Cookie ではログインできませんでした")

        except Exception as e:
            print(f"❌ Cookie 読み込みエラー: {e}")
    else:
        print("⚠️ Cookie ファイルが見つかりません。")


def click_button(driver, xpath, timeout=10):
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        button.click()
        wait_for_page_load(driver)
    except Exception as e:
        print(f"❌ ボタンクリックエラー: {e}")


def check_element(driver, xpath, timeout=80):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        print(f"✅ 要素を発見しました: {xpath}")
        return element
    except Exception as e:
        print(f"❌ 要素チェックエラー ({xpath}): {e}")
        return None


def switch_to_new_tab(driver):
    try:
        # 開いているタブのハンドルを取得
        window_handles = driver.window_handles
        
        if len(window_handles) > 1:
            driver.switch_to.window(window_handles[-1])  # 最新のタブに切り替え
            print("✅ 新しいタブに切り替えました")
            wait_for_page_load(driver)
        else:
            print("⚠️ 新しいタブが開かれていません")
    except Exception as e:
        print(f"❌ タブ切り替えエラー: {e}")


def main():
    driver = init_driver()
    driver.get(login_url)
    wait_for_page_load(driver)

    load_cookies(driver)

    # 「あとで見る」ボタンをクリック
    click_button(driver, '//*[@id="skipMsg"]/button')

    # 「My資産」ボタンをクリック
    click_button(driver, '//*[@id="mymenuSec"]/div/div[2]/div/div[2]/div[1]/div[2]/a[1]')

    switch_to_new_tab(driver)

    # 各「評価額」を取得
    investment_trust = check_element(driver, '//*[@id="balance"]/ul/li[2]/div[2]/p')
    deposit = check_element(driver, '//*[@id="balance"]/ul/li[3]/div[2]/p')

    if investment_trust:
        print(f"投資信託: {investment_trust.text}")
    else:
        print("❌ 投資信託の情報を取得できませんでした")

    if deposit:
        print(f"預り金: {deposit.text}")
    else:
        print("❌ 預り金の情報を取得できませんでした")


    
    time.sleep(5)
    
    driver.quit()


if __name__ == "__main__":
    main()