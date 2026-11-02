"""F1 — Evolução do escore bruto médio por componente.

Gera 3 figuras separadas: EB1, EB2 e NR (nota da redação). Cada figura tem 3
painéis empilhados (PAS 1, PAS 2, PAS 3), com eixos x (data de aplicação da
prova) e y compartilhados, e uma linha por grupo de concorrência. Faixa = IC 95%
da média (média ± 1,96 · dp / √n).

LINHAS (cada candidato entra em UM só grupo: o de `sistema_inscricao`, que é a
categoria mais restritiva em que ele tem classificação):
    Universal estrito (só SU)   quem só tem classificação no Sistema Universal
    Negros, EP PPI, EP Não-PPI  demais grupos (`grupo_concorrencia`)
    Universal amplo (todos)     linha de referência pontilhada: TODOS os
                                candidatos, já que todo mundo tem classificação
                                no SU (inclui os cotistas). Serve para mostrar o
                                efeito de usar o Universal "diluído".

DATAS: as datas exatas de aplicação estão na tabela DATAS_PROVAS abaixo.
Datas atípicas (calendário alterado pela pandemia) levam "*" no rótulo.

PASTA exploracao/ (dentro da saída): mesmas figuras, mas só com candidatos
APROVADOS (convocados) e agrupados pela cota da vaga (`cota_aprovacao`),
disjuntos — ou seja, os "topos" do ranking de cada cota. Sem a linha "amplo".

Escopo (--escopo): computacao (padrão; results/F1), geral (todos os cursos;
results/geral/F1) ou curso (um por área; results/curso/F1/<área>).

Saída: F1_eb1/eb2/nr .png/.pdf e F1_dados.csv

Uso:  python scripts/pas/graficos/f1_escore_medio_componente.py [--sem-ic]
      [--escopo computacao|geral|curso] [--tabela ARQ.csv]
"""
from __future__ import annotations

import argparse

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import (
    COR_AMPLO,
    COR_GRUPO,
    ETAPAS,
    GRUPO_AMPLO,
    GRUPOS,
    PROVAS,
    ROTULO_GRUPO,
    TABELA_PADRAO,
    aplicar_estilo,
    grupo_de_cota,
    pasta_saida,
    recortes,
    salvar,
)

# Datas de aplicação (PAS 1, PAS 2, PAS 3) de cada subprograma.
# Fonte: tabela fornecida pelo grupo, conferida com avisos do Cebraspe.
# AJUSTE: 16-18/PAS 3 estava 02/12/2018 na tabela; o Cebraspe informa que as
# provas de todos os subprogramas vigentes foram aplicadas juntas em 09/12/2018.
DATAS_PROVAS = {
    "15-17": ("2015-12-06", "2016-12-03", "2017-12-03"),
    "16-18": ("2016-12-04", "2017-12-02", "2018-12-09"),
    "17-19": ("2017-12-03", "2018-12-09", "2019-12-01"),
    "18-20": ("2018-12-09", "2019-12-01", "2021-07-18"),
    "19-21": ("2019-12-01", "2021-06-20", "2022-01-30"),
    "20-22": ("2021-06-27", "2022-02-13", "2022-12-11"),
    "21-23": ("2022-02-20", "2022-12-10", "2023-12-17"),
    "22-24": ("2022-12-17", "2023-12-10", "2024-12-01"),
    "23-25": ("2023-12-03", "2024-12-08", "2025-11-30"),
}
# (subprograma, etapa) com data atípica por causa da pandemia de Covid-19.
ATIPICAS = {("18-20", 3), ("19-21", 2), ("19-21", 3), ("20-22", 1), ("20-22", 2), ("21-23", 1)}

DATAS = {
    (sub, etapa): pd.Timestamp(d)
    for sub, ds in DATAS_PROVAS.items()
    for etapa, d in zip(ETAPAS, ds)
}

MARCADOR = {"Universal": "o", "Negros": "s", "EP PPI": "^", "EP Não-PPI": "D", GRUPO_AMPLO: "x"}
YLABEL = {"eb1": "Escore bruto médio — EB1", "eb2": "Escore bruto médio — EB2", "nr": "Nota média da redação (0–10)"}
ROTULO_APROV = {
    "Universal": "Aprovados em vaga Universal",
    "Negros": "Aprovados em cota Negros",
    "EP PPI": "Aprovados em cota EP PPI",
    "EP Não-PPI": "Aprovados em cota EP Não-PPI",
}


def calcular(base: pd.DataFrame, subs_validas: list[str]) -> pd.DataFrame:
    """`base` precisa ter a coluna `_g` (grupo de cada linha)."""
    partes = []
    for prova in PROVAS:
        for etapa in ETAPAS:
            col = f"{prova}_pas{etapa}"
            g = (
                base.groupby(["subprograma", "_g"])[col]
                .agg(n="count", media="mean", dp="std")
                .reset_index()
                .rename(columns={"_g": "grupo"})
            )
            ep = 1.96 * g["dp"] / np.sqrt(g["n"].where(g["n"] > 1))
            g["ic_inf"], g["ic_sup"] = g["media"] - ep, g["media"] + ep
            g["data"] = [DATAS.get((s, etapa)) for s in g["subprograma"]]
            g.insert(0, "etapa", etapa)
            g.insert(0, "prova", prova)
            partes.append(g)
    t = pd.concat(partes, ignore_index=True)
    fora = sorted(set(t.loc[t["data"].isna(), "subprograma"]))
    if fora:
        print(f"[aviso] subprogramas sem data em DATAS_PROVAS (ficam fora): {fora}")
    return t


