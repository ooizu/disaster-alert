import requests
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

RECIPIENTS = ["audi0505@hotmail.com", "ken.fujiwara.sk@nttdocomo.com"]

# ================== Gmail設定（必ず変更）==================
GMAIL_ADDRESS = "あなたのGmailアドレス@gmail.com"          # ← ここを変更
GMAIL_APP_PASSWORD = "ここにアプリパスワードを入力"       # ← 必須！
# =======================================================

def extract_prefectures(text):
    keywords = ["避難指示", "緊急安全確保", "高齢者等避難"]
    prefs = ["北海道","青森","岩手","宮城","秋田","山形","福島","茨城","栃木","群馬","埼玉","千葉","東京","神奈川","新潟","富山","石川","福井","山梨","長野","岐阜","静岡","愛知","三重","滋賀","京都","大阪","兵庫","奈良","和歌山","鳥取","島根","岡山","広島","山口","徳島","香川","愛媛","高知","福岡","佐賀","長崎","熊本","大分","宮崎","鹿児島","沖縄"]
    
    found = []
    for kw in keywords:
        pos = text.find(kw)
        if pos != -1:
            section = text[max(0, pos-600):pos+600]
            for p in prefs:
                if p in section and p not in found:
                    found.append(p)
    return found if found else ["該当地域あり（詳細確認）"]

def send_email(subject, body):
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = ", ".join(RECIPIENTS)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, RECIPIENTS, msg.as_string())
        server.quit()
        print("✅ メールを送信しました！")
    except Exception as e:
        print("❌ メール送信エラー:", e)

def check_alert():
    try:
        url = "https://crisis.yahoo.co.jp/evacuation/"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        text = r.text

        has_alert = any(k in text for k in ["避難指示", "緊急安全確保", "高齢者等避難"])
        prefs = extract_prefectures(text)
        prefs_text = "、".join(prefs)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S JST")

        print(f"[{now}] チェック完了 → 避難指示: {has_alert} | 対象: {prefs_text}")

        if has_alert:
            subject = "【緊急】避難指示が発令されました"
            body = f"対象地域: {prefs_text}\n\n検知時刻: {now}\n詳細ページ: {url}\n\n※これは自動監視ツールです。\n必ずYahoo!防災速報アプリで確認してください。"
            send_email(subject, body)

    except Exception as e:
        print("エラー:", e)

if __name__ == "__main__":
    print("避難指示監視ツール起動...")
    while True:
        check_alert()
        time.sleep(600)  # 10分間隔
