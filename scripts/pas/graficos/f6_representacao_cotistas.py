"""F6 — Representação proporcional dos cotistas entre candidatos e aprovados.

Por curso e subprograma:
  candidatos  = % de cotistas entre quem fez o PAS 3 no curso (compareceu_pas3)
  aprovados   = % de cotistas entre os aprovados (convocados), pelo perfil de inscrição
  vaga de cota = % dos aprovados que entraram por vaga reservada (cota_aprovacao != SU)
  linha       = % das vagas do curso reservadas a cotas (quadro de vagas)
Cotista = sistema_inscricao diferente de SU (Negros ou qualquer categoria de escola
pública, incluindo PcD). A diferença entre "aprovados" e "vaga de cota" mostra os
cotistas aprovados pela ampla concorrência, regra da Lei 14.723 a partir de 22-24.

Saída: results/computacao/candidatos_geral/F6/
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import (PARSED, aplicar_estilo, indice_lei_14723, marcar_lei,
                            ordem_subprogramas, pasta_saida, salvar)
from f4_notas_corte import CURSOS

TABELA1 = "tabela1_alunos_sem_eng_soft.csv"
TABELA2 = "tabela2_curso_cota_sem_eng_soft.csv"
BARRAS = [("pct_cotistas_candidatos", "Cotistas entre os candidatos", "#9ecae1"),
          ("pct_cotistas_aprovados", "Cotistas entre os aprovados", "#2171b5"),
          ("pct_aprovados_por_vaga_de_cota", "Aprovados por vaga de cota", "#08306b")]


def _bool(s):
    return s.astype(str).str.strip().str.lower().eq("true")


def calcular(t1: pd.DataFrame, t2: pd.DataFrame) -> pd.DataFrame:
    t1 = t1[t1["area_computacao"].isin(CURSOS) & _bool(t1["compareceu_pas3"])].copy()
    t1["cotista"] = t1["sistema_inscricao"].ne("SU")
    t1["aprov"] = _bool(t1["aprovado"])
    t1["por_cota"] = t1["aprov"] & t1["cota_aprovacao"].notna() & t1["cota_aprovacao"].ne("SU")
    chave = ["area_computacao", "subprograma"]
    a = t1.groupby(chave).agg(candidatos=("cotista", "size"), cotistas_candidatos=("cotista", "sum"))
    ap = t1[t1["aprov"]]
    b = ap.groupby(chave).agg(aprovados=("cotista", "size"), cotistas_aprovados=("cotista", "sum"),
                              aprovados_com_categoria=("cota_aprovacao", lambda s: s.notna().sum()),
                              aprovados_por_vaga_de_cota=("por_cota", "sum"))
    t2 = t2[t2["area_computacao"].isin(CURSOS)].copy()
    t2["vagas"] = pd.to_numeric(t2["vagas"], errors="coerce")
    v = t2.groupby(chave).apply(lambda d: pd.Series({
        "vagas": d["vagas"].sum(),
        "vagas_reservadas": d.loc[d["categoria"] != "SU", "vagas"].sum()}), include_groups=False)
    t = a.join(b).join(v).reset_index()
    t["pct_cotistas_candidatos"] = 100 * t["cotistas_candidatos"] / t["candidatos"]
    t["pct_cotistas_aprovados"] = 100 * t["cotistas_aprovados"] / t["aprovados"]
    t["pct_aprovados_por_vaga_de_cota"] = 100 * t["aprovados_por_vaga_de_cota"] / t["aprovados_com_categoria"]
    t["pct_vagas_reservadas"] = 100 * t["vagas_reservadas"] / t["vagas"]
    t["razao_representacao"] = t["pct_cotistas_aprovados"] / t["pct_cotistas_candidatos"]
    t["curso"] = t["area_computacao"].map(CURSOS)
    return t


def criar_figura(t: pd.DataFrame):
    subs = ordem_subprogramas(t["subprograma"])
    x = np.arange(len(subs))
    larg = 0.27
    fig, eixos = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    for ax, (area, nome) in zip(eixos, CURSOS.items()):
        d = t[t["area_computacao"] == area].set_index("subprograma").reindex(subs)
        for k, (col, rot, cor) in enumerate(BARRAS):
            ax.bar(x + (k - 1) * larg, d[col], larg, color=cor, label=rot)
        ax.plot(x, d["pct_vagas_reservadas"], color="#e6550d", marker="D", ms=4, lw=1.6,
                label="Vagas reservadas a cotas")
        marcar_lei(ax, indice_lei_14723(subs))
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}%")
        ax.set_title(nome)
        ax.set_xticks(x)
        ax.set_xticklabels(subs, rotation=45)
        ax.set_xlabel("Subprograma")
        ax.grid(axis="y", alpha=0.25)
    eixos[0].set_ylabel("Percentual")
    h, l = eixos[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=9, bbox_to_anchor=(0.5, -0.12))
    fig.suptitle("F6 — Cotistas entre candidatos e aprovados (perfil de inscrição e via de entrada)", y=1.02)
    fig.text(0.5, -0.17, "Cotista = inscrito em Cotas para Negros ou em qualquer categoria de escola pública. "
             "Aprovado = convocado em alguma chamada.", ha="center", fontsize=8, color="0.3")
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela1", default=TABELA1)
    ap.add_argument("--tabela2", default=TABELA2)
    args = ap.parse_args()
    aplicar_estilo()
    t1 = pd.read_csv(PARSED / args.tabela1, low_memory=False, dtype=str)
    t2 = pd.read_csv(PARSED / args.tabela2, low_memory=False, dtype={"subprograma": str})
    t = calcular(t1, t2)
    saida = pasta_saida("F6", escopo="computacao", homologados=False)
    t.to_csv(saida / "F6_dados.csv", index=False, float_format="%.2f")
    fig = criar_figura(t)
    salvar(fig, saida, "F6_representacao_cotistas")
    plt.close(fig)


if __name__ == "__main__":
    main()
