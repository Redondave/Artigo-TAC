"""F7 — Posição dos cursos de TI nas notas de corte.

Cada painel mostra um curso de TI. Cada linha representa uma categoria de
concorrência e acompanha a nota de corte ao longo dos subprogramas. Os pontos
são anotados com a posição ordinal do curso entre todos os cursos, da maior
para a menor nota de corte. A faixa de fundo mostra a média dos demais cursos
e um desvio-padrão em torno dela.

Para melhorar a leitura, as categorias originais são agrupadas em cinco
macrocategorias: SU, NEG, EP/PCD, EP/PPI e EP/RI.

Quando existem várias células para o mesmo curso, subprograma e categoria
(campus, turno ou semestre), a nota usada no gráfico é a mediana dessas
células. A tabela de saída também informa quantas células foram agregadas.

Uso:
    python scripts/pas/graficos/f7_seletividade_cursos.py
    python scripts/pas/graficos/f7_seletividade_cursos.py --nota-corte primeira
"""
from __future__ import annotations

import argparse
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comum_graficos import CATEGORIAS, PARSED, ordem_subprogramas, pasta_saida


TABELA_PADRAO = "tabela2_curso_cota_sem_14_16.csv"
MACROCATEGORIAS = ["SU", "NEG", "EP/PCD", "EP/PPI", "EP/RI"]
ROTULOS_MACRO = {
    "SU": "Sistema Universal",
    "NEG": "Cotas para Negros",
    "EP/PCD": "EP / PCD",
    "EP/PPI": "EP / PPI",
    "EP/RI": "EP / renda",
}
CORES_MACRO = {
    "SU": "#222222",
    "NEG": "#d95f02",
    "EP/PCD": "#7570b3",
    "EP/PPI": "#1b9e77",
    "EP/RI": "#e7298a",
}


def _ler_tabela(nome: str, coluna_nota: str) -> pd.DataFrame:
    caminho = PARSED / nome
    if not caminho.exists():
        raise SystemExit(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho, low_memory=False)
    obrigatorias = [
        "subprograma",
        "curso",
        "categoria",
        "area_computacao",
        coluna_nota,
    ]
    faltando = [c for c in obrigatorias if c not in df.columns]
    if faltando:
        raise SystemExit(f"Colunas ausentes em {nome}: {faltando}")

    df[coluna_nota] = pd.to_numeric(df[coluna_nota], errors="coerce")
    df = df[
        df["subprograma"].notna()
        & df["curso"].notna()
        & df["categoria"].isin(CATEGORIAS)
        & df[coluna_nota].notna()
    ].copy()
    if df.empty:
        raise SystemExit(f"Nenhuma nota de corte válida foi encontrada em {nome}.")
    # A prioridade evita sobreposição: PCD, depois PPI; o restante das
    # escolas públicas fica na categoria residual de renda.
    df["categoria"] = df["categoria"].map(
        lambda categoria: (
            categoria
            if categoria in {"SU", "NEG"}
            else "EP/PCD"
            if categoria.endswith("_PCD")
            else "EP/PPI"
            if categoria.endswith("_PPI")
            else "EP/RI"
        )
    )
    return df


def calcular(df: pd.DataFrame, coluna_nota: str) -> pd.DataFrame:
    """Agrega as células e calcula a posição ordinal dos cursos."""
    chaves = ["subprograma", "curso", "categoria"]
    t = (
        df.groupby(chaves, as_index=False)
        .agg(
            nota_corte=(coluna_nota, "median"),
            n_celulas=(coluna_nota, "count"),
            eh_ti=("area_computacao", lambda s: s.notna().any()),
        )
    )
    t["tipo_curso"] = np.where(t["eh_ti"], "TI", "Demais cursos")

    ranking = t.groupby(["subprograma", "categoria"])["nota_corte"]
    t["posicao_nota_corte"] = ranking.rank(method="min", ascending=False).astype("Int64")
    t["n_cursos_ranking"] = ranking.transform("count").astype("Int64")

    calibracao = t[t["tipo_curso"] == "Demais cursos"]
    resumo_calibracao = (
        calibracao.groupby(["subprograma", "categoria"], as_index=False)
        .agg(
            media_demais_cursos=("nota_corte", "mean"),
            dp_demais_cursos=("nota_corte", "std"),
        )
    )
    t = t.merge(resumo_calibracao, on=["subprograma", "categoria"], how="left")
    percentis = []
    for row in t[t["eh_ti"]].itertuples(index=False):
        valores = calibracao.loc[
            (calibracao["subprograma"] == row.subprograma)
            & (calibracao["categoria"] == row.categoria),
            "nota_corte",
        ]
        percentis.append(
            {
                "subprograma": row.subprograma,
                "curso": row.curso,
                "categoria": row.categoria,
                "percentil_demais_cursos": (
                    100 * (valores <= row.nota_corte).mean() if len(valores) else np.nan
                ),
                "n_cursos_calibracao": len(valores),
            }
        )
    p = pd.DataFrame(percentis)
    t = t.merge(p, on=["subprograma", "curso", "categoria"], how="left")
    t["categoria_rotulo"] = t["categoria"].map(ROTULOS_MACRO).fillna(t["categoria"])
    ordem_sub = {s: i for i, s in enumerate(ordem_subprogramas(t["subprograma"]))}
    ordem_cat = {c: i for i, c in enumerate(MACROCATEGORIAS)}
    t["_ordem_sub"] = t["subprograma"].map(ordem_sub)
    t["_ordem_cat"] = t["categoria"].map(ordem_cat)
    return t.sort_values(["curso", "_ordem_sub", "_ordem_cat"]).drop(
        columns=["_ordem_sub", "_ordem_cat"]
    )


