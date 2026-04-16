import re
from datetime import datetime
from typing import Any

import requests


URL_BASE_COMEX = "https://api-comexstat.mdic.gov.br"
TIMEOUT_PADRAO = 30


def extrair_periodo(texto: str) -> tuple[str, str]:
    texto = texto.lower()

    resultado_mes = re.search(r"\b(20\d{2})[-/](0[1-9]|1[0-2])\b", texto)
    if resultado_mes:
        ano = resultado_mes.group(1)
        mes = resultado_mes.group(2)
        periodo = f"{ano}-{mes}"
        return periodo, periodo

    resultado_ano = re.search(r"\b(20\d{2})\b", texto)
    if resultado_ano:
        ano = resultado_ano.group(1)
        return f"{ano}-01", f"{ano}-12"

    hoje = datetime.now()
    periodo_atual = hoje.strftime("%Y-%m")
    return periodo_atual, periodo_atual


def consultar_exportacoes_gerais(data_inicial: str, data_final: str) -> dict[str, Any] | None:
    url = f"{URL_BASE_COMEX}/general"
    params = {"language": "pt"}

    payload = {
        "flow": "export",
        "monthDetail": False,
        "period": {
            "from": data_inicial,
            "to": data_final
        },
        "details": ["ncm"],
        "metrics": ["metricFOB"]
    }

    try:
        resposta = requests.post(url, params=params, json=payload, timeout=TIMEOUT_PADRAO)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException:
        return None


def extrair_registros(resposta_api: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(resposta_api, dict):
        return []

    for chave in ["data", "list", "items", "results"]:
        valor = resposta_api.get(chave)
        if isinstance(valor, list):
            return [item for item in valor if isinstance(item, dict)]

    data = resposta_api.get("data")
    if isinstance(data, dict):
        for chave in ["data", "list", "items", "results"]:
            valor = data.get(chave)
            if isinstance(valor, list):
                return [item for item in valor if isinstance(item, dict)]

    return []


def obter_primeiro_valor_existente(registro: dict[str, Any], chaves: list[str]) -> Any:
    for chave in chaves:
        if chave in registro and registro[chave] not in (None, ""):
            return registro[chave]
    return None


def converter_valor_monetario(valor: Any) -> float | None:
    if valor is None:
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

    if isinstance(valor, str):
        valor_limpo = valor.strip().replace(".", "").replace(",", ".")
        try:
            return float(valor_limpo)
        except ValueError:
            return None

    return None


def formatar_valor_usd(valor: float | None) -> str:
    if valor is None:
        return "valor não disponível"

    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"US$ {texto}"


def obter_dados_produto(registro: dict[str, Any]) -> dict[str, Any] | None:
    valor_bruto = obter_primeiro_valor_existente(
        registro,
        ["metricFOB", "metricfob", "fob", "value", "valor"]
    )
    valor = converter_valor_monetario(valor_bruto)
    if valor is None:
        return None

    codigo = obter_primeiro_valor_existente(
        registro,
        ["ncmCode", "ncm", "code", "codigo"]
    )

    descricao = obter_primeiro_valor_existente(
        registro,
        ["ncmDescription", "ncm_description", "description", "descricao", "name", "nome"]
    )

    if descricao is None and codigo is not None:
        descricao = f"NCM {codigo}"

    return {
        "codigo": codigo,
        "descricao": descricao or "produto não identificado",
        "valor_fob": valor,
        "valor_formatado": formatar_valor_usd(valor),
    }


def obter_top_produtos(registros: list[dict[str, Any]], limite: int = 3) -> list[dict[str, Any]]:
    produtos = []

    for registro in registros:
        produto = obter_dados_produto(registro)
        if produto:
            produtos.append(produto)

    produtos_ordenados = sorted(
        produtos,
        key=lambda item: item["valor_fob"],
        reverse=True
    )

    return produtos_ordenados[:limite]


def obter_dados_comex(texto_usuario: str) -> dict[str, Any]:
    data_inicial, data_final = extrair_periodo(texto_usuario)

    resposta_api = consultar_exportacoes_gerais(data_inicial, data_final)
    if not resposta_api:
        return {
            "sucesso": False,
            "mensagem": "Não foi possível consultar o Comex Stat no momento."
        }

    registros = extrair_registros(resposta_api)
    if not registros:
        return {
            "sucesso": False,
            "mensagem": "Não encontrei dados de exportação para o período informado."
        }

    top_produtos = obter_top_produtos(registros, limite=3)
    if not top_produtos:
        return {
            "sucesso": False,
            "mensagem": "Os dados foram retornados, mas não consegui identificar os produtos de destaque."
        }

    if data_inicial == data_final:
        periodo = data_inicial
    else:
        periodo = f"{data_inicial} a {data_final}"

    produto_principal = top_produtos[0]

    ranking_texto = []
    for i, produto in enumerate(top_produtos, start=1):
        ranking_texto.append(
            f"{i}. {produto['descricao']} - {produto['valor_formatado']}"
        )

    return {
        "sucesso": True,
        "tipo": "comex",
        "periodo": periodo,
        "produto": produto_principal["descricao"],
        "codigo": produto_principal["codigo"],
        "valor": produto_principal["valor_formatado"],
        "valor_numerico": produto_principal["valor_fob"],
        "top_produtos": top_produtos,
        "ranking": "\n".join(ranking_texto),
        "mensagem": "Consulta realizada com sucesso."
    }