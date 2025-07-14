import os, requests, time
from dotenv import load_dotenv

load_dotenv()
URL      = "https://relief-ticket.jp/events/artist/16/105"
WEBHOOK  = os.getenv("SLACK_WEBHOOK")
KEYWORD  = "購入手続きへ"

def notify(msg):
    if WEBHOOK:
        requests.post(WEBHOOK, json={"text": msg}, timeout=10)

def sales_status():
    html = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}).text
    return "在庫あり" if KEYWORD in html else "在庫なし"

if __name__ == "__main__":
    now = sales_status()
    print(time.strftime("%F %T"), now)
    if now == "在庫あり":
        notify(f"🎫 RELIEF Ticket 販売開始！\n<{URL}|公演一覧>")
