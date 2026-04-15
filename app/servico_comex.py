import re
from datetime import datetime
from typing import Any

import requests


URL_BASE_COMEX = "https://api-comexstat.mdic.gov.br"
TIMEOUT_PADRAO = 30


def extrair_periodo(texto: str) -> tuple[str, str]:
    """
    Extrai um período simples do texto do usuário.

    Exemplos aceitos:
    - "2025"
    - "2025-03"
    - "2025/03"

    Retorna:
    (data_inicial, data_final) no formato YYYY-MM
    """
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
    """
    Consulta o endpoint de dados gerais do Comex Stat.

    A documentação oficial indica POST em /general com campos como:
    flow, monthDetail, period, details e metrics.
    """
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
    """
    Localiza a lista de registros na resposta da API.

    A estrutura real pode variar, então a extração é defensiva.
    """
    if not isinstance(resposta_api, dict):
        return []

    candidatos_diretos = ["data", "list", "items", "results"]
    for chave in candidatos_diretos:
        valor = resposta_api.get(chave)
        if isinstance(valor, list):
            return [item for item in valor if isinstance(item, dict)]

    data = resposta_api.get("data")
    if isinstance(data, dict):
        candidatos_internos = ["data", "list", "items", "results"]
        for chave in candidatos_internos:
            valor = data.get(chave)
            if isinstance(valor, list):
                return [item for item in valor if isinstance(item, dict)]

    return []


def obter_primeiro_valor_existente(registro: dict[str, Any], chaves: list[str]) -> Any:
    """
    Retorna o primeiro valor encontrado dentre várias chaves possíveis.
    """
    for chave in chaves:
        if chave in registro and registro[chave] not in (None, ""):
            return registro[chave]
    return None


def converter_valor_monetario(valor: Any) -> float | None:
    """
    Converte o valor retornado pela API para float, quando possível.
    """
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


def formatar_valor_brl(valor: float | None) -> str:
    """
    Formata um número para exibição amigável.
    """
    if valor is None:
        return "valor não disponível"

    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"US$ {texto}"


def identificar_produto_destaque(registros: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    Procura o registro com maior valor FOB dentro da resposta.

    Como os nomes exatos das chaves podem variar, usamos alternativas.
    """
    if not registros:
        return None

    melhor_registro = None
    maior_valor = -1.0

    for registro in registros:
        valor_bruto = obter_primeiro_valor_existente(
            registro,
            [
                "metricFOB",
                "metricfob",
                "fob",
                "value",
                "valor",
            ],
        )
        valor = converter_valor_monetario(valor_bruto)
        if valor is None:
            continue

        if valor > maior_valor:
            maior_valor = valor
            melhor_registro = registro

    if melhor_registro is None:
        return None

    codigo = obter_primeiro_valor_existente(
        melhor_registro,
        ["ncmCode", "ncm", "code", "codigo"]
    )

    descricao = obter_primeiro_valor_existente(
        melhor_registro,
        ["ncmDescription", "ncm_description", "description", "descricao", "name", "nome"]
    )

    if descricao is None and codigo is not None:
        descricao = f"NCM {codigo}"

    return {
        "codigo": codigo,
        "descricao": descricao or "produto não identificado",
        "valor_fob": maior_valor,
    }


def obter_dados_comex(texto_usuario: str) -> dict[str, Any]:
    """
    Função principal do serviço de Comex.

    MVP:
    - extrai período do texto
    - consulta exportações gerais
    - identifica o produto com maior valor FOB no período
    """
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

    destaque = identificar_produto_destaque(registros)
    if not destaque:
        return {
            "sucesso": False,
            "mensagem": "Os dados foram retornados, mas não consegui identificar o produto de destaque."
        }

    if data_inicial == data_final:
        periodo = data_inicial
    else:
        periodo = f"{data_inicial} a {data_final}"

    return {
        "sucesso": True,
        "tipo": "comex",
        "periodo": periodo,
        "produto": destaque["descricao"],
        "codigo": destaque["codigo"],
        "valor": formatar_valor_brl(destaque["valor_fob"]),
        "valor_numerico": destaque["valor_fob"],
        "mensagem": "Consulta realizada com sucesso."
    }