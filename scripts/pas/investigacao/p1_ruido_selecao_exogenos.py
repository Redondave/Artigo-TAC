"""Parte 1, hipóteses H4 a H8: curso, ruído × tendência, efeito de seleção
(população × candidatos de um curso), fatores exógenos e composição.

Saídas em results/investigacao_paradoxo/:
  p1_ultrapassagens.csv        cada comparação de médias de F1 (etapa × prova × grupo × ano)
                               na Computação, com o sinal observado
  p1_ultrapassagens_simulacao.csv  quantas ultrapassagens o acaso produziria se o gap
                               verdadeiro fosse constante (o gap médio da série)
  p1_tendencia_d.csv           meta-regressão do d de Cohen (AF) contra o ano, com Q e I²
  p1_regressao_curso.csv       AF ~ grupo × curso + ano (Computação), erros robustos
  p1_d_por_curso_unb.csv       d (SUE × EP e SUE × Negros) em cada curso da UnB
  p1_decomposicao_unb.csv      gap da UnB inteira × gap médio dentro dos cursos
  p1_seletividade_vs_gap.csv   correlação entre seletividade do curso e o gap
  p1_composicao_periodos.csv   n e quantis por grupo nos períodos (SISUnB, pandemia, lei)
  p1_did_computacao_unb.csv    gap da Computação menos gap da UnB, por período
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from comum import CURSOS, GRUPOS, RNG_SEED, SUBS, carregar, cohen_d, limpa, salvar

ETAPAS_PROVAS = [(e, p) for e in (1, 2, 3) for p in ("eb1", "eb2", "nr")]
PERIODO = {"15-17": "SISUnB", "16-18": "SISUnB", "17-19": "pré-pandemia",
           "18-20": "pandemia", "19-21": "pandemia", "20-22": "pandemia",
           "21-23": "pós-pandemia", "22-24": "Lei 14.723", "23-25": "Lei 14.723"}


def meta_regressao(d, v, x):
    """Regressão ponderada (pesos 1/variância) de d contra x; devolve inclinação,
    erro, p, Q de Cochran e I² (parcela da variação entre anos que não é acaso)."""
    d, v, x = map(np.asarray, (d, v, x))
    w = 1 / v
    dm = np.sum(w * d) / np.sum(w)
    q = np.sum(w * (d - dm) ** 2)
    k = len(d)
    i2 = max(0.0, (q - (k - 1)) / q) if q > 0 else 0.0
    X = np.c_[np.ones(k), x]
    W = np.diag(w)
    cov = np.linalg.inv(X.T @ W @ X)
    b = cov @ X.T @ W @ d
    se = np.sqrt(np.diag(cov))
    z = b[1] / se[1]
    return {"d_medio_ponderado": dm, "inclinacao_por_ano": b[1], "ep_inclinacao": se[1],
            "p_inclinacao": 2 * stats.norm.sf(abs(z)), "Q_cochran": q, "gl": k - 1,
            "p_Q": stats.chi2.sf(q, k - 1), "I2_pct": 100 * i2}


def main():
    t = carregar()
    rng = np.random.default_rng(RNG_SEED)
    c = t[t["comp"]].copy()

    # ---------------- H6a: ultrapassagens observadas × esperadas pelo acaso
    linhas = []
    for sub in SUBS:
        ds = c[c["subprograma"] == sub]
        sue = ds[ds["grupo_concorrencia"] == "Universal"]
        for g in ["Negros", "EP PPI", "EP Não-PPI"]:
            gg = ds[ds["grupo_concorrencia"] == g]
            for e, p in ETAPAS_PROVAS:
                col = f"{p}_pas{e}"
                a, b = limpa(sue[col]), limpa(gg[col])
                if len(a) < 2 or len(b) < 2:
                    continue
                linhas.append({"subprograma": sub, "grupo": g, "etapa": e, "prova": p,
                               "media_sue": a.mean(), "media_cota": b.mean(),
                               "dif": a.mean() - b.mean(),
                               "ep_dif": np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)),
                               "cota_acima": b.mean() > a.mean()})
    ult = pd.DataFrame(linhas)
    salvar(ult, "p1_ultrapassagens.csv")
    # Simulação: o gap verdadeiro de cada (grupo, etapa, prova) é o gap médio da
    # série (constante no tempo). Sorteia a média observada de cada ano com o erro
    # padrão real daquela célula e conta quantas vezes a cota fica acima do SUE.
    ult["gap_medio"] = ult.groupby(["grupo", "etapa", "prova"])["dif"].transform(
        lambda s: np.average(s, weights=1 / ult.loc[s.index, "ep_dif"] ** 2))
    sims = []
    for _ in range(10000):
        sim = rng.normal(ult["gap_medio"], ult["ep_dif"])
        sims.append([(sim < 0).sum(),
                     (sim[ult["prova"].eq("eb2")] < 0).sum(),
                     (sim[ult["prova"].eq("nr")] < 0).sum()])
    sims = np.array(sims)
    obs = [ult["cota_acima"].sum(), ult.loc[ult["prova"].eq("eb2"), "cota_acima"].sum(),
           ult.loc[ult["prova"].eq("nr"), "cota_acima"].sum()]
    res = []
    for i, nome in enumerate(["todas as provas", "EB2", "Redação"]):
        res.append({"conjunto": nome, "comparacoes": int([len(ult), ult["prova"].eq("eb2").sum(),
                                                         ult["prova"].eq("nr").sum()][i]),
                    "ultrapassagens_observadas": int(obs[i]),
                    "esperadas_pelo_acaso_media": sims[:, i].mean(),
                    "esperadas_ic90_inf": np.percentile(sims[:, i], 5),
                    "esperadas_ic90_sup": np.percentile(sims[:, i], 95),
                    "p_observado_maior_ou_igual": (sims[:, i] >= obs[i]).mean()})
    salvar(pd.DataFrame(res), "p1_ultrapassagens_simulacao.csv")

    # ---------------- H6b: tendência do d (AF) ao longo dos anos
    linhas = []
    for escopo, d in [("UnB", t), ("Computação", c),
                      ("Ciência da Computação", c[c["area_computacao"] == "CC_BACHARELADO"]),
                      ("Engenharia de Computação", c[c["area_computacao"] == "ENG_COMPUTACAO"]),
                      ("Licenciatura", c[c["area_computacao"] == "COMPUTACAO_LICENCIATURA"])]:
        for g, filtro in [("EP (todas)", lambda x: x["ep"]),
                          ("Negros", lambda x: x["grupo_concorrencia"] == "Negros")]:
            ds, vs, xs = [], [], []
            for i, sub in enumerate(SUBS):
                x = d[d["subprograma"] == sub]
                r = cohen_d(x.loc[x["grupo_concorrencia"] == "Universal", "af"], x.loc[filtro(x), "af"])
                if np.isfinite(r["d"]):
                    ds.append(r["d"]); vs.append(r["d_var"]); xs.append(i)
            for janela, idx in [("15-17 a 23-25", slice(None)), ("15-17 a 22-24 (sem o último)", slice(0, -1))]:
                linhas.append({"escopo": escopo, "grupo": g, "janela": janela, "n_anos": len(ds[idx]),
                               **meta_regressao(ds[idx], vs[idx], xs[idx])})
    salvar(pd.DataFrame(linhas), "p1_tendencia_d.csv")

    # ---------------- H4: regressão AF ~ grupo × curso + ano (Computação)
    c["curso_nome"] = c["area_computacao"].map(CURSOS)
    m = smf.ols("af ~ C(grupo_concorrencia, Treatment('Universal')) * C(curso_nome, Treatment('Ciência da Computação')) + C(subprograma)",
                data=c).fit(cov_type="HC3")
    reg = pd.DataFrame({"coef": m.params, "ep_robusto": m.bse, "p": m.pvalues,
                        "ic_inf": m.conf_int()[0], "ic_sup": m.conf_int()[1]}).reset_index(names="termo")
    reg = reg[~reg["termo"].str.startswith("C(subprograma)")]
    salvar(reg, "p1_regressao_curso.csv")

    # ---------------- H7: d dentro de cada curso da UnB × d da UnB inteira
    linhas = []
    for (sub, chave), x in t.groupby(["subprograma", "curso_chave"]):
        sue = x.loc[x["grupo_concorrencia"] == "Universal", "af"]
        for g, alvo in [("EP (todas)", x.loc[x["ep"], "af"]),
                        ("Negros", x.loc[x["grupo_concorrencia"] == "Negros", "af"])]:
            if len(sue) >= 10 and len(alvo) >= 5:
                r = cohen_d(sue, alvo)
                linhas.append({"subprograma": sub, "curso": chave, "grupo": g, "n_sue": len(sue),
                               "n_cota": len(alvo), "mediana_sue": sue.median(),
                               "p90_sue": sue.quantile(.9), "computacao": bool(x["comp"].iloc[0]), **r})
    pc = pd.DataFrame(linhas)
    salvar(pc, "p1_d_por_curso_unb.csv")

    linhas = []
    for sub in SUBS + ["todos"]:
        x = t if sub == "todos" else t[t["subprograma"] == sub]
        p = pc if sub == "todos" else pc[pc["subprograma"] == sub]
        for g, alvo in [("EP (todas)", x.loc[x["ep"], "af"]),
                        ("Negros", x.loc[x["grupo_concorrencia"] == "Negros", "af"])]:
            pg = p[p["grupo"] == g]
            w = 1 / pg["d_var"]
            # Variação total do AF decomposta em "entre cursos" e "dentro dos cursos"
            linhas.append({"subprograma": sub, "grupo": g,
                           "d_unb_inteira": cohen_d(x.loc[x["grupo_concorrencia"] == "Universal", "af"], alvo)["d"],
                           "d_medio_dentro_dos_cursos": np.average(pg["d"], weights=w),
                           "mediana_d_cursos": pg["d"].median(),
                           "pct_cursos_com_d_negativo": 100 * (pg["d"] < 0).mean(),
                           "n_cursos": len(pg)})
    salvar(pd.DataFrame(linhas), "p1_decomposicao_unb.csv")

    # Fração da distância da UnB explicada pela escolha do curso: regressão do AF
    # com e sem efeito fixo de curso (por subprograma).
    linhas = []
    for sub in SUBS:
        x = t[t["subprograma"] == sub].copy()
        x["cota"] = x["grupo_concorrencia"].ne("Universal").astype(int)
        b0 = smf.ols("af ~ cota", data=x).fit().params["cota"]
        b1 = smf.ols("af ~ cota + C(curso_chave)", data=x).fit().params["cota"]
        linhas.append({"subprograma": sub, "gap_cota_sem_controle_de_curso": b0,
                       "gap_cota_dentro_do_mesmo_curso": b1,
                       "pct_do_gap_explicado_pela_escolha_do_curso": 100 * (1 - b1 / b0)})
    salvar(pd.DataFrame(linhas), "p1_gap_controlando_curso.csv")

    # Seletividade do curso (mediana do AF do SUE) × gap
    sel = pc.groupby(["curso", "grupo"]).agg(d_medio=("d", "mean"), mediana_sue=("mediana_sue", "mean"),
                                             n_anos=("d", "size"), computacao=("computacao", "first")).reset_index()
    sel = sel[sel["n_anos"] >= 5]
    linhas = []
    for g in ["EP (todas)", "Negros"]:
        s = sel[sel["grupo"] == g]
        rho = stats.spearmanr(s["mediana_sue"], s["d_medio"])
        linhas.append({"grupo": g, "n_cursos": len(s), "spearman_rho": rho.statistic, "p": rho.pvalue})
    salvar(pd.DataFrame(linhas), "p1_seletividade_vs_gap.csv")
    salvar(sel.sort_values(["grupo", "mediana_sue"], ascending=[True, False]), "p1_seletividade_cursos.csv")

    # ---------------- H5/H8: composição por período e diferença em diferenças
    linhas = []
    for nome, d in [("Computação", c), ("UnB", t)]:
        for sub in SUBS:
            x = d[d["subprograma"] == sub]
            for g in GRUPOS:
                a = limpa(x.loc[x["grupo_concorrencia"] == g, "af"])
                linhas.append({"escopo": nome, "subprograma": sub, "periodo": PERIODO[sub], "grupo": g,
                               "n": len(a), "pct_do_total": 100 * len(a) / len(x),
                               "p10": np.percentile(a, 10), "p50": np.median(a), "p90": np.percentile(a, 90),
                               "media": a.mean()})
    salvar(pd.DataFrame(linhas), "p1_composicao_periodos.csv")

    linhas = []
    for sub in SUBS:
        for g, f in [("EP (todas)", lambda x: x["ep"]), ("Negros", lambda x: x["grupo_concorrencia"] == "Negros")]:
            r = {}
            for nome, d in [("comp", c), ("unb", t)]:
                x = d[d["subprograma"] == sub]
                r[nome] = cohen_d(x.loc[x["grupo_concorrencia"] == "Universal", "af"], x.loc[f(x), "af"])
            linhas.append({"subprograma": sub, "periodo": PERIODO[sub], "grupo": g,
                           "d_computacao": r["comp"]["d"], "d_unb": r["unb"]["d"],
                           "diferenca_comp_menos_unb": r["comp"]["d"] - r["unb"]["d"],
                           "ep_diferenca": np.sqrt(r["comp"]["d_var"] + r["unb"]["d_var"])})
    did = pd.DataFrame(linhas)
    salvar(did, "p1_did_computacao_unb.csv")

    # d por etapa (EB2) da coorte: a inversão de 23-25 já existia no PAS 1 e 2?
    linhas = []
    for sub in SUBS:
        x = c[c["subprograma"] == sub]
        for g, f in [("EP (todas)", lambda x: x["ep"]), ("Negros", lambda x: x["grupo_concorrencia"] == "Negros")]:
            for col in ["eb2_pas1", "eb2_pas2", "eb2_pas3", "nr_pas1", "nr_pas2", "nr_pas3", "af"]:
                linhas.append({"subprograma": sub, "grupo": g, "medida": col,
                               **cohen_d(x.loc[x["grupo_concorrencia"] == "Universal", col], x.loc[f(x), col])})
    salvar(pd.DataFrame(linhas), "p1_d_por_etapa_computacao.csv")
    print("ok")


if __name__ == "__main__":
    main()
