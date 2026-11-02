"""F3 — Heatmap do gap (d de Cohen) por categoria de concorrência.

Linhas: as 10 categorias de `sistema_inscricao` (SU, NEG e 8 EP_*), onde cada
candidato aparece em UMA só categoria (a mais restritiva em que tem classificação).
Colunas: subprogramas, em ordem cronológica.
Célula: d de Cohen entre a referência e a categoria, na medida escolhida
(padrão: argumento final).  d = (média referência − média categoria) / dp combinado,
logo d > 0 => referência à frente.

Gera DOIS heatmaps por medida (os dois têm a linha de Cotas para Negros):
    F3_heatmap_<metrica>                     referência = Universal ESTRITO
        (candidatos só com classificação no SU). A linha SU é a própria referência
        e fica em cinza.
    F3_heatmap_<metrica>_vs_universal_amplo  referência = Universal AMPLO (todos os
        candidatos, inclusive os cotistas). Serve de sensibilidade; aqui a linha SU
        (estrito) também é comparada.

Células com menos de --min-n candidatos ficam em cinza com o n escrito, porque d
com amostras minúsculas é ruído (várias categorias PCD).

Escopo (--escopo): computacao (padrão; results/F3), geral (todos os cursos;
results/geral/F3) ou curso (um por área; results/curso/F3/<área>).

Saída: F3_heatmap_*.png/.pdf e F3_dados_*.csv

Uso:  python scripts/pas/graficos/f3_heatmap_gap_categorias.py
      [--metrica argumento_final|eb1_pas3|nr_pas2|...] [--min-n 5] [--tabela ARQ.csv]
      [--escopo computacao|geral|curso]
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import (
    CATEGORIAS,
    COLUNAS_NUMERICAS,
    ROTULOS,
    TABELA_PADRAO,
    aplicar_estilo,
    cohen_d,
    indice_lei_14723,
    marcar_lei,
    nome_metrica,
    ordem_subprogramas,
    pasta_saida,
    recortes,
    salvar,
)


def calcular_matriz(df, subs, metrica, min_n, ref="estrito") -> pd.DataFrame:
    """ref="estrito": referência = só SU (linha SU mascarada).
    ref="amplo": referência = todos os candidatos (linha SU também é comparada)."""
    referencia = df[df["sistema_inscricao"] == "SU"] if ref == "estrito" else df
    linhas = []
    for cat in CATEGORIAS:
        dcat = df[df["sistema_inscricao"] == cat]
        for sub in subs:
            a = referencia.loc[referencia["subprograma"] == sub, metrica]
            b = dcat.loc[dcat["subprograma"] == sub, metrica]
            if cat == "SU" and ref == "estrito":
                r = {"d": np.nan, "n_ref": a.notna().sum(), "n_alvo": a.notna().sum()}
            else:
                r = cohen_d(a, b)
            linhas.append({"categoria": cat, "subprograma": sub, **r})
    t = pd.DataFrame(linhas).rename(columns={"n_ref": "n_ref", "n_alvo": "n_categoria"})
    t["mascarada"] = (
        ((t["categoria"] == "SU") & (ref == "estrito"))
        | t["d"].isna()
        | (t["n_categoria"] < min_n)
        | (t["n_ref"] < min_n)
    )
    return t


def desenhar(t, subs, metrica, idx_lei, ref="estrito"):
    aplicar_estilo()
    nl, nc = len(CATEGORIAS), len(subs)

    d = np.full((nl, nc), np.nan)
    n = np.zeros((nl, nc), dtype=int)
    mask = np.ones((nl, nc), dtype=bool)
    for _, r in t.iterrows():
        i, j = CATEGORIAS.index(r["categoria"]), subs.index(r["subprograma"])
        d[i, j] = r["d"]
        n[i, j] = r["n_categoria"]
        mask[i, j] = r["mascarada"]

    visivel = np.ma.masked_array(d, mask=mask | np.isnan(d))
    lim = max(0.5, float(np.ceil(np.nanmax(np.abs(visivel.filled(np.nan))) * 4) / 4)) if (~visivel.mask).any() else 1.0

    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#ececec")

    fig, ax = plt.subplots(figsize=(1.0 * nc + 4.2, 0.62 * nl + 1.8))
    im = ax.imshow(visivel, cmap=cmap, vmin=-lim, vmax=lim, aspect="auto")

    for i in range(nl):
        for j in range(nc):
            if CATEGORIAS[i] == "SU" and ref == "estrito":
                ax.text(j, i, f"ref.\n({n[i, j]})", ha="center", va="center",
                        fontsize=7, color="0.45", style="italic")
            elif mask[i, j]:
                txt = "–" if n[i, j] == 0 else f"n={n[i, j]}"
                ax.text(j, i, txt, ha="center", va="center", fontsize=7, color="0.45")
            else:
                cor = "white" if abs(d[i, j]) > 0.6 * lim else "black"
                ax.text(j, i, f"{d[i, j]:.2f}\n({n[i, j]})", ha="center", va="center",
                        fontsize=7.5, color=cor)

    # separadores: SU | NEG | EP renda<=lim | EP renda>lim
    for y in (0.5, 1.5, 5.5):
        ax.axhline(y, color="white", lw=3)
    ax.set_xticks(range(nc))
    ax.set_xticklabels(subs, rotation=45, ha="right")
    ax.set_yticks(range(nl))
    rot = dict(ROTULOS)
    rot["SU"] = "Universal estrito (ref.)" if ref == "estrito" else "Universal estrito (só SU)"
    ax.set_yticklabels([rot[c] for c in CATEGORIAS])
    for lado in ax.spines.values():
        lado.set_visible(False)
    ax.tick_params(length=0)
    marcar_lei(ax, idx_lei)
    ax.set_xlabel("Subprograma")
    nome_ref = "Universal estrito (só SU)" if ref == "estrito" else "Universal amplo (todos os candidatos)"
    ax.set_title(f"Gap em relação ao {nome_ref} — {nome_metrica(metrica)}")

    cb = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.04)
    cb.set_label("d de Cohen (referência − categoria)")
    fig.text(
        0.01, -0.02,
        "Valor (n): d e nº de candidatos na categoria. Cinza: referência ou n < mínimo. Cada candidato conta em uma só linha.\n"
        "d > 0: referência à frente. 'lim.' = limite de renda (1,5 SM até 21-23; 1 SM desde 22-24).",
        fontsize=7.5, color="0.35", va="top",
    )
    fig.tight_layout()
    return fig


def executar(df, base, metrica="argumento_final", min_n=5) -> None:
    subs = ordem_subprogramas(df["subprograma"])
    idx_lei = indice_lei_14723(subs)
    for ref, sufixo in (("estrito", ""), ("amplo", "_vs_universal_amplo")):
        t = calcular_matriz(df, subs, metrica, min_n, ref)
        csv = base / f"F3_dados_{metrica}{sufixo}.csv"
        t.to_csv(csv, index=False, float_format="%.4f")
        print(f"  salvo: {csv.name}")
        fig = desenhar(t, subs, metrica, idx_lei, ref)
        salvar(fig, base, f"F3_heatmap_{metrica}{sufixo}")
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV em parsed_data/")
    ap.add_argument("--metrica", default="argumento_final", choices=COLUNAS_NUMERICAS)
    ap.add_argument("--min-n", type=int, default=5, help="n mínimo por célula (padrão 5)")
    ap.add_argument("--escopo", choices=["computacao", "geral", "curso"], default="computacao")
    args = ap.parse_args()
    for df, escopo, area in recortes(args.tabela, (args.escopo,)):
        print(f"== F3 | {escopo} {area or ''} ({len(df)} candidatos)")
        executar(df, pasta_saida("F3", escopo, area), args.metrica, args.min_n)


if __name__ == "__main__":
    main()