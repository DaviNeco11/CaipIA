def gerar_resposta_ia(pergunta_usuario: str, dados: dict) -> str:
    """
    Gera uma resposta amigável com base nos dados retornados pelos serviços.
    Versão simples (sem LLM externo).
    """

    if not dados or not dados.get("sucesso"):
        return dados.get("mensagem", "Não foi possível processar sua solicitação.")

    tipo = dados.get("tipo")

    if tipo == "clima":
        return gerar_resposta_clima(dados)

    elif tipo == "comex":
        return gerar_resposta_comex(dados)

    elif "clima" in dados and "comex" in dados:
        return gerar_resposta_resumo(dados)

    return "Não consegui gerar uma resposta adequada."


# 🌦️ Resposta para clima
def gerar_resposta_clima(dados: dict) -> str:
    cidade = dados.get("cidade")
    estado = dados.get("estado")
    temperatura = dados.get("temperatura")
    descricao = dados.get("descricao")
    umidade = dados.get("umidade")

    resposta = (
        f"📍 Clima em {cidade} - {estado}\n"
        f"🌡️ Temperatura: {temperatura}°C\n"
        f"🌤️ Condição: {descricao}\n"
        f"💧 Umidade: {umidade}%\n"
    )

    return resposta


# 🌾 Resposta para Comex
def gerar_resposta_comex(dados: dict) -> str:
    produto = dados.get("produto")
    valor = dados.get("valor")
    periodo = dados.get("periodo")

    resposta = (
        f"📊 Exportações do Agro ({periodo})\n"
        f"🌾 Produto destaque: {produto}\n"
        f"💰 Valor exportado: {valor}\n"
    )

    return resposta


# 🧠 Resumo combinado
def gerar_resposta_resumo(dados: dict) -> str:
    clima = dados.get("clima", {})
    comex = dados.get("comex", {})

    cidade = clima.get("cidade")
    descricao = clima.get("descricao")
    temperatura = clima.get("temperatura")

    produto = comex.get("produto")
    valor = comex.get("valor")

    resposta = (
        f"📍 Cenário geral\n\n"
        f"🌦️ Em {cidade}, o clima está {descricao} com temperatura de {temperatura}°C.\n"
        f"🌾 No comércio exterior, o produto em destaque é {produto}, "
        f"com valor exportado de {valor}.\n"
        f"\n📌 Esse cenário indica condições típicas do período, sendo importante acompanhar variações climáticas e de mercado."
    )

    return resposta