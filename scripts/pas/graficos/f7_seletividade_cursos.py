"""F7 — Seletividade relativa dos cursos de TI.

Cada painel mostra um curso de TI. Para cada categoria de concorrência, o
boxplot representa a distribuição das notas de corte dos demais cursos da UnB,
ao longo dos subprogramas. Os pontos sobrepostos são as notas do curso de TI
do painel, identificadas pelo subprograma.

Saída: results/computacao/candidatos_geral/F7/
"""
from __future__ import annotations

import argparse
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import CATEGORIAS, PARSED, ROTULOS, ordem_subprogramas, pasta_saida


TABELA_PADRAO = "tabela2_curso_cota_sem_14_16.csv"
CORES_TI = ["#d95f02", "#1b9e77", "#7570b3", "#e7298a"]


def _ler_tabela(nome: str, coluna_nota: str) -> pd.DataFrame:
    caminho = PARSED / nome
    if not caminho.exists():
        raise SystemExit(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho, low_memory=False)
    obrigatorias = [
        "subprograma",
        "curso",
        "categoria",
        "area_computacao",
        coluna_nota,
    ]
    faltando = [c for c in obrigatorias if c not in df.columns]
    if faltando:
        raise SystemExit(f"Colunas ausentes em {nome}: {faltando}")

    df[coluna_nota] = pd.to_numeric(df[coluna_nota], errors="coerce")
    df = df[
        df["subprograma"].notna()
        & df["curso"].notna()
        & df["categoria"].isin(CATEGORIAS)
        & df[coluna_nota].notna()
    ].copy()
    if df.empty:
        raise SystemExit(f"Nenhuma nota de corte válida foi encontrada em {nome}.")
    return df


def calcular(df: pd.DataFrame, coluna_nota: str) -> pd.DataFrame:
    chaves = ["subprograma", "curso", "categoria"]
    t = (
        df.groupby(chaves, as_index=False)
        .agg(
            nota_corte=(coluna_nota, "median"),
            n_celulas=(coluna_nota, "count"),
            eh_ti=("area_computacao", lambda s: s.notna().any()),
        )
    )
    t["tipo_curso"] = np.where(t["eh_ti"], "TI", "Demais cursos")

    calibracao = t[t["tipo_curso"] == "Demais cursos"]
    percentis = []
    for row in t[t["eh_ti"]].itertuples(index=False):
        valores = calibracao.loc[
            (calibracao["subprograma"] == row.subprograma)
            & (calibracao["categoria"] == row.categoria),
            "nota_corte",
        ]
        percentis.append(
            {
                "subprograma": row.subprograma,
                "curso": row.curso,
                "categoria": row.categoria,
                "percentil_demais_cursos": (
                    100 * (valores <= row.nota_corte).mean() if len(valores) else np.nan
                ),
                "n_cursos_calibracao": len(valores),
            }
        )
    p = pd.DataFrame(percentis)
    t = t.merge(p, on=["subprograma", "curso", "categoria"], how="left")
    t["categoria_rotulo"] = t["categoria"].map(ROTULOS).fillna(t["categoria"])
    ordem_sub = {s: i for i, s in enumerate(ordem_subprogramas(t["subprograma"]))}
    ordem_cat = {c: i for i, c in enumerate(CATEGORIAS)}
    t["_ordem_sub"] = t["subprograma"].map(ordem_sub)
    t["_ordem_cat"] = t["categoria"].map(ordem_cat)
    return t.sort_values(["curso", "_ordem_sub", "_ordem_cat"]).drop(
        columns=["_ordem_sub", "_ordem_cat"]
    )


def _boxplot(ax, calibracao: pd.DataFrame, categorias: list[str]) -> None:
    dados = [
        calibracao.loc[calibracao["categoria"] == categoria, "nota_corte"].to_numpy()
        for categoria in categorias
    ]
    ax.boxplot(
        dados,
        positions=np.arange(1, len(categorias) + 1),
        widths=0.65,
        patch_artist=True,
        showfliers=False,
        boxprops={"facecolor": "#d9d9d9", "edgecolor": "#666666"},
        medianprops={"color": "#222222", "linewidth": 1.2},
        whiskerprops={"color": "#666666"},
        capprops={"color": "#666666"},
    )


def criar_figura(t: pd.DataFrame, nota_corte: str):
    ti = t[t["eh_ti"]].copy()
    calibracao = t[~t["eh_ti"]]
    cursos = sorted(ti["curso"].unique())
    categorias = [c for c in CATEGORIAS if c in t["categoria"].values]
    fig, axes = plt.subplots(2, 2, figsize=(18, 11), sharey=True)
    axes = axes.ravel()
    x = np.arange(1, len(categorias) + 1)
    subs = ordem_subprogramas(t["subprograma"])
    cores = dict(zip(subs, plt.get_cmap("viridis")(np.linspace(0.1, 0.9, len(subs)))))

    for ax, curso in zip(axes, cursos):
        _boxplot(ax, calibracao, categorias)
        dados_curso = ti[ti["curso"] == curso]
        for sub in subs:
            pontos = dados_curso[dados_curso["subprograma"] == sub]
            if pontos.empty:
                continue
            pontos = pontos.set_index("categoria").reindex(categorias).dropna(subset=["nota_corte"])
            ax.scatter(
                [x[categorias.index(c)] for c in pontos.index],
                pontos["nota_corte"],
                color=cores[sub],
                s=26,
                alpha=0.9,
                label=sub,
                zorder=3,
            )
        ax.set_title(curso, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels([ROTULOS[c].replace("Sistema Universal (ref.)", "Universal") for c in categorias], rotation=45, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.25)
        ax.axhline(0, color="#888888", linewidth=0.7)

    for ax in axes[len(cursos) :]:
        ax.set_visible(False)
    axes[0].set_ylabel(f"Nota de corte ({nota_corte})")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, title="Subprograma", loc="upper center", ncol=5)
    fig.suptitle(
        "Seletividade dos cursos de TI em relação aos demais cursos da UnB",
        y=0.99,
        fontsize=14,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV da tabela 2 em parsed_data/")
    ap.add_argument(
        "--nota-corte",
        choices=["primeira", "ultima"],
        default="ultima",
        help="Nota de corte a usar: primeira ou última chamada",
    )
    args = ap.parse_args()

    coluna_nota = {
        "primeira": "nota_corte_1a_chamada",
        "ultima": "nota_corte_ultima_chamada",
    }[args.nota_corte]
    dados = calcular(_ler_tabela(args.tabela, coluna_nota), coluna_nota)
    
    # Aqui a única mudança real
    saida = pasta_saida("F7", escopo="computacao", homologados=False)
    
    dados.to_csv(saida / "F7_dados.csv", index=False, float_format="%.3f")
    dados[dados["eh_ti"]].to_csv(saida / "F7_ti.csv", index=False, float_format="%.3f")

    fig = criar_figura(dados, args.nota_corte)
    for extensao in ("png", "pdf"):
        fig.savefig(saida / f"F7_seletividade_cursos.{extensao}", dpi=300)
    plt.close(fig)
    print(f"{len(dados)} linhas agregadas; {dados['eh_ti'].sum()} linhas de TI.")
    print(f"Arquivos salvos em {saida}")


if __name__ == "__main__":
    main()