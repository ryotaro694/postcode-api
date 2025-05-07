import re
from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright, input_address: str) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.post.japanpost.jp/zipcode/")

    try:
        page.get_by_role("textbox", name="市区町村・町名").click()
        page.get_by_role("textbox", name="市区町村・町名").fill(f"{input_address}")
        page.get_by_role("button", name="郵便番号を検索").click()
        page.locator('a.line').first.click()
        page.get_by_text("〒 289-").click()
    except Exception as e:
        print(f"Error occurred: {e}")
    page.close()

    # ---------------------
    context.close()
    browser.close()

def remove_pref_from_address(input_address: str) -> str:
    """
        addressから都道府県を取り除く
    """
    input_address = re.sub(r"^.+?[都道府県]", "", input_address)
    return

def convert_address(input_address: str) -> str:
    """
        住所を変換する
        ×霞ヶ関
        ○霞が関
        ×紀ノ川市
        ○紀の川市
        【新字・旧字】
        ×桧原村
        ○檜原村
    """
    
    input_address = re.sub(r"霞ヶ関", "霞が関", input_address)
    input_address = re.sub(r"紀ノ川市", "紀の川市", input_address)
    input_address = re.sub(r"桧原村", "檜原村", input_address)
    return input_address

def main():
    """
        メイン関数
    """
    
    with sync_playwright() as playwright:
        run(playwright, "千葉県山武郡横芝光町宮川")

if __name__ == "__main__":
    main()