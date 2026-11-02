"""F4 — Evolução das notas de corte por sistema de concorrência nos cursos de computação.

Nota de corte de um grupo = menor argumento final (AF) entre os convocados da 1ª chamada
do 1º semestre nas categorias do grupo (em 18-20, ingresso único: semestre 0). As
categorias PcD ficam de fora: têm uma vaga, quase sempre vazia ou preenchida por regra
própria, e o mínimo delas não representa o grupo.

O AF é padronizado dentro de cada coorte (z-escores somados com pesos 1, 2 e 3): ele
mede a posição relativa do candidato no seu ano, não um nível absoluto.

Saída: results/computacao/candidatos_geral/F4/
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import (COR_GRUPO, GRUPOS, PARSED, aplicar_estilo, indice_lei_14723,
                            marcar_lei, ordem_subprogramas, pasta_saida, salvar)

TABELA_PADRAO = "tabela2_curso_cota_sem_eng_soft.csv"

# categoria da tabela 2 -> grupo dos gráficos (sem PcD)
GRUPO_DA_CATEGORIA = {
    "SU": "Universal",
    "NEG": "Negros",
    "EP_R1_PPI": "EP PPI", "EP_R2_PPI": "EP PPI",
    "EP_R1_NPPI": "EP Não-PPI", "EP_R2_NPPI": "EP Não-PPI",
}
CURSOS = {
    "CC_BACHARELADO": "Ciência da Computação (bacharelado)",
    "ENG_COMPUTACAO": "Engenharia de Computação",
    "COMPUTACAO_LICENCIATURA": "Computação (licenciatura, noturno)",
}
SUBS_SISUNB = {"15-17", "16-18"}
SUBS_PANDEMIA = {"18-20", "19-21"}


def ler_tabela2(nome: str = TABELA_PADRAO) -> pd.DataFrame:
    caminho = PARSED / nome
    if not caminho.exists():
        raise SystemExit(f"Arquivo não encontrado: {caminho}")
    df = pd.read_csv(caminho, low_memory=False, dtype={"subprograma": str, "semestre": str})
    df = df[df["area_computacao"].isin(CURSOS) & df["categoria"].isin(GRUPO_DA_CATEGORIA)].copy()
    for c in ("vagas", "inscritos", "convocados", "convocados_1a_chamada", "ultima_chamada",
              "nota_corte_1a_chamada", "nota_corte_ultima_chamada"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["semestre"] = df["semestre"].replace({"0": "1"})  # 18-20: ingresso único
    df["grupo"] = df["categoria"].map(GRUPO_DA_CATEGORIA)
    return df


def calcular(df: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por curso × subprograma × grupo, com o corte da 1ª chamada do 1º semestre."""
    s1 = df[df["semestre"] == "1"]
    t = (s1.groupby(["area_computacao", "subprograma", "grupo"], as_index=False)
         .agg(nota_corte=("nota_corte_1a_chamada", "min"),
              vagas_1sem=("vagas", "sum"),
              convocados_1a_chamada=("convocados_1a_chamada", "sum"),
              inscritos=("inscritos", "sum")))
    t["curso"] = t["area_computacao"].map(CURSOS)
    return t


def _marcos(ax, subs):
    """Faixa do SISUnB, faixa da pandemia e linha da Lei 14.723."""
    for conjunto, rotulo, cor in ((SUBS_SISUNB, "SISUnB", "0.93"), (SUBS_PANDEMIA, "Pandemia", "#fde8d7")):
        idx = [i for i, s in enumerate(subs) if s in conjunto]
        if idx:
            ax.axvspan(min(idx) - 0.5, max(idx) + 0.5, color=cor, zorder=0, lw=0)
            ax.text((min(idx) + max(idx)) / 2, 0.02, rotulo, transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=7, color="0.35")
    marcar_lei(ax, indice_lei_14723(subs))


def criar_figura(t: pd.DataFrame):
    subs = ordem_subprogramas(t["subprograma"])
    x = np.arange(len(subs))
    fig, eixos = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    for ax, (area, nome) in zip(eixos, CURSOS.items()):
        _marcos(ax, subs)
        d = t[t["area_computacao"] == area]
        for g in GRUPOS:
            serie = d[d["grupo"] == g].set_index("subprograma").reindex(subs)["nota_corte"]
            ax.plot(x, serie, marker="o", lw=2, ms=4.5, color=COR_GRUPO[g], label=g)
        ax.axhline(0, color="0.6", lw=0.8)
        ax.set_title(nome)
        ax.set_xticks(x)
        ax.set_xticklabels(subs, rotation=45)
        ax.set_xlabel("Subprograma")
        ax.grid(axis="y", alpha=0.25)
    eixos[0].set_ylabel("Nota de corte (argumento final)")
    h, l = eixos[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=9, bbox_to_anchor=(0.5, -0.12))
    fig.suptitle("F4 — Nota de corte da 1ª chamada do 1º semestre, por sistema de concorrência", y=1.02)
    fig.text(0.5, -0.17, "AF padronizado dentro de cada coorte (posição relativa no ano). "
             "Grupos sem PcD; EP PPI e EP Não-PPI = menor corte entre as faixas de renda. "
             "18-20: ingresso único.", ha="center", fontsize=8, color="0.3")
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV da tabela 2 em parsed_data/")
    args = ap.parse_args()
    aplicar_estilo()
    t = calcular(ler_tabela2(args.tabela))
    saida = pasta_saida("F4", escopo="computacao", homologados=False)
    t.to_csv(saida / "F4_dados.csv", index=False, float_format="%.3f")
    fig = criar_figura(t)
    salvar(fig, saida, "F4_notas_corte")
    plt.close(fig)


if __name__ == "__main__":
    main()
