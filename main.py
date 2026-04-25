import requests
import time
from datetime import datetime

RECIPIENTS = ["audi0505@hotmail.com", "ken.fujiwara.sk@nttdocomo.com"]

def extract_prefectures(text):
    # 避難指示関連のキーワード周辺だけを対象に絞る
    keywords = ["避難指示", "緊急安全確保", "高齢者等避難"]
    prefs = ["北海道","青森","岩手","宮城","秋田","山形","福島","茨城","栃木","群馬","埼玉","千葉","東京","神奈川","新潟","富山","石川","福井","山梨","長野","岐阜","静岡","愛知","三重","滋賀","京都","大阪","兵庫","奈良","和歌山","鳥取","島根","岡山","広島","山口","徳島","香川","愛媛","高知","福岡","佐賀","長崎","熊本","大分","宮崎","鹿児島","沖縄"]
    
    found = []
    for kw in keywords:
        pos = text.find(kw)
        if pos != -1:
            # キーワードの前後500文字だけを調べる
            section = text[max(0, pos-500):pos+500]
            for p in prefs:
                if p in section and p not in found:
                    found.append(p)
    return found if found else ["該当地域あり（詳細確認）"]

def check_alert():
    try:
        url = "https://crisis.yahoo.co.jp/evacuation/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=15)
        text = r.text

        has_alert = any(k in text for k in ["避難指示", "緊急安全確保", "高齢者等避難"])

        prefs = extract_prefectures(text)
        prefs_text = "、".join(prefs)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S JST")

        print(f"[{now}] チェック完了 → 避難指示: {has_alert} | 対象: {prefs_text}")

        if has_alert:
            print(f"【緊急】避難指示が検知されました！ 対象: {prefs_text}")

    except Exception as e:
        print("エラー:", e)

if __name__ == "__main__":
    print("避難指示監視ツール起動...")
    while True:
        check_alert()
        time.sleep(600)  # 10分間隔
