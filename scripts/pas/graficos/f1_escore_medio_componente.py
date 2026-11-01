"""F1 — Evolução do escore bruto médio por componente.

Gera 3 figuras separadas: EB1, EB2 e NR (nota da redação). Cada figura tem 3
painéis empilhados (PAS 1, PAS 2, PAS 3) com eixo y compartilhado e eixo x
compartilhado em datas de aplicação da prova, e 4 linhas de grupos de
concorrência: Universal, Negros, EP PPI, EP Não-PPI (`grupo_concorrencia`).
Faixa = IC 95% da média (média ± 1,96 · dp / √n).

DATAS DAS PROVAS (eixo x), lidas de parsed_data/subprogramas*.csv:
    data_prova_pas3            existe no glossário; usada como está.
    data_prova_pas1/_pas2      OPCIONAIS. Se a coluna não existir (ou estiver
                               vazia num subprograma), a data é APROXIMADA como
                               a do PAS 3 menos 2 anos (PAS 1) e menos 1 ano
                               (PAS 2). O script avisa quando isso acontece.
                               Para datas exatas, adicione essas colunas.
Formatos aceitos: AAAA-MM-DD ou DD/MM/AAAA.

ATENÇÃO — quem entra nas médias: `grupo_concorrencia` só existe para quem chegou
à classificação do PAS 3. Logo, as médias dos painéis PAS 1 e PAS 2 são dos
candidatos que continuaram até o PAS 3 (não de todos que fizeram a 1ª/2ª etapa).

Saída (results/F1/):
    F1_eb1.png/.pdf, F1_eb2.png/.pdf, F1_nr.png/.pdf
    F1_dados.csv   n, média, dp, IC95% e data usada, por prova x etapa x subprograma x grupo

Uso:  python scripts/pas/graficos/f1_escore_medio_componente.py [--sem-ic]
      [--tabela ARQ.csv] [--subprogramas ARQ.csv]
"""
from __future__ import annotations

import argparse
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import (
    COR_GRUPO,
    ETAPAS,
    GRUPOS,
    PARSED,
    PROVAS,
    SUBPROGRAMAS_PADRAO,
    TABELA_PADRAO,
    aplicar_estilo,
    carregar_alunos,
    ordem_subprogramas,
    pasta_saida,
    salvar,
)

MARCADOR = {"Universal": "o", "Negros": "s", "EP PPI": "^", "EP Não-PPI": "D"}
YLABEL = {"eb1": "Escore bruto médio — EB1", "eb2": "Escore bruto médio — EB2", "nr": "Nota média da redação (0–10)"}


def _parse_datas(s: pd.Series) -> pd.Series:
    """AAAA-MM-DD primeiro; o que sobrar tenta DD/MM/AAAA."""
    out = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    resto = out.isna() & s.notna()
    if resto.any():
        out[resto] = pd.to_datetime(s[resto], dayfirst=True, errors="coerce")
    return out


def carregar_datas(nome: str):
    """Devolve ({etapa: Series indexada por subprograma}, etapas_aproximadas)."""
    caminho = PARSED / nome
    if not caminho.exists():
        sys.exit(f"Arquivo não encontrado: {caminho}")
    t = pd.read_csv(caminho, dtype=str).set_index("subprograma")
    if "data_prova_pas3" not in t.columns:
        sys.exit(f"Coluna data_prova_pas3 ausente em {nome}")

    datas = {}
    for e in ETAPAS:
        col = f"data_prova_pas{e}"
        datas[e] = _parse_datas(t[col]) if col in t.columns else pd.Series(pd.NaT, index=t.index, dtype="datetime64[ns]")

    aproximadas = []
    for etapa, anos in ((1, 2), (2, 1)):
        falta = datas[etapa].isna() & datas[3].notna()
        if falta.any():
            datas[etapa][falta] = datas[3][falta] - pd.DateOffset(years=anos)
            aproximadas.append(etapa)
    if aproximadas:
        print(
            f"[aviso] datas do PAS {aproximadas} aproximadas como (data do PAS 3 − "
            "2 anos / − 1 ano). Para datas exatas, adicione data_prova_pas1/_pas2 "
            f"em {nome}."
        )
    sem = [s for s in t.index if pd.isna(datas[3].get(s))]
    if sem:
        print(f"[aviso] subprogramas sem data_prova_pas3 (ficam fora da F1): {sem}")
    return datas, aproximadas


