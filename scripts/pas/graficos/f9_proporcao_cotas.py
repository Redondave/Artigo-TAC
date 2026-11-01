"""F9 — Proporção de inscritos por categoria de concorrência nos cursos de TI.

Gera um gráfico de linhas para cada curso de TI. Cada linha representa uma
categoria de concorrência e mostra sua proporção entre os inscritos do curso
em cada subprograma.

As células de campus, turno e semestre são somadas por curso, subprograma e
categoria. A categoria ``DESCONHECIDA`` é excluída, pois não representa um
sistema de concorrência identificável. O denominador é o total de inscritos
nas dez categorias conhecidas do curso e subprograma.

Uso:
    python scripts/pas/graficos/f9_proporcao_cotas.py
"""
from __future__ import annotations

import argparse
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import CATEGORIAS, PARSED, ROTULOS, ordem_subprogramas, pasta_saida


TABELA_PADRAO = "tabela2_curso_cota_sem_14_16.csv"


def _ler_tabela(nome: str) -> pd.DataFrame:
    caminho = PARSED / nome
    if not caminho.exists():
        raise SystemExit(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho, low_memory=False)
    obrigatorias = [
        "subprograma",
        "curso",
        "categoria",
        "area_computacao",
        "inscritos",
    ]
    faltando = [c for c in obrigatorias if c not in df.columns]
    if faltando:
        raise SystemExit(f"Colunas ausentes em {nome}: {faltando}")

    df["inscritos"] = pd.to_numeric(df["inscritos"], errors="coerce")
    df = df[
        df["subprograma"].notna()
        & df["curso"].notna()
        & df["area_computacao"].notna()
        & df["categoria"].isin(CATEGORIAS)
        & df["inscritos"].notna()
    ].copy()
    if df.empty:
        raise SystemExit("Nenhuma linha válida de cursos de TI foi encontrada.")
    return df


def calcular(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula a proporção de inscritos em cada categoria."""
    base = (
        df.groupby(["subprograma", "curso", "categoria"], as_index=False)["inscritos"]
        .sum()
        .rename(columns={"inscritos": "inscritos_categoria"})
    )
    cursos = base[["subprograma", "curso"]].drop_duplicates()
    subs_cursos = cursos.assign(_chave=1)
    categorias = pd.DataFrame({"categoria": CATEGORIAS, "_chave": 1})
    t = subs_cursos.merge(categorias, on="_chave").drop(columns="_chave")
    t = t.merge(base, on=["subprograma", "curso", "categoria"], how="left")
    t["inscritos_categoria"] = t["inscritos_categoria"].fillna(0)

    totais = (
        t.groupby(["subprograma", "curso"], as_index=False)["inscritos_categoria"]
        .sum()
        .rename(columns={"inscritos_categoria": "inscritos_total"})
    )
    t = t.merge(totais, on=["subprograma", "curso"])
    t["proporcao"] = np.where(
        t["inscritos_total"] > 0,
        t["inscritos_categoria"] / t["inscritos_total"],
        np.nan,
    )
    t["percentual"] = 100 * t["proporcao"]
    t["categoria_rotulo"] = t["categoria"].map(ROTULOS).fillna(t["categoria"])
    t["ordem_subprograma"] = t["subprograma"].map(
        {s: i for i, s in enumerate(ordem_subprogramas(t["subprograma"]))}
    )
    t["ordem_categoria"] = t["categoria"].map(
        {categoria: i for i, categoria in enumerate(CATEGORIAS)}
    )
    return t.sort_values(
        ["curso", "ordem_subprograma", "ordem_categoria"]
    ).drop(columns=["ordem_subprograma", "ordem_categoria"])


def _nome_arquivo(valor: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", valor).strip("_")


def criar_figura(t: pd.DataFrame, curso: str):
    dados = t[t["curso"] == curso].copy()
    subs = ordem_subprogramas(dados["subprograma"])
    x = np.arange(len(subs))
    fig, eixo = plt.subplots(figsize=(14, 8))
    cores = plt.get_cmap("tab10")(np.linspace(0, 1, len(CATEGORIAS)))

    for categoria, cor in zip(CATEGORIAS, cores):
        serie = (
            dados[dados["categoria"] == categoria]
            .set_index("subprograma")
            .reindex(subs)["percentual"]
        )
        eixo.plot(
            x,
            serie,
            marker="o",
            linewidth=1.8,
            markersize=4.5,
            color=cor,
            label=ROTULOS.get(categoria, categoria),
        )

    eixo.set_xticks(x)
    eixo.set_xticklabels(subs)
    eixo.set_ylim(0, 100)
    eixo.set_xlabel("Subprograma")
    eixo.set_ylabel("Inscritos na categoria (%)")
    eixo.set_title(f"{curso}\nComposição dos inscritos por sistema de concorrência")
    eixo.yaxis.set_major_formatter(lambda valor, pos: f"{valor:.0f}%")
    eixo.grid(axis="y", alpha=0.25)
    eixo.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=9)
    fig.tight_layout()
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV da tabela 2 em parsed_data/")
    args = ap.parse_args()

    dados = calcular(_ler_tabela(args.tabela))
    saida = pasta_saida("F9")
    dados.to_csv(saida / "F9_dados.csv", index=False, float_format="%.4f")

    for curso in sorted(dados["curso"].unique()):
        fig = criar_figura(dados, curso)
        nome = f"F9_{_nome_arquivo(curso)}"
        for extensao in ("png", "pdf"):
            fig.savefig(saida / f"{nome}.{extensao}", dpi=300)
        plt.close(fig)

    print(
        f"{len(dados)} linhas; {dados['curso'].nunique()} cursos de TI; "
        f"{dados['subprograma'].nunique()} subprogramas; "
        f"{dados['categoria'].nunique()} categorias."
    )
    print(f"Arquivos salvos em {saida}")


if __name__ == "__main__":
    main()
