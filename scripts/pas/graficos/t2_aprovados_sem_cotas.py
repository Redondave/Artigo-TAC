"""T2 — Simulação de aprovação sem cotas para os cursos de TI.

Saída: results/computacao/candidatos_geral/T2/
"""
from __future__ import annotations

import argparse
import re

from pathlib import Path

import pandas as pd

from comum_graficos import GRUPOS, PARSED, carregar_alunos, ordem_subprogramas, pasta_saida


TABELA_ALUNOS_PADRAO = "tabela1_alunos_sem_14_16.csv"
TABELA_VAGAS_PADRAO = "tabela2_curso_cota_sem_14_16.csv"


def _nome_arquivo(valor: str) -> str:
    nome = re.sub(r"[^A-Za-z0-9]+", "_", str(valor)).strip("_")
    return nome or "curso_sem_nome"


def _ler_vagas(nome: str) -> pd.DataFrame:
    caminho = PARSED / nome
    if not caminho.exists():
        raise SystemExit(f"Arquivo de vagas não encontrado: {caminho}")

    vagas = pd.read_csv(caminho, low_memory=False, dtype=str)
    faltando = [c for c in ("subprograma", "curso", "area_computacao", "vagas") if c not in vagas]
    if faltando:
        raise SystemExit(f"Colunas ausentes em {nome}: {faltando}")

    vagas["vagas"] = pd.to_numeric(vagas["vagas"], errors="coerce").fillna(0)
    return vagas[vagas["area_computacao"].notna() & vagas["curso"].notna()].copy()


def _selecionar_subprogramas(
    df: pd.DataFrame, ultimos: int, selecionados: list[str] | None
) -> list[str]:
    disponiveis = ordem_subprogramas(df["subprograma"].dropna())
    if selecionados:
        ausentes = sorted(set(selecionados) - set(disponiveis))
        if ausentes:
            raise SystemExit(
                f"Subprogramas não encontrados na tabela de alunos: {', '.join(ausentes)}"
            )
        return selecionados
    if ultimos < 1:
        raise SystemExit("--ultimos deve ser maior que zero")
    return disponiveis[-ultimos:]


def calcular(
    alunos: pd.DataFrame, vagas: pd.DataFrame, subprogramas: list[str]
) -> pd.DataFrame:
    alunos = alunos[
        alunos["subprograma"].isin(subprogramas)
        & alunos["curso"].notna()
        & alunos["argumento_final"].notna()
    ].copy()
    vagas = vagas[vagas["subprograma"].isin(subprogramas)]

    vagas_curso = (
        vagas.groupby(["subprograma", "curso"], as_index=False)["vagas"]
        .sum()
        .rename(columns={"vagas": "vagas_totais"})
    )
    cursos = sorted(alunos["curso"].unique())
    linhas = []

    for subprograma in subprogramas:
        for curso in cursos:
            candidatos = alunos[
                (alunos["subprograma"] == subprograma) & (alunos["curso"] == curso)
            ].copy()
            if candidatos.empty:
                continue

            vaga = vagas_curso[
                (vagas_curso["subprograma"] == subprograma)
                & (vagas_curso["curso"] == curso)
            ]
            if vaga.empty:
                raise SystemExit(
                    f"Não há vagas na tabela 2 para {curso} no subprograma {subprograma}"
                )
            n_vagas = int(vaga.iloc[0]["vagas_totais"])
            candidatos = candidatos.sort_values(
                ["argumento_final", "id_aluno"], ascending=[False, True], kind="mergesort"
            )
            selecionados = candidatos.head(n_vagas)
            contagem = (
                selecionados["grupo_concorrencia"]
                .fillna("Não informado")
                .value_counts()
                .to_dict()
            )
            candidatos_grupo = (
                candidatos["grupo_concorrencia"].fillna("Não informado").value_counts().to_dict()
            )

            grupos = list(GRUPOS)
            grupos.extend(
                sorted((set(candidatos_grupo) | set(contagem)) - set(grupos))
            )
            for grupo in grupos:
                n_selecionados = int(contagem.get(grupo, 0))
                linhas.append(
                    {
                        "subprograma": subprograma,
                        "curso": curso,
                        "vagas_totais": n_vagas,
                        "n_candidatos_com_argumento": len(candidatos),
                        "grupo_concorrencia": grupo,
                        "n_vagas_ocupadas_sem_cotas": n_selecionados,
                        "percentual_vagas_sem_cotas": (
                            100 * n_selecionados / n_vagas if n_vagas else 0
                        ),
                        "n_candidatos_do_grupo": int(candidatos_grupo.get(grupo, 0)),
                    }
                )

    if not linhas:
        raise SystemExit("Nenhum candidato de TI com argumento_final foi encontrado.")
    return pd.DataFrame(linhas)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_ALUNOS_PADRAO, help="CSV de alunos em parsed_data/")
    ap.add_argument("--tabela-vagas", default=TABELA_VAGAS_PADRAO, help="CSV de vagas em parsed_data/")
    ap.add_argument("--ultimos", type=int, default=3, help="Quantidade de subprogramas mais recentes")
    ap.add_argument(
        "--subprogramas",
        nargs="+",
        help="Lista explícita de subprogramas; substitui --ultimos",
    )
    args = ap.parse_args()

    alunos = carregar_alunos(args.tabela)
    subprogramas = _selecionar_subprogramas(alunos, args.ultimos, args.subprogramas)
    resultado = calcular(alunos, _ler_vagas(args.tabela_vagas), subprogramas)

    saida = pasta_saida("T2", escopo="computacao", homologados=False)
    
    for subprograma, por_subprograma in resultado.groupby("subprograma", sort=False):
        pasta = saida / subprograma
        pasta.mkdir(parents=True, exist_ok=True)
        for curso, tabela in por_subprograma.groupby("curso", sort=True):
            tabela.to_csv(
                pasta / f"T2_{_nome_arquivo(curso)}.csv",
                index=False,
                float_format="%.2f",
            )
    resultado.to_csv(saida / "T2_resumo.csv", index=False, float_format="%.2f")
    print(f"Subprogramas: {', '.join(subprogramas)}")
    print(f"{len(resultado)} linhas salvas em {saida}")


if __name__ == "__main__":
    main()