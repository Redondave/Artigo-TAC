"""Parte 1, hipóteses H1 a H4: descritivas robustas, testes de diferença,
caudas, influência do topo, cota para Negros e recorte por curso.

Saídas em results/investigacao_paradoxo/:
  p1_descritivas.csv          n, média, mediana, média aparada 5%, variância, dp, quantis
                              (escopo × curso × subprograma × grupo × medida)
  p1_testes_sue_vs_cotas.csv  diferenças SUE − cota com IC bootstrap e p-valores
  p1_retirar_topo.csv         média da cota sem os k melhores (k = 0..3) contra o SUE
  p1_caudas.csv               % de candidatos com AF < 0 e AF < −50, por grupo
  p1_quantis_dif.csv          diferença SUE − cota em cada quantil (p10…p90), com IC
  p1_negros_ks.csv            Negros × SUE e Negros × EP (teste KS, todos os anos juntos)
  p1_quartil_superior.csv     participação de cada grupo no quartil superior do curso
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from comum import (CURSOS, GRUPOS, RNG_SEED, SUBS, carregar, comparar, descrever,
                   limpa, salvar)

MEDIDAS = ["af", "eb2_pas1", "eb2_pas2", "eb2_pas3", "nr_pas3"]


def recortes(t):
    yield "UnB (todos os cursos)", t
    c = t[t["comp"]]
    yield "Computação (3 cursos)", c
    yield "Bacharelados (CC + Eng. Comp.)", c[c["area_computacao"] != "COMPUTACAO_LICENCIATURA"]
    for k, v in CURSOS.items():
        yield v, c[c["area_computacao"] == k]


def main():
    t = carregar()
    rng = np.random.default_rng(RNG_SEED)

    # ---------------- descritivas
    linhas = []
    for nome, d in recortes(t):
        for sub in SUBS + ["todos"]:
            ds = d if sub == "todos" else d[d["subprograma"] == sub]
            for g in GRUPOS + ["Cotas (todas)"]:
                dg = ds[ds["grupo_concorrencia"] != "Universal"] if g == "Cotas (todas)" else ds[ds["grupo_concorrencia"] == g]
                for m in MEDIDAS:
                    linhas.append({"recorte": nome, "subprograma": sub, "grupo": g, "medida": m,
                                   **descrever(dg[m])})
    desc = pd.DataFrame(linhas)
    salvar(desc, "p1_descritivas.csv")

    # ---------------- testes SUE × cotas (AF e EB2 do PAS 3)
    linhas = []
    for nome, d in recortes(t):
        if nome.startswith("UnB"):
            n_boot, n_perm = 500, 500  # n grande: p-valores já são minúsculos
        else:
            n_boot, n_perm = 2000, 5000
        for sub in SUBS + ["todos"]:
            ds = d if sub == "todos" else d[d["subprograma"] == sub]
            sue = ds[ds["grupo_concorrencia"] == "Universal"]
            for g in ["Negros", "EP PPI", "EP Não-PPI", "EP (todas)", "Cotas (todas)"]:
                if g == "EP (todas)":
                    alvo = ds[ds["ep"]]
                elif g == "Cotas (todas)":
                    alvo = ds[ds["grupo_concorrencia"] != "Universal"]
                else:
                    alvo = ds[ds["grupo_concorrencia"] == g]
                for m in ["af", "eb2_pas3"]:
                    linhas.append({"recorte": nome, "subprograma": sub, "grupo": g, "medida": m,
                                   **comparar(sue[m], alvo[m], n_boot, n_perm)})
    testes = pd.DataFrame(linhas)
    salvar(testes, "p1_testes_sue_vs_cotas.csv")

    # ---------------- retirar os k melhores de cada grupo de cota
    linhas = []
    c = t[t["comp"]]
    for sub in SUBS:
        ds = c[c["subprograma"] == sub]
        sue = limpa(ds.loc[ds["grupo_concorrencia"] == "Universal", "af"])
        for g in ["Negros", "EP PPI", "EP Não-PPI"]:
            a = np.sort(limpa(ds.loc[ds["grupo_concorrencia"] == g, "af"]))[::-1]
            for k in range(4):
                linhas.append({"subprograma": sub, "grupo": g, "k_retirados": k,
                               "media_cota": a[k:].mean(), "media_sue": sue.mean(),
                               "cota_acima_do_sue": a[k:].mean() > sue.mean()})
    salvar(pd.DataFrame(linhas), "p1_retirar_topo.csv")

    # ---------------- caudas
    linhas = []
    for nome, d in recortes(t):
        for sub in SUBS + ["todos"]:
            ds = d if sub == "todos" else d[d["subprograma"] == sub]
            for g in GRUPOS:
                a = limpa(ds.loc[ds["grupo_concorrencia"] == g, "af"])
                if len(a):
                    linhas.append({"recorte": nome, "subprograma": sub, "grupo": g, "n": len(a),
                                   "pct_af_negativo": 100 * (a < 0).mean(),
                                   "pct_af_menor_-50": 100 * (a < -50).mean(),
                                   "pct_af_maior_100": 100 * (a > 100).mean()})
    salvar(pd.DataFrame(linhas), "p1_caudas.csv")

    # ---------------- diferença por quantil (Computação, anos juntos e por período)
    linhas = []
    qs = [10, 25, 50, 75, 90]
    periodos = {"todos": SUBS, "15-17 a 21-23": SUBS[:7], "22-24 e 23-25": SUBS[7:]}
    for nome, d in list(recortes(t))[1:]:
        for per, subs in periodos.items():
            dp = d[d["subprograma"].isin(subs)]
            sue = limpa(dp.loc[dp["grupo_concorrencia"] == "Universal", "af"])
            for g in ["Negros", "EP PPI", "EP Não-PPI", "Cotas (todas)"]:
                alvo = dp[dp["grupo_concorrencia"] != "Universal"] if g == "Cotas (todas)" else dp[dp["grupo_concorrencia"] == g]
                b = limpa(alvo["af"])
                if len(b) < 10:
                    continue
                obs = np.percentile(sue, qs) - np.percentile(b, qs)
                boot = np.array([np.percentile(rng.choice(sue, len(sue)), qs) - np.percentile(rng.choice(b, len(b)), qs)
                                 for _ in range(1000)])
                lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
                for i, q in enumerate(qs):
                    linhas.append({"recorte": nome, "periodo": per, "grupo": g, "quantil": f"p{q}",
                                   "n_sue": len(sue), "n_cota": len(b), "quantil_sue": np.percentile(sue, q),
                                   "quantil_cota": np.percentile(b, q), "dif_sue_menos_cota": obs[i],
                                   "ic_inf": lo[i], "ic_sup": hi[i]})
    salvar(pd.DataFrame(linhas), "p1_quantis_dif.csv")

    # ---------------- Negros: a distribuição parece com a do SUE ou com a de EP?
    linhas = []
    for nome, d in list(recortes(t))[:3]:
        for per, subs in periodos.items():
            dp = d[d["subprograma"].isin(subs)]
            neg = limpa(dp.loc[dp["grupo_concorrencia"] == "Negros", "af"])
            sue = limpa(dp.loc[dp["grupo_concorrencia"] == "Universal", "af"])
            ep = limpa(dp.loc[dp["ep"], "af"])
            for ref_nome, ref in [("SUE", sue), ("EP", ep)]:
                ks = stats.ks_2samp(neg, ref)
                linhas.append({"recorte": nome, "periodo": per, "comparacao": f"Negros × {ref_nome}",
                               "n_negros": len(neg), "n_ref": len(ref), "ks_distancia": ks.statistic,
                               "p_valor": ks.pvalue, "mediana_negros": np.median(neg),
                               "mediana_ref": np.median(ref), "dp_negros": neg.std(ddof=1),
                               "dp_ref": ref.std(ddof=1)})
    salvar(pd.DataFrame(linhas), "p1_negros_ks.csv")

    # ---------------- participação no quartil superior de cada curso-ano
    c = t[t["comp"]].copy()
    c["q75"] = c.groupby(["subprograma", "area_computacao"])["af"].transform(lambda s: s.quantile(.75))
    c["topo"] = c["af"] >= c["q75"]
    linhas = []
    for per, subs in periodos.items():
        dp = c[c["subprograma"].isin(subs)]
        for g in GRUPOS:
            dg = dp[dp["grupo_concorrencia"] == g]
            linhas.append({"periodo": per, "grupo": g, "n": len(dg),
                           "pct_no_quartil_superior": 100 * dg["topo"].mean()})
    salvar(pd.DataFrame(linhas), "p1_quartil_superior.csv")
    print("ok")


if __name__ == "__main__":
    main()