def _nome_arquivo(valor: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", valor).strip("_")


def _ordinal(valor) -> str:
    """Formata uma posição inteira como ordinal em português."""
    return f"{int(valor)}º" if pd.notna(valor) else ""


def criar_figura(t: pd.DataFrame, nota_corte: str):
    ti = t[t["eh_ti"]].copy()
    cursos = sorted(ti["curso"].unique())
    categorias = [c for c in MACROCATEGORIAS if c in t["categoria"].values]
    fig, axes = plt.subplots(2, 2, figsize=(18, 11), sharey=True)
    axes = axes.ravel()
    subs = ordem_subprogramas(t["subprograma"])
    x = np.arange(len(subs))
    cores = {categoria: CORES_MACRO[categoria] for categoria in categorias}

    for ax, curso in zip(axes, cursos):
        dados_curso = ti[ti["curso"] == curso]
        for categoria in categorias:
            pontos = (
                dados_curso[dados_curso["categoria"] == categoria]
                .set_index("subprograma")
                .reindex(subs)
            )
            if pontos["nota_corte"].notna().sum() == 0:
                continue
            medias = (
                t[
                    (~t["eh_ti"])
                    & (t["categoria"] == categoria)
                ]
                .groupby("subprograma")["nota_corte"]
                .mean()
                .reindex(subs)
            )
            desvios = (
                t[
                    (~t["eh_ti"])
                    & (t["categoria"] == categoria)
                ]
                .groupby("subprograma")["nota_corte"]
                .std()
                .reindex(subs)
                .fillna(0)
            )
            faixa_inferior = medias - desvios
            faixa_superior = medias + desvios
            valido = medias.notna().to_numpy()
            if valido.any():
                ax.fill_between(
                    x[valido],
                    faixa_inferior.to_numpy()[valido],
                    faixa_superior.to_numpy()[valido],
                    color="#bdbdbd",
                    alpha=0.12,
                    linewidth=0,
                    zorder=0,
                )
            linha = ax.plot(
                x,
                pontos["nota_corte"],
                marker="o",
                linewidth=1.5,
                markersize=4,
                color=cores[categoria],
                label=ROTULOS_MACRO[categoria],
                zorder=3,
            )[0]
            for pos, nota, ordinal in zip(
                x, pontos["nota_corte"], pontos["posicao_nota_corte"]
            ):
                if pd.notna(nota) and pd.notna(ordinal):
                    ax.annotate(
                        _ordinal(ordinal),
                        (pos, nota),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=7,
                        color=linha.get_color(),
                    )
        ax.set_title(curso, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(subs, rotation=45, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.25)
        ax.axhline(0, color="#888888", linewidth=0.7)

    for ax in axes[len(cursos) :]:
        ax.set_visible(False)
    axes[0].set_ylabel(f"Nota de corte ({nota_corte})")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, title="Categoria de cota", loc="upper center", ncol=3)
    fig.suptitle(
        "Posição dos cursos de TI nas notas de corte da UnB",
        y=0.99,
        fontsize=14,
    )
    fig.text(
        0.5,
        0.01,
        "Anotações: posição ordinal entre todos os cursos (1º = maior nota). "
        "Faixa cinza: média ± 1 desvio-padrão dos demais cursos.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tabela", default=TABELA_PADRAO, help="CSV da tabela 2 em parsed_data/")
    ap.add_argument(
        "--nota-corte",
        choices=["primeira", "ultima"],
        default="ultima",
        help="Nota de corte a usar: primeira ou última chamada",
    )
    args = ap.parse_args()

    coluna_nota = {
        "primeira": "nota_corte_1a_chamada",
        "ultima": "nota_corte_ultima_chamada",
    }[args.nota_corte]
    dados = calcular(_ler_tabela(args.tabela, coluna_nota), coluna_nota)
    saida = pasta_saida("F7")
    dados.to_csv(saida / "F7_dados.csv", index=False, float_format="%.3f")
    dados[dados["eh_ti"]].to_csv(saida / "F7_ti.csv", index=False, float_format="%.3f")

    fig = criar_figura(dados, args.nota_corte)
    for extensao in ("png", "pdf"):
        fig.savefig(saida / f"F7_seletividade_cursos.{extensao}", dpi=300)
    plt.close(fig)
    print(f"{len(dados)} linhas agregadas; {dados['eh_ti'].sum()} linhas de TI.")
    print(f"Arquivos salvos em {saida}")


if __name__ == "__main__":
    main()
