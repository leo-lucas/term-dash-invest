#!/usr/bin/env python3
"""Dashboard de investimentos no terminal."""

from __future__ import annotations

import argparse
import csv
import re
import urllib.request
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, List


@dataclass
class Ativo:
    nome: str
    preco_medio: Decimal
    quantidade: Decimal
    preco_atual: Decimal
    categoria: str
    ticker: str

    @property
    def total_investido(self) -> Decimal:
        return self.preco_medio * self.quantidade

    @property
    def valor_atual(self) -> Decimal:
        return self.preco_atual * self.quantidade

    @property
    def lucro(self) -> Decimal:
        return self.valor_atual - self.total_investido

    @property
    def percentual(self) -> Decimal:
        if self.total_investido == 0:
            return Decimal("0")
        return (self.lucro / self.total_investido) * Decimal("100")


def _to_decimal(value: str, field: str) -> Decimal:
    try:
        normalized = value.replace(".", "").replace(",", ".")
        return Decimal(normalized)
    except (InvalidOperation, AttributeError):
        raise ValueError(f"Valor inválido em '{field}': {value!r}")


def carregar_ativos(caminho: Path) -> List[Ativo]:
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    ativos: List[Ativo] = []
    with caminho.open(encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        obrigatorios = {"ativo", "preco_medio", "quantidade"}
        if leitor.fieldnames is None or not obrigatorios.issubset(leitor.fieldnames):
            raise ValueError(
                "CSV precisa conter as colunas: ativo, preco_medio, quantidade"
            )

        for linha in leitor:
            ativo = Ativo(
                nome=linha.get("ativo", "").strip(),
                preco_medio=_to_decimal(linha.get("preco_medio", "0"), "preco_medio"),
                quantidade=_to_decimal(linha.get("quantidade", "0"), "quantidade"),
                preco_atual=Decimal("0"),
                categoria=linha.get("categoria", "").strip(),
                ticker=linha.get("ticker", "").strip(),
            )
            ativos.append(ativo)

    return ativos


def _formatar_moeda(valor: Decimal) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _formatar_percentual(valor: Decimal) -> str:
    return f"{valor:.2f}%".replace(".", ",")


def _linha(*colunas: str, larguras: Iterable[int]) -> str:
    partes = []
    for coluna, largura in zip(colunas, larguras):
        partes.append(coluna.ljust(largura))
    return " | ".join(partes)


def descobrir_csv(caminho_informado: str | None) -> Path:
    if caminho_informado:
        return Path(caminho_informado)

    home = Path.home()
    candidatos = [
        home / "investimentos.csv",
        home / ".investimentos.csv",
        Path("data/investimentos.csv"),
    ]
    for candidato in candidatos:
        if candidato.exists():
            return candidato
    return candidatos[0]


def buscar_preco_google(ticker: str) -> Decimal:
    url = f"https://www.google.com/finance/quote/{ticker}"
    requisicao = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
    )
    with urllib.request.urlopen(requisicao, timeout=10) as resposta:
        html = resposta.read().decode("utf-8")

    correspondencia = re.search(r'data-last-price="([^"]+)"', html)
    if not correspondencia:
        raise ValueError(f"Não foi possível ler o preço do ticker {ticker}.")
    return _to_decimal(correspondencia.group(1), "preco_atual")


def atualizar_precos_google(ativos: List[Ativo]) -> None:
    for ativo in ativos:
        ticker = ativo.ticker or ativo.nome
        if not ticker:
            print("Aviso: ativo sem ticker não pode ser atualizado no Google.")
            continue
        try:
            ativo.preco_atual = buscar_preco_google(ticker)
        except Exception as exc:  # noqa: BLE001 - feedback ao usuário
            print(f"Aviso: não foi possível atualizar {ticker}: {exc}")


def exibir_dashboard(ativos: List[Ativo]) -> None:
    if not ativos:
        print("Nenhum ativo encontrado no CSV.")
        return

    larguras = [15, 12, 12, 14, 14, 10]
    cabecalho = _linha(
        "Ativo",
        "Preço Médio",
        "Qtd",
        "Valor Atual",
        "Resultado",
        "%",
        larguras=larguras,
    )
    print(cabecalho)
    print("-" * len(cabecalho))

    total_investido = Decimal("0")
    total_atual = Decimal("0")

    for ativo in ativos:
        total_investido += ativo.total_investido
        total_atual += ativo.valor_atual
        print(
            _linha(
                ativo.nome,
                _formatar_moeda(ativo.preco_medio),
                f"{ativo.quantidade}",
                _formatar_moeda(ativo.valor_atual),
                _formatar_moeda(ativo.lucro),
                _formatar_percentual(ativo.percentual),
                larguras=larguras,
            )
        )

    resultado = total_atual - total_investido
    percentual = Decimal("0") if total_investido == 0 else (resultado / total_investido) * Decimal("100")

    print("-" * len(cabecalho))
    print(
        _linha(
            "TOTAL",
            "",
            "",
            _formatar_moeda(total_atual),
            _formatar_moeda(resultado),
            _formatar_percentual(percentual),
            larguras=larguras,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Dashboard de investimentos no terminal")
    parser.add_argument(
        "csv",
        nargs="?",
        default=None,
        help="Caminho para o arquivo CSV",
    )
    args = parser.parse_args()

    caminho_csv = descobrir_csv(args.csv)
    ativos = carregar_ativos(caminho_csv)
    atualizar_precos_google(ativos)
    exibir_dashboard(ativos)


if __name__ == "__main__":
    main()