def calcular(df: pd.DataFrame, datas: dict, subs: list[str]) -> pd.DataFrame:
    partes = []
    for prova in PROVAS:
        for etapa in ETAPAS:
            col = f"{prova}_pas{etapa}"
            g = (
                df.groupby(["subprograma", "grupo_concorrencia"])[col]
                .agg(n="count", media="mean", dp="std")
                .reset_index()
                .rename(columns={"grupo_concorrencia": "grupo"})
            )
            ep = 1.96 * g["dp"] / np.sqrt(g["n"].where(g["n"] > 1))
            g["ic_inf"], g["ic_sup"] = g["media"] - ep, g["media"] + ep
            g["data"] = g["subprograma"].map(datas[etapa])
            g.insert(0, "etapa", etapa)
            g.insert(0, "prova", prova)
            partes.append(g)
    return pd.concat(partes, ignore_index=True)


def desenhar(t: pd.DataFrame, prova: str, com_ic: bool, aproximadas: list[int]):
    aplicar_estilo()
    fig, axes = plt.subplots(3, 1, figsize=(9, 8.8), sharex=True, sharey=True)
    for ax, etapa in zip(axes, ETAPAS):
        for grupo in GRUPOS:
            s = t[(t["prova"] == prova) & (t["etapa"] == etapa) & (t["grupo"] == grupo)]
            s = s.dropna(subset=["data"]).sort_values("data")
            cor = COR_GRUPO[grupo]
            ax.plot(s["data"], s["media"], marker=MARCADOR[grupo], ms=4, lw=1.6, color=cor, label=grupo)
            if com_ic:
                ax.fill_between(s["data"], s["ic_inf"], s["ic_sup"], color=cor, alpha=0.10, lw=0)
        # rótulo do subprograma de cada aplicação, na base do painel
        for _, r in t[(t["prova"] == prova) & (t["etapa"] == etapa)].drop_duplicates("subprograma").dropna(subset=["data"]).iterrows():
            ax.text(r["data"], 0.02, r["subprograma"], transform=ax.get_xaxis_transform(),
                    rotation=90, ha="center", va="bottom", fontsize=6, color="0.5")
        sufixo = " (datas aproximadas)" if etapa in aproximadas else ""
        ax.set_title(f"{etapa}ª etapa (PAS {etapa}){sufixo}", loc="left")
    axes[0].legend(fontsize=8, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.12))
    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[-1].set_xlabel("Data de aplicação da prova")
    fig.supylabel(YLABEL[prova])
    nota = (
        "Médias de candidatos que chegaram à classificação do PAS 3"
        + ("; faixas: IC 95% da média" if com_ic else "")
        + ". Rótulos em cinza: subprograma."
    )
    fig.text(0.5, -0.01, nota, ha="center", fontsize=8, color="0.35")
    fig.tight_layout()
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV em parsed_data/")
    ap.add_argument("--subprogramas", default=SUBPROGRAMAS_PADRAO, help="CSV em parsed_data/ com as datas")
    ap.add_argument("--sem-ic", action="store_true", help="não desenha as faixas de IC95%%")
    args = ap.parse_args()

    df = carregar_alunos(args.tabela)
    if "grupo_concorrencia" not in df.columns:
        sys.exit(f"Coluna grupo_concorrencia ausente em {args.tabela}")
    subs = ordem_subprogramas(df["subprograma"])
    datas, aproximadas = carregar_datas(args.subprogramas)
    t = calcular(df, datas, subs)

    saida = pasta_saida("F1")
    t.to_csv(saida / "F1_dados.csv", index=False, float_format="%.4f", date_format="%Y-%m-%d")
    print("  salvo: F1_dados.csv")
    for prova in PROVAS:
        fig = desenhar(t, prova, com_ic=not args.sem_ic, aproximadas=aproximadas)
        salvar(fig, saida, f"F1_{prova}")
        plt.close(fig)


if __name__ == "__main__":
    main()