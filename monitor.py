import os, requests, bs4, json, pathlib, time
from dotenv import load_dotenv 
load_dotenv()                    
URL = "https://ticket.pia.jp/sp/ticketInformation.do?eventCd=2523084&rlsCd=001"
WEBHOOK = os.getenv("SLACK_WEBHOOK")
STATUS_FILE = pathlib.Path("last_status.json")

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

def fetch_status():
    with sync_playwright() as p:
        desktop_ua = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=desktop_ua)

        # 1) LP かもしれないので最初は何でも受け止める
        page.goto(URL, wait_until="networkidle", timeout=30000)

        # 2) LP だったらリンクを踏む
        if "lp/event.do" in page.url:
            link = page.query_selector('a[href*="ticketInformation.do"]')
            if link:
                link.click()
                page.wait_for_load_state("networkidle")

        # 3) 最大 30 秒粘って HTML を取得
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except PWTimeout:
            pass  # ネットワークが静かにならなくても続行

        html = page.content()

        # 4) キーワードで判定
        if "発売中" in html:
            status = "発売中"
        elif "受付中" in html:
            status = "受付中"
        elif "予定枚数終了" in html:
            status = "予定枚数終了"
        else:
            status = "unknown"

        browser.close()
        return status


def notify(msg):
    if WEBHOOK:
        requests.post(WEBHOOK, json={"text": msg}, timeout=10)

def load_last():
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text()).get("status", "")
    return ""

def save_last(s): STATUS_FILE.write_text(json.dumps({"status": s}))

if __name__ == "__main__":
    last = load_last()
    while True:
        try:
            now = fetch_status()
            print(time.strftime("%F %T"), now)
            if now != last and now in ("発売中", "受付中"):
                notify(f"🎫 販売開始！ {URL}")
            last = now
            save_last(last)
        except Exception as e:
            print("ERROR:", e)
        time.sleep(60)
