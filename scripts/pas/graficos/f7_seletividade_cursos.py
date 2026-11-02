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
        widths=0.5, # Levemente mais fino para dar espaço aos pontos
        patch_artist=True,
        showfliers=False,
        boxprops={"facecolor": "#e0e0e0", "edgecolor": "#999999", "alpha": 0.6},
        medianprops={"color": "#555555", "linewidth": 1.5},
        whiskerprops={"color": "#999999", "linewidth": 1},
        capprops={"color": "#999999", "linewidth": 1},
        zorder=1
    )


def criar_figura(t: pd.DataFrame, nota_corte: str):
    ti = t[t["eh_ti"]].copy()
    calibracao = t[~t["eh_ti"]]
    cursos = sorted(ti["curso"].unique())
    categorias = [c for c in CATEGORIAS if c in t["categoria"].values]
    
    # constrained_layout resolve automaticamente sobreposições de título e eixos
    fig, axes = plt.subplots(2, 2, figsize=(18, 11), sharey=True, constrained_layout=True)
    axes = axes.ravel()
    x = np.arange(1, len(categorias) + 1)
    subs = ordem_subprogramas(t["subprograma"])
    
    # Mapa de cores categóricas (melhor para distinguir anos diferentes)
    cores = dict(zip(subs, plt.get_cmap("tab10").colors[:len(subs)]))

    for ax, curso in zip(axes, cursos):
        # Limpeza visual (remove bordas desnecessárias)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
        ax.set_axisbelow(True)
        ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)

        _boxplot(ax, calibracao, categorias)
        dados_curso = ti[ti["curso"] == curso]
        
        # Desenha os pontos com Jitter (deslocamento) para não sobreporem totalmente
        for i, sub in enumerate(subs):
            pontos = dados_curso[dados_curso["subprograma"] == sub]
            if pontos.empty:
                continue
            pontos = pontos.set_index("categoria").reindex(categorias).dropna(subset=["nota_corte"])
            
            # Calcula um pequeno recuo no eixo X baseado no subprograma
            offset = (i - (len(subs) - 1) / 2) * 0.1
            x_pos = [x[categorias.index(c)] + offset for c in pontos.index]
            
            ax.scatter(
                x_pos,
                pontos["nota_corte"],
                color=cores[sub],
                s=60,                  # Aumentado para melhor visibilidade
                edgecolors="white",    # Borda branca destaca contra o fundo do boxplot
                linewidth=1,
                alpha=0.95,
                label=sub,
                zorder=3,
            )
            
        ax.set_title(curso, fontsize=12, fontweight='bold', color="#333333", pad=12)
        ax.set_xticks(x)
        
        # rotation_mode="anchor" garante que o final da palavra aponte para o tick do eixo
        ax.set_xticklabels(
            [ROTULOS[c].replace("Sistema Universal (ref.)", "Universal") for c in categorias], 
            rotation=45, 
            ha="right", 
            rotation_mode="anchor", 
            fontsize=9
        )
        ax.axhline(0, color="#aaaaaa", linewidth=1.2, zorder=0)

    for ax in axes[len(cursos) :]:
        ax.set_visible(False)
        
    axes[0].set_ylabel(f"Nota de corte ({nota_corte})", fontsize=11, labelpad=10)
    
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        # Legenda movida para o topo, fora da área dos gráficos, sem caixa em volta
        fig.legend(
            handles, labels, 
            title="Subprograma", 
            loc="upper center", 
            bbox_to_anchor=(0.5, 1.08), 
            ncol=len(subs),
            frameon=False,
            fontsize=10
        )
        
    fig.suptitle(
        "Seletividade dos cursos de TI em relação aos demais cursos da UnB",
        fontsize=16,
        fontweight="bold",
        color="#222222"
    )
    
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
    
    saida = pasta_saida("F7", escopo="computacao", homologados=False)
    
    dados.to_csv(saida / "F7_dados.csv", index=False, float_format="%.3f")
    dados[dados["eh_ti"]].to_csv(saida / "F7_ti.csv", index=False, float_format="%.3f")

    fig = criar_figura(dados, args.nota_corte)
    for extensao in ("png", "pdf"):
        fig.savefig(saida / f"F7_seletividade_cursos.{extensao}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"{len(dados)} linhas agregadas; {dados['eh_ti'].sum()} linhas de TI.")
    print(f"Arquivos salvos em {saida}")


if __name__ == "__main__":
    main()