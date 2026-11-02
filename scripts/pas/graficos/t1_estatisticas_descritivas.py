"""T1 (Apêndice) — Estatísticas descritivas completas.

Para cada combinação de subprograma x cota x prova x etapa calcula n, média,
desvio-padrão (amostral, ddof=1) e mediana. 

Saída (results/computacao/candidatos_geral/T1/):
    T1_estatisticas_descritivas.csv   formato longo (uma linha por combinação)
    T1_estatisticas_descritivas.tex   longtable pronta para \\input{} 

Uso:  python scripts/pas/graficos/t1_estatisticas_descritivas.py [--cota grupo]
"""
from __future__ import annotations

import argparse

import pandas as pd

from comum_graficos import (
    CATEGORIAS,
    ETAPAS,
    GRUPOS,
    PROVAS,
    TABELA_PADRAO,
    carregar_alunos,
    ordem_subprogramas,
    pasta_saida,
)

ORDEM_PROVA = ["Argumento final"] + [PROVAS[p] for p in PROVAS]


def calcular(df: pd.DataFrame, coluna_cota: str, ordem_cotas: list[str]) -> pd.DataFrame:
    base = pd.concat([df, df.assign(**{coluna_cota: "Todos"})], ignore_index=True)

    medidas = [("Argumento final", None, "argumento_final")] + [
        (PROVAS[p], e, f"{p}_pas{e}") for p in PROVAS for e in ETAPAS
    ]
    partes = []
    for prova, etapa, col in medidas:
        g = (
            base.groupby(["subprograma", coluna_cota])[col]
            .agg(n="count", media="mean", dp="std", mediana="median")
            .reset_index()
            .rename(columns={coluna_cota: "cota"})
        )
        g.insert(2, "prova", prova)
        g.insert(3, "etapa", float(etapa) if etapa is not None else float("nan"))
        partes.append(g)
    t = pd.concat(partes, ignore_index=True)

    t["_sub"] = t["subprograma"].map({s: i for i, s in enumerate(ordem_subprogramas(t["subprograma"]))})
    t["_cota"] = t["cota"].map({c: i for i, c in enumerate(ordem_cotas + ["Todos"])})
    t["_prova"] = t["prova"].map({p: i for i, p in enumerate(ORDEM_PROVA)})
    t = t.sort_values(["_sub", "_cota", "_prova", "etapa"], na_position="first")
    t = t.drop(columns=["_sub", "_cota", "_prova"]).reset_index(drop=True)
    t["etapa"] = t["etapa"].astype("Int64")
    return t


def _esc(s) -> str:
    return str(s).replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")


def para_latex(t: pd.DataFrame) -> str:
    def num(x, casas=3):
        return "--" if pd.isna(x) else f"{x:.{casas}f}"

    cab = r"Subprograma & Cota & Prova & Etapa & $n$ & Média & DP & Mediana \\"
    linhas = [
        r"\begin{longtable}{lllcrrrr}",
        r"\caption{Estatísticas descritivas por subprograma, cota, prova e etapa.}\label{tab:t1-descritivas}\\",
        r"\toprule", cab, r"\midrule", r"\endfirsthead",
        r"\toprule", cab, r"\midrule", r"\endhead",
        r"\bottomrule", r"\endfoot",
    ]
    anterior = None
    for r in t.itertuples(index=False):
        if anterior is not None and r.subprograma != anterior:
            linhas.append(r"\midrule")
        anterior = r.subprograma
        etapa = "--" if pd.isna(r.etapa) else int(r.etapa)
        linhas.append(
            f"{_esc(r.subprograma)} & {_esc(r.cota)} & {_esc(r.prova)} & {etapa} & "
            f"{r.n} & {num(r.media)} & {num(r.dp)} & {num(r.mediana)} \\\\"
        )
    linhas.append(r"\end{longtable}")
    return "\n".join(linhas) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV em parsed_data/")
    ap.add_argument("--cota", choices=["categoria", "grupo"], default="categoria")
    args = ap.parse_args()

    df = carregar_alunos(args.tabela)
    if args.cota == "categoria":
        coluna, ordem = "sistema_inscricao", CATEGORIAS
    else:
        coluna, ordem = "grupo_concorrencia", GRUPOS
        if coluna not in df.columns:
            raise SystemExit(f"Coluna {coluna} ausente em {args.tabela}")

    t = calcular(df, coluna, ordem)

    saida = pasta_saida("T1", homologados=False)
    t.to_csv(saida / "T1_estatisticas_descritivas.csv", index=False, float_format="%.3f")
    (saida / "T1_estatisticas_descritivas.tex").write_text(para_latex(t), encoding="utf-8")
    print(f"  {len(t)} linhas salvas em {saida}")


if __name__ == "__main__":
    main()