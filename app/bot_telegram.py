import requests
import time

from app.configuracao import TELEGRAM_TOKEN, URL_API


if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN não definido no .env")


URL_TELEGRAM = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def enviar_mensagem(chat_id: int, texto: str):
    url = f"{URL_TELEGRAM}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": texto
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except requests.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")


def obter_updates(offset=None):
    url = f"{URL_TELEGRAM}/getUpdates"

    params = {
        "timeout": 100,
        "offset": offset
    }

    try:
        resposta = requests.get(url, params=params, timeout=120)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as e:
        print(f"Erro ao obter updates: {e}")
        return None


def processar_mensagem(update):
    try:
        mensagem = update.get("message")

        if not mensagem:
            return

        texto = mensagem.get("text")
        chat_id = mensagem["chat"]["id"]

        if not texto:
            enviar_mensagem(chat_id, "Envie uma mensagem de texto.")
            return

        # 🔗 Chamada para o backend
        resposta = requests.post(
            f"{URL_API}/mensagem",
            json={"texto": texto},
            timeout=15
        )

        resposta.raise_for_status()
        dados = resposta.json()

        texto_resposta = dados.get("resposta", "Não consegui gerar resposta.")

        enviar_mensagem(chat_id, texto_resposta)

    except requests.RequestException as e:
        print(f"Erro ao chamar API: {e}")
        enviar_mensagem(chat_id, "Erro ao processar sua solicitação.")

    except Exception as e:
        print(f"Erro inesperado: {e}")


def iniciar_bot():
    print("🤖 Bot iniciado...")

    offset = None

    while True:
        dados = obter_updates(offset)

        if dados and "result" in dados:
            for update in dados["result"]:
                offset = update["update_id"] + 1
                processar_mensagem(update)

        time.sleep(1)


# ▶️ Ponto de entrada
if __name__ == "__main__":
    iniciar_bot()