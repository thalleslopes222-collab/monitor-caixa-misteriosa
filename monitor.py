import os
import requests
import time

# ===================== CONFIGURAÇÃO =====================
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
INTERVALO = 3  # segundos entre cada consulta
# ========================================================

ENDPOINT = "https://www.webcontinental.com.br/_v/box-showcase"
LANDING = "https://www.webcontinental.com.br/caixa-misteriosa"
ACTIVE_WORDS = ["ativo", "ativa", "liberado", "liberada", "disponivel", "disponível", "aberto", "aberta"]

seen_keys = set()

def send_telegram_alert(message, url):
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "🛒 ABRIR VITRINE AGORA", "url": url}
            ]]
        }
    }
    try:
        requests.post(api_url, json=payload, timeout=5)
    except Exception as e:
        print(f"Erro ao enviar alerta para o Telegram: {e}")

def check_boxes():
    global seen_keys
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(ENDPOINT, headers=headers, timeout=8)
        if response.status_code != 200:
            print(f"[{time.strftime('%H:%M:%S')}] Erro HTTP: {response.status_code}")
            return
        
        data = response.json()
        items = data.get("itens", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        
        for i, item in enumerate(items):
            status = str(item.get("status", "")).strip().lower()
            ordem = item.get("ordem", f"i{i}")
            sku = item.get("sku", "")
            sku2 = item.get("sku2", "")
            hash_code = item.get("hash", "")
            
            key = f"{ordem}|{sku}|{sku2}|{status}"
            
            is_active = status in ACTIVE_WORDS or (hash_code and (sku or sku2))
            
            if is_active and key not in seen_keys:
                seen_keys.add(key)
                msg = f"🚨 <b>CAIXA MISTERIOSA LIBERADA!</b> 🚨\n\nStatus: <i>{status.upper()}</i>\nCorra para o site antes que esgote!"
                print(f"[{time.strftime('%H:%M:%S')}] CAIXA LIBERADA! Enviando notificação...")
                send_telegram_alert(msg, LANDING)
                
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Erro de conexão: {e}")

print("🚀 Monitor da Caixa Misteriosa rodando em Python...")
send_telegram_alert("✅ <b>Monitor Iniciado</b>\nO robô está ativo e consultando a vitrine.", LANDING)

while True:
    check_boxes()
    time.sleep(INTERVALO)