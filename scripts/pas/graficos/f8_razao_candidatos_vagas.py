"""F8 — Relação entre candidatos e vagas nos cursos de TI.

Saída: results/computacao/candidatos_geral/F8/
"""
from __future__ import annotations

import argparse
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import CATEGORIAS, PARSED, ordem_subprogramas, pasta_saida


TABELA_PADRAO = "tabela2_curso_cota_sem_14_16.csv"
GRUPOS_GRAFICO = ("Universal", "Cotas")
CORES = {"Universal": "#4c78a8", "Cotas": "#f58518"}


def _ler_tabela(nome: str) -> pd.DataFrame:
    caminho = PARSED / nome
    if not caminho.exists():
        raise SystemExit(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho, low_memory=False)
    obrigatorias = ["subprograma", "curso", "categoria", "area_computacao", "vagas", "inscritos"]
    faltando = [c for c in obrigatorias if c not in df.columns]
    if faltando:
        raise SystemExit(f"Colunas ausentes em {nome}: {faltando}")

    for coluna in ("vagas", "inscritos"):
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df = df[
        df["subprograma"].notna()
        & df["curso"].notna()
        & df["area_computacao"].notna()
        & df["categoria"].isin(CATEGORIAS)
        & df["vagas"].notna()
        & df["inscritos"].notna()
    ].copy()
    if df.empty:
        raise SystemExit("Nenhuma linha válida de cursos de TI foi encontrada.")

    df["grupo_grafico"] = np.where(df["categoria"] == "SU", "Universal", "Cotas")
    return df


def calcular(df: pd.DataFrame) -> pd.DataFrame:
    t = (
        df.groupby(["subprograma", "curso", "grupo_grafico"], as_index=False)[
            ["vagas", "inscritos"]
        ]
        .sum()
        .rename(columns={"vagas": "vagas_totais", "inscritos": "inscritos_totais"})
    )
    t["razao_candidatos_vagas"] = np.where(
        t["vagas_totais"] > 0,
        t["inscritos_totais"] / t["vagas_totais"],
        np.nan,
    )
    t["ordem_subprograma"] = t["subprograma"].map(
        {s: i for i, s in enumerate(ordem_subprogramas(t["subprograma"]))}
    )
    t["ordem_grupo"] = t["grupo_grafico"].map({"Universal": 0, "Cotas": 1})
    return t.sort_values(
        ["curso", "ordem_subprograma", "ordem_grupo"]
    ).drop(columns=["ordem_subprograma", "ordem_grupo"])


def _nome_arquivo(valor: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", valor).strip("_")


def criar_figura(t: pd.DataFrame, curso: str):
    dados = t[t["curso"] == curso].copy()
    subs = ordem_subprogramas(dados["subprograma"])
    x = np.arange(len(subs))
    largura = 0.34
    fig, eixo_barras = plt.subplots(figsize=(13, 7))
    eixo_linha = eixo_barras.twinx()

    fundos = {"inscritos_totais": -largura / 2, "vagas_totais": largura / 2}
    rotulos_barras = {"inscritos_totais": "Candidatos inscritos", "vagas_totais": "Vagas"}
    barras_legendadas = []
    for metrica, deslocamento in fundos.items():
        base = np.zeros(len(subs))
        for grupo in GRUPOS_GRAFICO:
            valores = (
                dados[dados["grupo_grafico"] == grupo]
                .set_index("subprograma")
                .reindex(subs)[metrica]
                .fillna(0)
                .to_numpy()
            )
            barras = eixo_barras.bar(
                x + deslocamento,
                valores,
                largura,
                bottom=base,
                color=CORES[grupo],
                alpha=0.82 if metrica == "inscritos_totais" else 0.48,
                edgecolor="white",
                linewidth=0.5,
                label=f"{rotulos_barras[metrica]} — {grupo}",
            )
            if metrica == "inscritos_totais":
                barras_legendadas.append(barras)
            base += valores

    for grupo in GRUPOS_GRAFICO:
        valores = (
            dados[dados["grupo_grafico"] == grupo]
            .set_index("subprograma")
            .reindex(subs)["razao_candidatos_vagas"]
        )
        linha = eixo_linha.plot(
            x,
            valores,
            color=CORES[grupo],
            marker="o",
            linewidth=2.2,
            markersize=5,
            label=f"Razão inscritos/vagas — {grupo}",
            zorder=5,
        )
    eixo_barras.set_xticks(x)
    eixo_barras.set_xticklabels(subs)
    eixo_barras.set_ylabel("Quantidade")
    eixo_linha.set_ylabel("Candidatos por vaga")
    eixo_barras.set_xlabel("Subprograma")
    eixo_barras.grid(axis="y", alpha=0.25)
    eixo_barras.set_title(
        f"{curso}\nCandidatos, vagas e razão de concorrência por sistema"
    )

    handles_1, labels_1 = eixo_barras.get_legend_handles_labels()
    handles_2, labels_2 = eixo_linha.get_legend_handles_labels()
    eixo_barras.legend(
        handles_1 + handles_2,
        labels_1 + labels_2,
        loc="upper left",
        fontsize=9,
        frameon=False,
    )
    fig.tight_layout()
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV da tabela 2 em parsed_data/")
    args = ap.parse_args()

    dados = calcular(_ler_tabela(args.tabela))
    saida = pasta_saida("F8", escopo="computacao", homologados=False)
    dados.to_csv(saida / "F8_dados.csv", index=False, float_format="%.3f")

    for curso in sorted(dados["curso"].unique()):
        fig = criar_figura(dados, curso)
        nome = f"F8_{_nome_arquivo(curso)}"
        for extensao in ("png", "pdf"):
            fig.savefig(saida / f"{nome}.{extensao}", dpi=300)
        plt.close(fig)

    print(
        f"{len(dados)} linhas agregadas; {dados['curso'].nunique()} cursos de TI; "
        f"{dados['subprograma'].nunique()} subprogramas."
    )
    print(f"Arquivos salvos em {saida}")


if __name__ == "__main__":
    main()