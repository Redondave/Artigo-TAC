"""F2 — Evolução do gap de desempenho em desvios-padrão (d de Cohen).

Compara, subprograma a subprograma, os candidatos de cotas (Escola Pública e Negros) 
com os do Universal ESTRITO (`sistema_inscricao == "SU"`, isto é, quem só tem 
classificação no Sistema Universal), em: argumento final e em EB1, EB2 e NR de cada etapa. 

Saída (results/computacao/candidatos_geral/F2/):
    F2_gap_cohen_d.png / .pdf                figura 2x2 (EP vs Universal estrito)
    F2_dados.csv                             d, IC95% e n por subprograma x medida (EP)
    F2_gap_cohen_d_negros.png / .pdf         figura 2x2 (Negros vs Universal estrito)
    F2_dados_negros.csv                      d, IC95% e n por subprograma x medida (Negros)
    F2_sensibilidade_universal_amplo.png/.pdf 
        argumento final: gap contra o Universal estrito vs. Universal "amplo".
        
A pasta candidatos_convocados_para_homologacao/F2/ conterá as mesmas figuras,
mas aplicadas apenas ao topo do ranking.

Escopo (--escopo): computacao (padrão; results/computacao/candidatos_geral/F2), 
geral (results/geral/...) ou curso (results/por_curso/<área>/...).

Uso:  python scripts/pas/graficos/f2_gap_cohen_d.py [--tabela ARQ.csv] [--sem-ic]
      [--escopo computacao|geral|curso]
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import (
    ETAPAS,
    PROVAS,
    TABELA_PADRAO,
    aplicar_estilo,
    cohen_d,
    grupo_de_cota,
    indice_lei_14723,
    marcar_lei,
    ordem_subprogramas,
    pasta_saida,
    recortes,
    salvar,
)

COR_ETAPA = {1: "#1b9e77", 2: "#d95f02", 3: "#7570b3"}
MARCADOR_ETAPA = {1: "o", 2: "s", 3: "^"}


def calcular_gaps(ref: pd.DataFrame, ep: pd.DataFrame, subs: list[str], so_af: bool = False) -> pd.DataFrame:
    medidas = [("af", None, "argumento_final")]
    if not so_af:
        medidas += [(p, e, f"{p}_pas{e}") for p in PROVAS for e in ETAPAS]
    linhas = []
    for prova, etapa, col in medidas:
        for sub in subs:
            r = cohen_d(
                ref.loc[ref["subprograma"] == sub, col],
                ep.loc[ep["subprograma"] == sub, col],
            )
            linhas.append({"subprograma": sub, "prova": prova, "etapa": etapa, **r})
    return pd.DataFrame(linhas).rename(columns={"n_ref": "n_ref", "n_alvo": "n_ep"})


def desenhar(gaps, subs, idx_lei, com_ic, ylabel, nota):
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
    fig.supylabel(ylabel)
    fig.supxlabel("Subprograma", y=0.0)
    fig.text(0.5, -0.035, nota + (" Faixas: IC 95%." if com_ic else ""),
             ha="center", fontsize=8, color="0.35")
    fig.tight_layout()
    return fig


def desenhar_sensibilidade(est, amp, subs, idx_lei, com_ic):
    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    x = np.arange(len(subs))
    for g, rot, cor, ls, mk in [
        (est, "contra Universal estrito (só SU)", "black", "-", "o"),
        (amp, "contra Universal amplo (todos os candidatos)", "0.55", "--", "x"),
    ]:
        s = g.set_index("subprograma").reindex(subs)
        ax.plot(x, s["d"], ls=ls, marker=mk, ms=4, lw=1.6, color=cor, label=rot)
        if com_ic:
            ax.fill_between(x, s["ic_inf"], s["ic_sup"], color=cor, alpha=0.10, lw=0)
    ax.axhline(0, color="0.5", lw=0.8, zorder=0)
    marcar_lei(ax, idx_lei)
    ax.set_xticks(x)
    ax.set_xticklabels(subs, rotation=45, ha="right")
    ax.set_xlabel("Subprograma")
    ax.set_ylabel("d de Cohen (referência − EP)")
    ax.set_title("Argumento final: gap de EP contra duas definições de Universal")
    ax.legend(fontsize=8, loc="best")
    fig.text(0.5, -0.04, "O Universal amplo inclui os próprios cotistas EP, o que aproxima as médias e encolhe o gap.",
             ha="center", fontsize=8, color="0.35")
    fig.tight_layout()
    return fig


def executar(df: pd.DataFrame, escopo: str, area, com_ic: bool = True) -> None:
    subs = ordem_subprogramas(df["subprograma"])
    idx_lei = indice_lei_14723(subs)

    # --- padrão: EP vs Universal estrito (grupos disjuntos) ---
    base = pasta_saida("F2", escopo, area, homologados=False)
    su = df[df["sistema_inscricao"] == "SU"]
    ep = df[df["sistema_inscricao"].str.startswith("EP_")]
    gaps = calcular_gaps(su, ep, subs)
    gaps.to_csv(base / "F2_dados.csv", index=False, float_format="%.4f")
    print("  salvo: F2_dados.csv")
    fig = desenhar(gaps, subs, idx_lei, com_ic, "d de Cohen (Universal estrito − EP)",
                   "d > 0: Universal estrito (só SU) à frente dos cotistas de escola pública.")
    salvar(fig, base, "F2_gap_cohen_d")
    plt.close(fig)

    # --- padrão: Negros vs Universal estrito ---
    neg = df[df["sistema_inscricao"] == "NEG"]
    gaps_neg = calcular_gaps(su, neg, subs)
    gaps_neg.to_csv(base / "F2_dados_negros.csv", index=False, float_format="%.4f")
    print("  salvo: F2_dados_negros.csv")
    fig_neg = desenhar(
        gaps_neg, 
        subs, 
        idx_lei, 
        com_ic, 
        "d de Cohen (Universal estrito − Negros)",
        "d > 0: Universal estrito (só SU) à frente da cota para Negros."
    )
    salvar(fig_neg, base, "F2_gap_cohen_d_negros")
    plt.close(fig_neg)

    # --- sensibilidade: Universal amplo = todos os candidatos ---
    amp = calcular_gaps(df, ep, subs, so_af=True)
    fig = desenhar_sensibilidade(gaps[gaps["prova"] == "af"], amp, subs, idx_lei, com_ic)
    salvar(fig, base, "F2_sensibilidade_universal_amplo")
    plt.close(fig)

    # --- homologados: grupo = cota da vaga ---
    ap = df[df["aprovado_bool"] & df["cota_aprovacao"].notna()].copy()
    if ap.empty:
        print("  [homologados] sem convocados com cota_aprovacao; pulando.")
        return
    ap["_g"] = ap["cota_aprovacao"].map(grupo_de_cota)
    sem = ap.loc[ap["_g"].isna(), "cota_aprovacao"]
    if len(sem):
        print(f"  [homologados] {len(sem)} convocados com cota_aprovacao não reconhecida "
              f"(ignorados): {sorted(set(sem))[:8]}")
    
    su_a = ap[ap["_g"] == "Universal"]
    ep_a = ap[ap["_g"].isin(["EP PPI", "EP Não-PPI"])]
    
    pasta_aprov = pasta_saida("F2", escopo, area, homologados=True)
    
    gaps_a = calcular_gaps(su_a, ep_a, subs)
    gaps_a.to_csv(pasta_aprov / "F2_gap_cohen_d_homologados_dados.csv", index=False, float_format="%.4f")
    fig = desenhar(gaps_a, subs, idx_lei, com_ic, "d de Cohen (convocados Universal − convocados EP)",
                   "Somente convocados para homologação, agrupados pela cota da vaga. d > 0: Universais à frente.")
    salvar(fig, pasta_aprov, "F2_gap_cohen_d_homologados")
    plt.close(fig)

    # --- homologados extra: convocados Negros ---
    neg_a = ap[ap["_g"] == "Negros"]
    gaps_neg_a = calcular_gaps(su_a, neg_a, subs)
    gaps_neg_a.to_csv(pasta_aprov / "F2_gap_cohen_d_homologados_negros_dados.csv", index=False, float_format="%.4f")
    fig_neg_a = desenhar(
        gaps_neg_a, 
        subs, 
        idx_lei, 
        com_ic, 
        "d de Cohen (convocados Universal − convocados Negros)",
        "Somente convocados para homologação. d > 0: convocados Universais à frente."
    )
    salvar(fig_neg_a, pasta_aprov, "F2_gap_cohen_d_homologados_negros")
    plt.close(fig_neg_a)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV em parsed_data/")
    ap.add_argument("--sem-ic", action="store_true", help="não desenha as faixas de IC95%%")
    ap.add_argument("--escopo", choices=["computacao", "geral", "curso"], default="computacao")
    args = ap.parse_args()
    for df, escopo, area in recortes(args.tabela, (args.escopo,)):
        print(f"== F2 | {escopo} {area or ''} ({len(df)} candidatos)")
        executar(df, escopo, area, com_ic=not args.sem_ic)


if __name__ == "__main__":
    main()