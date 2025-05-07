from playwright.sync_api import sync_playwright, Error as PlaywrightError
from logging import getLogger

logger = getLogger(__name__)

JPPOST_URL = "https://www.post.japanpost.jp/zipcode/"

def fetch_postal_code(address: str, pref_code: int | None) -> dict:
    """
    指定された住所から郵便番号を取得する
    
    Args:
        address (str): 検索する住所
        
    Returns:
        dict: 郵便番号情報を含む辞書 {"postal_code": "XXX-XXXX", "status": "success"} または {"status": "error", "message": "エラーメッセージ"}
    """
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(JPPOST_URL)
            if pref_code:
                pref_selector = page.locator('select[name="pref"]')
                pref_selector.select_option(str(pref_code))
            page.get_by_role("textbox", name="市区町村・町名").click()
            page.get_by_role("textbox", name="市区町村・町名").fill(f"{address}")
            page.get_by_role("button", name="郵便番号を検索").click()
        
            try:
                locator = page.locator('a.line').first
                locator.wait_for(timeout=1000)
                if locator:
                    locator.click()
                    
                    zipcode_element = page.locator('span.zip-code')
                    zipcode_element.wait_for(timeout=1000)
                    if zipcode_element:
                        zipcode_text = zipcode_element.text_content().strip()
                        # "〒 XXX-XXXX" 形式から数字部分だけを抽出
                        postal_code = ''.join(c for c in zipcode_text if c.isdigit() or c == '-')
                        return {"postal_code": postal_code, "status": "success"}
                    else:
                        logger.warning("郵便番号要素が見つかりませんでした")
                        return {"status": "error", "message": "郵便番号要素が見つかりませんでした"} 
                    # address_element = page.locator('div.searchResults') 
                    # print(address_element.inner_html())
                
                else:
                    # 検索結果がない場合
                    logger.info("検索した住所は見つかりませんでした")
                    return {"status": "error", "message": "検索した住所は見つかりませんでした"}

            except PlaywrightError as e:
                logger.error(f"要素の操作中にエラーが発生しました: {e}")
                return {"status": "error", "message": f"要素の操作中にエラーが発生しました: {str(e)}"}
            finally:
                page.close()
                context.close()
                browser.close()
        except Exception as e:
            logger.error(f"郵便番号取得中に予期しないエラーが発生しました: {e}")
            return {"status": "error", "message": f"郵便番号取得中に予期しないエラーが発生しました: {str(e)}"}
