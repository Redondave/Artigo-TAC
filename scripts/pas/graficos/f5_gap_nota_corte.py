"""F5 — Respiro da nota de corte: 1ª chamada do 1º semestre × último convocado.

gap = nota de corte da 1ª chamada do 1º semestre − menor AF entre todos os convocados
do grupo, em todas as chamadas e nos dois semestres. Gap positivo = a nota caiu ao
longo das chamadas suplementares e do 2º semestre (o "respiro").
Mesmos grupos e cursos da F4 (sem PcD; 18-20 com ingresso único).

Saída: results/computacao/candidatos_geral/F5/
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import (COR_GRUPO, GRUPOS, aplicar_estilo, indice_lei_14723, marcar_lei,
                            ordem_subprogramas, pasta_saida, salvar)
from f4_notas_corte import CURSOS, TABELA_PADRAO, ler_tabela2


def calcular(df: pd.DataFrame) -> pd.DataFrame:
    chave = ["area_computacao", "subprograma", "grupo"]
    inicial = (df[df["semestre"] == "1"].groupby(chave, as_index=False)
               .agg(corte_1a_chamada_1sem=("nota_corte_1a_chamada", "min")))
    final = (df.groupby(chave, as_index=False)
             .agg(corte_ultimo_convocado=("nota_corte_ultima_chamada", "min"),
                  convocados_total=("convocados", "sum"),
                  vagas_total=("vagas", "sum"),
                  ultima_chamada=("ultima_chamada", "max")))
    t = inicial.merge(final, on=chave, how="outer")
    t["gap"] = t["corte_1a_chamada_1sem"] - t["corte_ultimo_convocado"]
    t["curso"] = t["area_computacao"].map(CURSOS)
    return t


def criar_figura(t: pd.DataFrame):
    subs = ordem_subprogramas(t["subprograma"])
    x = np.arange(len(subs))
    larg = 0.2
    fig, eixos = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    for ax, (area, nome) in zip(eixos, CURSOS.items()):
        d = t[t["area_computacao"] == area]
        for k, g in enumerate(GRUPOS):
            serie = d[d["grupo"] == g].set_index("subprograma").reindex(subs)["gap"]
            ax.bar(x + (k - 1.5) * larg, serie, larg, color=COR_GRUPO[g], label=g)
        marcar_lei(ax, indice_lei_14723(subs))
        ax.axhline(0, color="0.4", lw=0.8)
        ax.set_title(nome)
        ax.set_xticks(x)
        ax.set_xticklabels(subs, rotation=45)
        ax.set_xlabel("Subprograma")
        ax.grid(axis="y", alpha=0.25)
    eixos[0].set_ylabel("Queda da nota de corte (pontos de AF)")
    h, l = eixos[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=9, bbox_to_anchor=(0.5, -0.12))
    fig.suptitle("F5 — Corte da 1ª chamada do 1º semestre menos o AF do último convocado "
                 "(todas as chamadas, 2 semestres)", y=1.02)
    fig.text(0.5, -0.17, "Barra ausente = grupo sem convocado na 1ª chamada do 1º semestre. "
             "18-20: ingresso único (só chamadas suplementares).", ha="center", fontsize=8, color="0.3")
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV da tabela 2 em parsed_data/")
    args = ap.parse_args()
    aplicar_estilo()
    t = calcular(ler_tabela2(args.tabela))
    saida = pasta_saida("F5", escopo="computacao", homologados=False)
    t.to_csv(saida / "F5_dados.csv", index=False, float_format="%.3f")
    fig = criar_figura(t)
    salvar(fig, saida, "F5_gap_nota_corte")
    plt.close(fig)


if __name__ == "__main__":
    main()
