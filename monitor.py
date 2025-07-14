# relief_monitor.py  ---  RELIEF Ticket 監視
import os, requests, time
from dotenv import load_dotenv

load_dotenv()
URL      = "https://relief-ticket.jp/events/artist/16/105"
WEBHOOK  = os.getenv("SLACK_WEBHOOK")
KEYWORD  = "購入手続きへ"                    # ボタン文字
UA       = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36")

def notify(msg: str):
    if WEBHOOK:
        requests.post(WEBHOOK, json={"text": msg}, timeout=10)

def has_stock() -> bool:
    html = requests.get(URL, headers={"User-Agent": UA}, timeout=15).text
    return KEYWORD in html

if __name__ == "__main__":
    status = "在庫あり" if has_stock() else "在庫なし"
    print(time.strftime("%F %T"), status)
    if status == "在庫あり":
        notify(f"🎫 RELIEF Ticket 販売開始！\n<{URL}|公演一覧>")