def desenhar(t, prova, com_ic, grupos, rotulos, nota):
    aplicar_estilo()
    fig, axes = plt.subplots(3, 1, figsize=(9, 8.8), sharex=True, sharey=True)
    for ax, etapa in zip(axes, ETAPAS):
        for grupo in grupos:
            s = t[(t["prova"] == prova) & (t["etapa"] == etapa) & (t["grupo"] == grupo)]
            s = s.dropna(subset=["data"]).sort_values("data")
            if grupo == GRUPO_AMPLO:
                ax.plot(s["data"], s["media"], marker="x", ms=4, lw=1.3, ls="--",
                        color=COR_AMPLO, label=rotulos[grupo])
                continue
            cor = COR_GRUPO[grupo]
            ax.plot(s["data"], s["media"], marker=MARCADOR[grupo], ms=4, lw=1.6,
                    color=cor, label=rotulos[grupo])
            if com_ic:
                ax.fill_between(s["data"], s["ic_inf"], s["ic_sup"], color=cor, alpha=0.10, lw=0)
        # rótulo do subprograma de cada aplicação (com * se data atípica)
        ref = t[(t["prova"] == prova) & (t["etapa"] == etapa)].drop_duplicates("subprograma").dropna(subset=["data"])
        for _, r in ref.iterrows():
            marca = "*" if (r["subprograma"], etapa) in ATIPICAS else ""
            ax.text(r["data"], 0.02, r["subprograma"] + marca, transform=ax.get_xaxis_transform(),
                    rotation=90, ha="center", va="bottom", fontsize=6, color="0.5")
        ax.set_title(f"{etapa}ª etapa (PAS {etapa})", loc="left")
    axes[0].legend(fontsize=7.5, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.12))
    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[-1].set_xlabel("Data de aplicação da prova")
    fig.supylabel(YLABEL[prova])
    fig.text(0.5, -0.025, nota, ha="center", fontsize=8, color="0.35", va="top")
    fig.tight_layout()
    return fig


def _figuras(t, base, com_ic, grupos, rotulos, nota, sufixo=""):
    t.to_csv(base / f"F1_dados{sufixo}.csv", index=False, float_format="%.4f", date_format="%Y-%m-%d")
    print(f"  salvo: {(base / f'F1_dados{sufixo}.csv').name}")
    for prova in PROVAS:
        fig = desenhar(t, prova, com_ic, grupos, rotulos, nota)
        salvar(fig, base, f"F1_{prova}{sufixo}")
        plt.close(fig)


def executar(df: pd.DataFrame, base, com_ic: bool = True) -> None:
    """Gera as figuras padrão em `base` e, se houver aprovados, as de `base/exploracao`."""
    subs = sorted(set(df["subprograma"]))
    aviso_dados = "Médias de candidatos que chegaram à classificação do PAS 3. * data atípica (pandemia). Rótulo cinza: subprograma."

    # --- padrão: grupo da inscrição (disjunto) + linha "Universal amplo" ---
    b = df.assign(_g=df["grupo_concorrencia"])
    b = pd.concat([b, df.assign(_g=GRUPO_AMPLO)], ignore_index=True)
    t = calcular(b, subs)
    nota = aviso_dados + (" Faixas: IC 95%." if com_ic else "")
    _figuras(t, base, com_ic, GRUPOS + [GRUPO_AMPLO], ROTULO_GRUPO, nota)

    # --- exploração: só aprovados, grupo = cota da vaga (disjunto) ---
    ap = df[df["aprovado_bool"] & df["cota_aprovacao"].notna()].copy()
    if ap.empty:
        print("  [exploração] sem aprovados com cota_aprovacao; pulando.")
        return
    ap["_g"] = ap["cota_aprovacao"].map(grupo_de_cota)
    sem = ap.loc[ap["_g"].isna(), "cota_aprovacao"]
    if len(sem):
        print(f"  [exploração] {len(sem)} aprovados com cota_aprovacao não reconhecida "
              f"(ignorados): {sorted(set(sem))[:8]}")
    ap = ap.dropna(subset=["_g"])
    pasta = base / "exploracao"
    pasta.mkdir(exist_ok=True)
    t2 = calcular(ap, subs)
    nota2 = ("Somente candidatos aprovados (convocados), agrupados pela cota da vaga (cota_aprovacao): "
             "o topo do ranking de cada cota. * data atípica. Rótulo cinza: subprograma."
             + (" Faixas: IC 95%." if com_ic else ""))
    _figuras(t2, pasta, com_ic, GRUPOS, ROTULO_APROV, nota2, sufixo="_aprovados")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV em parsed_data/")
    ap.add_argument("--sem-ic", action="store_true", help="não desenha as faixas de IC95%%")
    ap.add_argument("--escopo", choices=["computacao", "geral", "curso"], default="computacao")
    args = ap.parse_args()
    for df, escopo, area in recortes(args.tabela, (args.escopo,)):
        print(f"== F1 | {escopo} {area or ''} ({len(df)} candidatos)")
        executar(df, pasta_saida("F1", escopo, area), com_ic=not args.sem_ic)


if __name__ == "__main__":
    main()