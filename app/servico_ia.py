import requests
from app.configuracao import OLLAMA_URL, OLLAMA_MODELO


def gerar_resposta_ia(pergunta_usuario: str, dados: dict) -> str:
    if not dados:
        return "Não consegui processar sua solicitação agora."

    if isinstance(dados, dict) and not dados.get("sucesso", True) and "clima" not in dados and "comex" not in dados:
        return dados.get("mensagem", "Não foi possível processar sua solicitação.")

    eh_resumo = "clima" in dados and "comex" in dados

    if eh_resumo:
        prompt_sistema = (
            "Você é um assistente especialista em agronegócio brasileiro.\n"
            "Responda sempre em português do Brasil.\n\n"

            "Sua tarefa é gerar um resumo interpretativo do cenário atual.\n"
            "Combine as informações de clima e exportações.\n\n"

            "Regras de comportamento:\n"
            "- Seja claro, direto e objetivo.\n"
            "- Use linguagem natural e amigável.\n"
            "- NÃO pareça um robô.\n"
            "- Traga leveza na conversa.\n"
            "- Sempre que possível, faça pequenos comentários naturais.\n"
            "- Pode usar leve humor ou trocadilhos, sem exagero.\n"
            "- Pode reagir à informação.\n"
            "- Pode dar uma opinião leve baseada nos dados.\n"
            "- Não invente informações.\n"
            "- Use apenas os dados fornecidos.\n"
            "- Se faltar informação, diga isso de forma natural.\n\n"

            "Formato das respostas:\n"
            "- Máximo 5 linhas.\n"
            "- Comece com uma noção geral do cenário.\n"
            "- Depois conecte clima e exportações.\n"
            "- Termine com uma conclusão curta.\n"
        )
    else:
        prompt_sistema = (
            "Você é um assistente especialista em agronegócio brasileiro.\n"
            "Responda sempre em português do Brasil.\n\n"

            "Regras de comportamento:\n"
            "- Seja claro, direto e objetivo.\n"
            "- Use linguagem natural e amigável.\n"
            "- NÃO pareça um robô.\n"
            "- Traga leveza na conversa.\n"
            "- Sempre que possível, faça pequenos comentários naturais.\n"
            "- Pode usar leve humor ou trocadilhos, sem exagero.\n"
            "- Pode reagir à informação.\n"
            "- Pode dar uma opinião leve baseada nos dados.\n"
            "- Não invente informações.\n"
            "- Use apenas os dados fornecidos.\n"
            "- Se faltar informação, diga isso de forma natural.\n\n"

            "Formato das respostas:\n"
            "- Respostas curtas, com no máximo 4 linhas.\n"
            "- Use quebras de linha para facilitar leitura.\n"
            "- Destaque as informações principais.\n"
        )

    prompt_usuario = (
        f"Pergunta do usuário:\n{pergunta_usuario}\n\n"
        f"Dados disponíveis:\n{dados}\n\n"
        "Gere uma resposta útil, natural e agradável."
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
            "temperature": 0.5,
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

        return "Não consegui gerar uma resposta agora."

    except requests.RequestException as e:
        print(f"Erro Ollama: {e}")
        return gerar_resposta_fallback(dados)


def gerar_resposta_fallback(dados: dict) -> str:
    if not dados:
        return "Erro ao processar os dados."

    if "clima" in dados and "comex" in dados:
        clima = dados.get("clima", {})
        comex = dados.get("comex", {})

        cidade = clima.get("cidade", "local não identificado")
        descricao = clima.get("descricao", "condição não disponível")
        temperatura = clima.get("temperatura", "N/D")
        produto = comex.get("produto", "produto não identificado")
        valor = comex.get("valor", "valor não disponível")

        return (
            f"Cenário atual:\n"
            f"Em {cidade}, o clima está {descricao}, com {temperatura}°C.\n"
            f"Nas exportações, o destaque é {produto}, com valor de {valor}.\n"
            f"No geral, o cenário parece estável."
        )

    tipo = dados.get("tipo")

    if tipo == "clima":
        return (
            f"Em {dados.get('cidade')} - {dados.get('estado')}, "
            f"o clima está {dados.get('descricao')} com {dados.get('temperatura')}°C."
        )

    if tipo == "comex":
        ranking = dados.get("ranking", "")
        return (
            f"Top exportações no período {dados.get('periodo')}:\n"
            f"{ranking}"
        )

    return "Não consegui gerar uma resposta adequada."