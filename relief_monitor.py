# relief_monitor.py  ---  RELIEF Ticket 監視 (Playwright 版)
import os, requests, time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
URL      = "https://relief-ticket.jp/events/artist/16/105"
WEBHOOK  = os.getenv("SLACK_WEBHOOK")
UA       = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36")

def notify(msg: str):
    if WEBHOOK:
        requests.post(WEBHOOK, json={"text": msg}, timeout=10)

def button_is_active() -> bool:
    """有効な『購入手続きへ』ボタンが 1 つでもあれば True"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=UA, viewport={"width":1280,"height":800})
        page.goto(URL, wait_until="networkidle", timeout=30000)

        # ボタンをすべて走査し「テキスト一致 & 表示中 & disabled 属性が無い」を探す
        found = page.evaluate("""
        () => [...document.querySelectorAll('button')]
              .some(btn => btn.innerText.trim().includes('購入手続きへ')
                        && !btn.disabled
                        && btn.offsetParent !== null)
        """)
        browser.close()
        return found

if __name__ == "__main__":
    status = "在庫あり" if button_is_active() else "在庫なし"
    print(time.strftime("%F %T"), status)
    if status == "在庫あり":
        notify(f"🎫 RELIEF Ticket 販売開始！\n<{URL}|公演一覧を開く>")
