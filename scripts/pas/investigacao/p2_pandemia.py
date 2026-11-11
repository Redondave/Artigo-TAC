"""Parte 2: a pandemia foi "mascarada" por provas mais fáceis?

Datas oficiais usadas (anos letivos de ensino remoto no DF): 2020 e 2021.
A etapa e do subprograma AA-BB avalia o ano letivo 20AA + e − 1. Provas de anos
letivos afetados: 18-20 (PAS 3), 19-21 (PAS 2 e 3), 20-22 (PAS 1 e 2), 21-23 (PAS 1).

Saídas em results/investigacao_paradoxo/:
  p2_provas_brutas.csv      média, dp, assimetria e n de cada prova (UnB inteira) por ano letivo
  p2_dificuldade_pandemia.csv  cada prova pandêmica comparada às demais da mesma etapa (escore z)
  p2_gap_por_etapa_unb.csv  d (SUE × EP e SUE × Negros) de cada etapa e prova, UnB inteira
  p2_modelo_pandemia.csv    regressão do d: coorte + etapa + prova + "prova feita na pandemia"
  p2_correlacao_etapas.csv  correlação EB2 PAS 1 × PAS 3 de cada coorte (estabilidade do ranking)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from comum import SUBS, carregar, cohen_d, salvar

ANOS_REMOTOS = {2020, 2021}


def ano_letivo(sub: str, etapa: int) -> int:
    return 2000 + int(sub[:2]) + etapa - 1


def main():
    todos = carregar(todos_os_inscritos=True)
    linhas = []
    for sub in SUBS:
        d = todos[todos["subprograma"] == sub]
        for e in (1, 2, 3):
            presentes = d[d[f"compareceu_pas{e}"]]
            for p in ("eb1", "eb2", "nr"):
                a = presentes[f"{p}_pas{e}"].dropna()
                if len(a) < 100:
                    continue
                linhas.append({"subprograma": sub, "etapa": e, "prova": p, "ano_letivo": ano_letivo(sub, e),
                               "pandemia": ano_letivo(sub, e) in ANOS_REMOTOS,
                               "n": len(a), "n_presentes": len(presentes),
                               "populacao_completa": len(a) >= 0.9 * len(presentes),
                               "media": a.mean(), "dp": a.std(), "assimetria": stats.skew(a),
                               "p10": a.quantile(.1), "p50": a.median(), "p90": a.quantile(.9)})
    brutas = pd.DataFrame(linhas)
    salvar(brutas, "p2_provas_brutas.csv")

    # Prova pandêmica × demais provas da mesma etapa e tipo (só populações completas)
    linhas = []
    b = brutas[brutas["populacao_completa"]]
    for (e, p), g in b.groupby(["etapa", "prova"]):
        normais = g[~g["pandemia"]]
        for _, r in g[g["pandemia"]].iterrows():
            linhas.append({"etapa": e, "prova": p, "ano_letivo": r["ano_letivo"], "subprograma": r["subprograma"],
                           "media_pandemia": r["media"], "media_outros_anos": normais["media"].mean(),
                           "dp_entre_outros_anos": normais["media"].std(),
                           "z_media": (r["media"] - normais["media"].mean()) / normais["media"].std(),
                           "assimetria_pandemia": r["assimetria"],
                           "assimetria_outros_anos": normais["assimetria"].mean(),
                           "n_outros_anos": len(normais)})
    salvar(pd.DataFrame(linhas), "p2_dificuldade_pandemia.csv")

    # Efeito diferencial: o gap entre SUE e cotas cresceu nas provas da pandemia?
    t = carregar()
    linhas = []
    for sub in SUBS:
        d = t[t["subprograma"] == sub]
        sue = d[d["grupo_concorrencia"] == "Universal"]
        for g, alvo in [("EP (todas)", d[d["ep"]]), ("Negros", d[d["grupo_concorrencia"] == "Negros"])]:
            for e in (1, 2, 3):
                for p in ("eb1", "eb2", "nr"):
                    col = f"{p}_pas{e}"
                    linhas.append({"subprograma": sub, "grupo": g, "etapa": e, "prova": p,
                                   "ano_letivo": ano_letivo(sub, e),
                                   "pandemia": int(ano_letivo(sub, e) in ANOS_REMOTOS),
                                   **cohen_d(sue[col], alvo[col])})
    gap = pd.DataFrame(linhas)
    salvar(gap, "p2_gap_por_etapa_unb.csv")

    linhas = []
    for g in ["EP (todas)", "Negros"]:
        for p in ["eb2", "nr", "todas"]:
            x = gap[gap["grupo"] == g]
            if p != "todas":
                x = x[x["prova"] == p]
            f = "d ~ C(subprograma) + C(etapa) + pandemia" + (" + C(prova)" if p == "todas" else "")
            m = smf.wls(f, data=x, weights=1 / x["d_var"]).fit()
            linhas.append({"grupo": g, "prova": p, "efeito_pandemia_no_d": m.params["pandemia"],
                           "ic_inf": m.conf_int().loc["pandemia", 0], "ic_sup": m.conf_int().loc["pandemia", 1],
                           "p": m.pvalues["pandemia"], "n_celulas": len(x)})
    salvar(pd.DataFrame(linhas), "p2_modelo_pandemia.csv")

    # Estabilidade do ranking: correlação EB2 PAS 1 × PAS 3 (e PAS 2 × PAS 3) por coorte
    linhas = []
    for sub in SUBS:
        d = t[t["subprograma"] == sub]
        linhas.append({"subprograma": sub,
                       "anos_letivos_remotos": ", ".join(f"PAS {e}" for e in (1, 2, 3)
                                                         if ano_letivo(sub, e) in ANOS_REMOTOS) or "nenhum",
                       "r_pas1_pas3": d[["eb2_pas1", "eb2_pas3"]].corr().iloc[0, 1],
                       "r_pas2_pas3": d[["eb2_pas2", "eb2_pas3"]].corr().iloc[0, 1],
                       "r_pas1_pas2": d[["eb2_pas1", "eb2_pas2"]].corr().iloc[0, 1],
                       "n": len(d)})
    salvar(pd.DataFrame(linhas), "p2_correlacao_etapas.csv")
    print("ok")


if __name__ == "__main__":
    main()
