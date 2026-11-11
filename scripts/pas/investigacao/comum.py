"""Funções comuns da investigação do "paradoxo" (cotas acima do SUE na Computação).

Tudo é lido de parsed_data/ e escrito em results/investigacao_paradoxo/.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[3]
PARSED = RAIZ / "parsed_data"
SAIDA = RAIZ / "results" / "investigacao_paradoxo"
SAIDA.mkdir(parents=True, exist_ok=True)

SUBS = ["15-17", "16-18", "17-19", "18-20", "19-21", "20-22", "21-23", "22-24", "23-25"]
GRUPOS = ["Universal", "Negros", "EP PPI", "EP Não-PPI"]
CURSOS = {"CC_BACHARELADO": "Ciência da Computação",
          "ENG_COMPUTACAO": "Engenharia de Computação",
          "COMPUTACAO_LICENCIATURA": "Licenciatura em Computação"}
PROVAS = [f"{p}_pas{e}" for e in (1, 2, 3) for p in ("eb1", "eb2", "nr")]
NUM = PROVAS + ["argumento_final"]
RNG_SEED = 42


def carregar(todos_os_inscritos: bool = False) -> pd.DataFrame:
    """Tabela 1 (sem Eng. Software). Por padrão, só quem fez o PAS 3 e tem cota
    declarada (o universo das figuras F1-F3). `cotista` = não SU; `ep` = EP."""
    t = pd.read_csv(PARSED / "tabela1_alunos_sem_eng_soft.csv", low_memory=False,
                    dtype={"subprograma": str, "id_aluno": str})
    for c in NUM:
        t[c] = pd.to_numeric(t[c], errors="coerce")
    for c in ["compareceu_pas1", "compareceu_pas2", "compareceu_pas3", "aprovado", "sub_judice"]:
        t[c] = t[c].astype(str).str.strip().str.lower().eq("true")
    if not todos_os_inscritos:
        t = t[t["compareceu_pas3"] & t["sistema_inscricao"].notna()].copy()
    t["af"] = t["argumento_final"]
    t["comp"] = t["area_computacao"].notna()
    t["ep"] = t["grupo_concorrencia"].isin(["EP PPI", "EP Não-PPI"])
    t["curso_chave"] = t["campus"].astype(str) + "|" + t["turno"].astype(str) + "|" + t["curso"].astype(str)
    return t


def limpa(x) -> np.ndarray:
    return pd.to_numeric(pd.Series(x), errors="coerce").dropna().to_numpy(float)


def descrever(x) -> dict:
    a = limpa(x)
    if len(a) == 0:
        return {"n": 0}
    q = np.percentile(a, [10, 25, 50, 75, 90])
    return {"n": len(a), "media": a.mean(), "mediana": q[2],
            "media_aparada_5": stats.trim_mean(a, 0.05) if len(a) >= 3 else np.nan,
            "variancia": a.var(ddof=1) if len(a) > 1 else np.nan,
            "desvio_padrao": a.std(ddof=1) if len(a) > 1 else np.nan,
            "p10": q[0], "p25": q[1], "p75": q[3], "p90": q[4], "iqr": q[3] - q[1],
            "minimo": a.min(), "maximo": a.max(),
            "assimetria": stats.skew(a) if len(a) > 2 else np.nan}


def cohen_d(ref, alvo) -> dict:
    """Mesma fórmula de scripts/pas/graficos/comum_graficos.cohen_d (d>0 = SUE à frente)."""
    a, b = limpa(ref), limpa(alvo)
    n1, n2 = len(a), len(b)
    out = {"d": np.nan, "d_ic_inf": np.nan, "d_ic_sup": np.nan, "d_var": np.nan}
    if n1 < 2 or n2 < 2:
        return out
    sp = np.sqrt(((n1 - 1) * a.var(ddof=1) + (n2 - 1) * b.var(ddof=1)) / (n1 + n2 - 2))
    d = (a.mean() - b.mean()) / sp
    v = (n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2))
    out.update(d=d, d_ic_inf=d - 1.96 * np.sqrt(v), d_ic_sup=d + 1.96 * np.sqrt(v), d_var=v)
    return out


def comparar(ref, alvo, n_boot: int = 2000, n_perm: int = 5000, seed: int = RNG_SEED) -> dict:
    """SUE (ref) contra um grupo de cota (alvo). Diferenças positivas = SUE à frente."""
    a, b = limpa(ref), limpa(alvo)
    out = {"n_sue": len(a), "n_cota": len(b)}
    if len(a) < 2 or len(b) < 2:
        return out
    rng = np.random.default_rng(seed)
    out["dif_media"] = a.mean() - b.mean()
    out["dif_mediana"] = np.median(a) - np.median(b)
    out["dif_media_aparada"] = stats.trim_mean(a, .05) - stats.trim_mean(b, .05)
    bm, bmed = np.empty(n_boot), np.empty(n_boot)
    for i in range(n_boot):
        ra, rb = rng.choice(a, len(a)), rng.choice(b, len(b))
        bm[i] = ra.mean() - rb.mean()
        bmed[i] = np.median(ra) - np.median(rb)
    out["dif_media_ic_inf"], out["dif_media_ic_sup"] = np.percentile(bm, [2.5, 97.5])
    out["dif_mediana_ic_inf"], out["dif_mediana_ic_sup"] = np.percentile(bmed, [2.5, 97.5])
    out["p_welch"] = stats.ttest_ind(a, b, equal_var=False).pvalue
    out["p_mann_whitney"] = stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
    # teste de permutação da diferença de médias
    junt = np.r_[a, b]
    obs = abs(out["dif_media"])
    cont = 0
    for _ in range(n_perm):
        rng.shuffle(junt)
        cont += abs(junt[:len(a)].mean() - junt[len(a):].mean()) >= obs
    out["p_permutacao"] = (cont + 1) / (n_perm + 1)
    out["p_levene_variancia"] = stats.levene(a, b).pvalue
    out.update(cohen_d(a, b))
    return out


def salvar(df: pd.DataFrame, nome: str) -> Path:
    p = SAIDA / nome
    df.to_csv(p, index=False, float_format="%.4f")
    return p
