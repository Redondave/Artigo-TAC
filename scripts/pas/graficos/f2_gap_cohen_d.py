"""F2 — Evolução do gap de desempenho em desvios-padrão (d de Cohen).

Compara, subprograma a subprograma, candidatos de computação inscritos em
alguma cota de escola pública (EP_*) com os do Sistema Universal (SU), em:
argumento final e em EB1, EB2 e NR de cada etapa.

Convenção: d = (média SU − média EP) / dp combinado. d > 0 => Universal à frente.
O grupo EP junta as 8 categorias EP_*; Negros (NEG) fica de fora (ver F3).

Saída (results/F2/):
    F2_gap_cohen_d.png / .pdf   figura 2x2 (AF, EB1, EB2, NR)
    F2_dados.csv                d, IC95% e n por subprograma x medida

Uso:  python scripts/pas/graficos/f2_gap_cohen_d.py [--tabela ARQ.csv] [--sem-ic]
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import (
    ETAPAS,
    PROVAS,
    aplicar_estilo,
    carregar_alunos,
    cohen_d,
    indice_lei_14723,
    marcar_lei,
    ordem_subprogramas,
    pasta_saida,
    salvar,
    TABELA_PADRAO,
)

COR_ETAPA = {1: "#1b9e77", 2: "#d95f02", 3: "#7570b3"}
MARCADOR_ETAPA = {1: "o", 2: "s", 3: "^"}


def calcular_gaps(df: pd.DataFrame, subs: list[str]) -> pd.DataFrame:
    su = df[df["sistema_inscricao"] == "SU"]
    ep = df[df["sistema_inscricao"].str.startswith("EP_")]

    medidas = [("af", None, "argumento_final")] + [
        (p, e, f"{p}_pas{e}") for p in PROVAS for e in ETAPAS
    ]
    linhas = []
    for prova, etapa, col in medidas:
        for sub in subs:
            r = cohen_d(
                su.loc[su["subprograma"] == sub, col],
                ep.loc[ep["subprograma"] == sub, col],
            )
            linhas.append({"subprograma": sub, "prova": prova, "etapa": etapa, **r})
    out = pd.DataFrame(linhas).rename(columns={"n_ref": "n_su", "n_alvo": "n_ep"})
    return out


def desenhar(gaps: pd.DataFrame, subs: list[str], idx_lei, com_ic: bool):
    aplicar_estilo()
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    paineis = [
        ("af", "Argumento final", axes[0, 0]),
        ("eb1", PROVAS["eb1"], axes[0, 1]),
        ("eb2", PROVAS["eb2"], axes[1, 0]),
        ("nr", PROVAS["nr"], axes[1, 1]),
    ]
    x = np.arange(len(subs))

    for prova, titulo, ax in paineis:
        g = gaps[gaps["prova"] == prova]
        if prova == "af":
            series = [(None, "Argumento final", "black", "o")]
        else:
            series = [
                (e, f"{e}ª etapa", COR_ETAPA[e], MARCADOR_ETAPA[e]) for e in ETAPAS
            ]
        for etapa, rotulo, cor, marc in series:
            sel = g[g["etapa"].isna()] if etapa is None else g[g["etapa"] == etapa]
            s = sel.set_index("subprograma").reindex(subs)
            ax.plot(x, s["d"], marker=marc, ms=4, lw=1.6, color=cor, label=rotulo)
            if com_ic:
                ax.fill_between(x, s["ic_inf"], s["ic_sup"], color=cor, alpha=0.12, lw=0)
        ax.axhline(0, color="0.5", lw=0.8, zorder=0)
        marcar_lei(ax, idx_lei)
        ax.set_title(titulo)
        if prova != "af":
            ax.legend(fontsize=8, loc="lower left", ncol=3, columnspacing=1.0, handlelength=1.5)

    for ax in axes[1]:
        ax.set_xticks(x)
        ax.set_xticklabels(subs, rotation=45, ha="right")
    fig.supylabel("d de Cohen (Universal − EP)")
    fig.supxlabel("Subprograma", y=0.0)
    fig.text(
        0.5,
        -0.035,
        "d > 0: Universal à frente dos cotistas de escola pública. "
        + ("Faixas: IC 95%." if com_ic else ""),
        ha="center",
        fontsize=8,
        color="0.35",
    )
    fig.tight_layout()
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV em parsed_data/")
    ap.add_argument("--sem-ic", action="store_true", help="não desenha as faixas de IC95%%")
    args = ap.parse_args()

    df = carregar_alunos(args.tabela)
    subs = ordem_subprogramas(df["subprograma"])
    gaps = calcular_gaps(df, subs)

    saida = pasta_saida("F2")
    gaps.to_csv(saida / "F2_dados.csv", index=False, float_format="%.4f")
    print(f"  salvo: {(saida / 'F2_dados.csv').relative_to(saida.parents[1])}")

    fig = desenhar(gaps, subs, indice_lei_14723(subs), com_ic=not args.sem_ic)
    salvar(fig, saida, "F2_gap_cohen_d")


if __name__ == "__main__":
    main()