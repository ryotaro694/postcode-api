from fastapi import FastAPI, Query, HTTPException
import re
from logging import getLogger
from app.scrapers.jppost_scraper import fetch_postal_code
from app.utils.prefectures import get_prefectures

logging = getLogger(__name__)
app = FastAPI()

PREFECTURES_DIC = get_prefectures()

@app.get("/")
def get_post_code(address: str = Query(
    ..., 
    alias="address",
    title="Address",
    description="郵便番号を検索したい住所（都道府県を含むほうが望ましい）。最大100文字。",
    max_length=100,
)) -> dict:
    """
    住所から郵便番号を取得するエンドポイント
    
    Args: 
        address (str): 検索したい住所
        
    Returns:
        dict: 郵便番号を含む辞書 {"postal_code": "XXX-XXXX"} または {"error": "エラーメッセージ"}
    """
    try:
        # 住所の前処理
        address, pref = _remove_pref_from_address(address)
        address = _transform_address(address)
        result = fetch_postal_code(address, PREFECTURES_DIC.get(pref))
        
        if result.get("status") == "success":
            return {"postal_code": result.get("postal_code")}
        else:
            raise HTTPException(status_code=404, detail=result.get("message"))
    except Exception as e:
        logging.error(f"郵便番号取得中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail=f"郵便番号取得中にエラーが発生しました: {str(e)}")

def _remove_pref_from_address(address: str) -> tuple[str, str | None]:
    """
    住所から都道府県を取り除く

    Args:
        address(str): 住所

    Returns:
        address(str): 都道府県を取り除いた住所
        pref(str | None): 都道府県
    """
    prefectures_list = list(PREFECTURES_DIC.keys())
    pref = None

    pattern = f"{'|'.join(prefectures_list)}"
    match = re.match(pattern, address)

    if match:
        pref = match.group(0)
        address = address[len(pref):]
    return address.strip(), pref

def _transform_address(address: str) -> str:
    """
    ルールベース

    Args:
        address (str): The input address to be transformed.

    Returns:
        str: The transformed address with replacements applied.
    
    Notes：
        https://www.post.japanpost.jp/cgi-zip/zipcode.php <- 入力のヒントに関して記述がある
        - 霞ヶ関 -> 霞が関
        - 紀ノ川市 -> 紀の川市
        - 桧原村 -> 檜原村
    """

    transformations = {
        "霞ヶ関": "霞が関",
        "紀ノ川市": "紀の川市",
        "桧原村": "檜原村"
    }
 
    for old, new in transformations.items():
        address = re.sub(old, new, address)

    return address
