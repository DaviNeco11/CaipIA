import requests
from app.configuracao import OLLAMA_URL, OLLAMA_MODELO


def gerar_resposta_ia(pergunta_usuario: str, dados: dict) -> str:
    if not dados:
        return "Não foi possível processar sua solicitação."

    # 🔹 Prompt de sistema otimizado para o modelo PT-BR
    prompt_sistema = (
        "Você é um assistente especializado em agronegócio brasileiro. "
        "Responda sempre em português do Brasil, de forma clara, direta e útil. "
        "Use apenas os dados fornecidos. Não invente informações. "
        "Se os dados estiverem incompletos, explique isso de forma natural."
    )

    # 🔹 Prompt com contexto
    prompt_usuario = (
        f"Pergunta do usuário:\n{pergunta_usuario}\n\n"
        f"Dados disponíveis:\n{dados}\n\n"
        "Gere uma resposta objetiva, natural e útil para o usuário."
    )

    url = f"{OLLAMA_URL}/api/chat"

    payload = {
        "model": OLLAMA_MODELO,
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,   # mais preciso
            "top_p": 0.9
        }
    }

    try:
        resposta = requests.post(url, json=payload, timeout=120)
        resposta.raise_for_status()

        dados_resposta = resposta.json()

        texto = dados_resposta.get("message", {}).get("content")

        if texto:
            return texto.strip()

        return "Não consegui gerar uma resposta no momento."

    except requests.RequestException as e:
        print(f"Erro Ollama: {e}")
        return gerar_resposta_fallback(dados)


# 🔁 fallback caso o Ollama falhe
def gerar_resposta_fallback(dados: dict) -> str:
    if not dados:
        return "Erro ao processar dados."

    tipo = dados.get("tipo")

    if tipo == "clima":
        return (
            f"Clima em {dados.get('cidade')} - {dados.get('estado')}: "
            f"{dados.get('descricao')}, "
            f"{dados.get('temperatura')}°C."
        )

    if tipo == "comex":
        return (
            f"Exportações ({dados.get('periodo')}): "
            f"{dados.get('produto')} com valor de {dados.get('valor')}."
        )

    if "clima" in dados and "comex" in dados:
        return (
            f"Clima: {dados['clima'].get('descricao')} em {dados['clima'].get('cidade')}. "
            f"Exportações: destaque para {dados['comex'].get('produto')}."
        )

    return "Não consegui gerar resposta."