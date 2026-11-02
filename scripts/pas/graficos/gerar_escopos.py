"""Gera F1, F2 e F3 para escopos além do padrão (computação junta).

    geral  -> results/geral/F1, F2, F3          todos os cursos da UnB no PAS
    curso  -> results/curso/F1, F2, F3/<área>   um curso de computação por vez
                                                (valores de `area_computacao`)
    computacao -> results/F1, F2, F3            o padrão (opcional aqui)

Usa as mesmas funções `executar` dos scripts f1/f2/f3 (mesmas figuras, mesmas
subpastas exploracao/), só trocando o recorte dos dados. O CSV é lido uma vez.

Uso:  python scripts/pas/graficos/gerar_escopos.py [--escopos geral curso computacao]
      [--tabela ARQ.csv] [--sem-ic] [--metrica argumento_final] [--min-n 5]
"""
from __future__ import annotations

import argparse

import f1_escore_medio_componente as f1
import f2_gap_cohen_d as f2
import f3_heatmap_gap_categorias as f3
from comum_graficos import COLUNAS_NUMERICAS, TABELA_PADRAO, pasta_saida, recortes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV em parsed_data/")
    ap.add_argument("--escopos", nargs="+", choices=["geral", "curso", "computacao"],
                    default=["geral", "curso"])
    ap.add_argument("--sem-ic", action="store_true", help="não desenha as faixas de IC95%%")
    ap.add_argument("--metrica", default="argumento_final", choices=COLUNAS_NUMERICAS)
    ap.add_argument("--min-n", type=int, default=5)
    args = ap.parse_args()

    for df, escopo, area in recortes(args.tabela, tuple(args.escopos)):
        rotulo = f"{escopo} {area or ''}".strip()
        print(f"\n===== {rotulo} ({len(df)} candidatos) =====")
        f1.executar(df, pasta_saida("F1", escopo, area), com_ic=not args.sem_ic)
        f2.executar(df, pasta_saida("F2", escopo, area), com_ic=not args.sem_ic)
        f3.executar(df, pasta_saida("F3", escopo, area), args.metrica, args.min_n)


if __name__ == "__main__":
    main()