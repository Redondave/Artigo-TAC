"""Utilidades compartilhadas pelos scripts de figuras e tabelas do artigo.

Não é executado diretamente: é importado por f2_*.py, f3_*.py e t1_*.py,
que ficam na mesma pasta (o import funciona sem configurar PYTHONPATH).

Convenção de pastas (relativa à raiz do repositório, que é calculada a partir
da posição deste arquivo: scripts/pas/graficos/ -> raiz = 3 níveis acima):
    parsed_data/   <- entrada (CSVs do pipeline)
    results/computacao/<grupo>/Fx/       <- computação (escopo padrão)
    results/geral/<grupo>/Fx/            <- todos os cursos
    results/por_curso/<área>/<grupo>/Fx/ <- um curso de computação por vez
    
    Onde <grupo> é 'candidatos_geral' ou 'candidatos_convocados_para_homologacao'.
"""
from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[3]
PARSED = RAIZ / "parsed_data"
RESULTS = RAIZ / "results"

TABELA_PADRAO = "tabela1_alunos_sem_eng_soft.csv"
SUBPROGRAMAS_PADRAO = "subprogramas_sem_eng_soft.csv"

# Ordem de exibição: referência, Negros, depois EP por renda (R1 -> R2),
# raça (PPI -> NPPI) e deficiência (PCD logo após a categoria geral).
CATEGORIAS = [
    "SU",
    "NEG",
    "EP_R1_PPI",
    "EP_R1_PPI_PCD",
    "EP_R1_NPPI",
    "EP_R1_NPPI_PCD",
    "EP_R2_PPI",
    "EP_R2_PPI_PCD",
    "EP_R2_NPPI",
    "EP_R2_NPPI_PCD",
]

ROTULOS = {
    "SU": "Sistema Universal (ref.)",
    "NEG": "Cotas para Negros",
    "EP_R1_PPI": "EP, renda ≤ lim., PPI",
    "EP_R1_PPI_PCD": "EP, renda ≤ lim., PPI, PCD",
    "EP_R1_NPPI": "EP, renda ≤ lim., não PPI",
    "EP_R1_NPPI_PCD": "EP, renda ≤ lim., não PPI, PCD",
    "EP_R2_PPI": "EP, renda > lim., PPI",
    "EP_R2_PPI_PCD": "EP, renda > lim., PPI, PCD",
    "EP_R2_NPPI": "EP, renda > lim., não PPI",
    "EP_R2_NPPI_PCD": "EP, renda > lim., não PPI, PCD",
}

# Agrupamentos de `grupo_concorrencia` (linhas da F1) e cores fixas por grupo.
GRUPOS = ["Universal", "Negros", "EP PPI", "EP Não-PPI"]
COR_GRUPO = {
    "Universal": "#222222",
    "Negros": "#d95f02",
    "EP PPI": "#1b9e77",
    "EP Não-PPI": "#7570b3",
}

# Universal "estrito" = quem só tem classificação no Sistema Universal
# (`sistema_inscricao == "SU"`, valor que `grupo_concorrencia` chama de
# "Universal"). Universal "amplo" = todos os candidatos, pois o glossário diz
# que todo candidato tem classificação em SU, inclusive os cotistas.
GRUPO_AMPLO = "Universal amplo"
ROTULO_GRUPO = {
    "Universal": "Universal estrito (só SU)",
    "Negros": "Negros",
    "EP PPI": "EP PPI",
    "EP Não-PPI": "EP Não-PPI",
    GRUPO_AMPLO: "Universal amplo (todos)",
}
COR_AMPLO = "0.55"

PROVAS = {
    "eb1": "EB1 (Parte I)",
    "eb2": "EB2 (Parte II)",
    "nr": "NR (redação)",
}
ETAPAS = (1, 2, 3)

COLUNAS_NUMERICAS = ["argumento_final"] + [
    f"{p}_pas{e}" for p in PROVAS for e in ETAPAS
]


# --------------------------------------------------------------------------
# Entrada / saída
# --------------------------------------------------------------------------
def pasta_saida(nome: str, escopo: str = "computacao", area=None, homologados: bool = False) -> Path:
    """Cria (se preciso) e devolve a pasta de saída de `nome` (F1, F2, ...):
        computacao -> results/computacao/<grupo>/<nome>
        geral      -> results/geral/<grupo>/<nome>
        curso      -> results/por_curso/<área>/<grupo>/<nome>
    """
    grupo = "candidatos_convocados_para_homologacao" if homologados else "candidatos_geral"
    
    if escopo == "geral":
        pasta = RESULTS / "geral" / grupo / nome
    elif escopo == "curso":
        pasta = RESULTS / "por_curso" / str(area) / grupo / nome
    else:
        pasta = RESULTS / "computacao" / grupo / nome
        
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def ordem_subprogramas(valores) -> list[str]:
    """Ordena '15-17', '16-18', ... pelo ano inicial (não alfabeticamente)."""
    return sorted(set(map(str, valores)), key=lambda s: int(s.split("-")[0]))


def nome_metrica(coluna: str) -> str:
    """'eb2_pas3' -> 'EB2 (Parte II), 3ª etapa'; 'argumento_final' -> 'Argumento final'."""
    if coluna == "argumento_final":
        return "Argumento final"
    prova, pas = coluna.split("_pas")
    return f"{PROVAS[prova]}, {pas}ª etapa"


def grupo_de_cota(valor):
    """Traduz o texto de `cota_aprovacao` para um dos 4 grupos de
    `grupo_concorrencia` (Universal, Negros, EP PPI, EP Não-PPI).
    Devolve None quando não reconhece o valor (ex.: EP sem divisão PPI/não PPI)."""
    if pd.isna(valor):
        return None
    v = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode().upper().strip()
    if v == "SU" or "UNIVERSAL" in v:
        return "Universal"
    if v == "NEG" or "NEGRO" in v:
        return "Negros"
    if v.startswith("EP") or "ESCOLA" in v:
        if "NPPI" in v or "NAO" in v:
            return "EP Não-PPI"
        if "PPI" in v:
            return "EP PPI"
    return None


def carregar_alunos(nome: str = TABELA_PADRAO, escopo: str = "computacao") -> pd.DataFrame:
    """Lê a tabela 1 e deixa só candidatos que chegaram à classificação do
    PAS 3 (único momento em que `sistema_inscricao` existe).

    escopo="computacao" (padrão): só cursos com `area_computacao` preenchida.
        O filtro já exclui Eng. de Software nas tabelas `_sem_eng_soft` (o
        pipeline apaga o rótulo, mantendo as linhas).
    escopo="geral": todos os cursos.

    Também cria `aprovado_bool` (coluna `aprovado` como booleano).
    """
    caminho = PARSED / nome
    if not caminho.exists():
        sys.exit(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(
        caminho,
        low_memory=False,
        dtype={
            "id_aluno": str,
            "subprograma": str,
            "area_computacao": str,
            "sistema_inscricao": str,
            "grupo_concorrencia": str,
            "cota_aprovacao": str,
            "curso": str,
        },
    )
    faltando = [
        c
        for c in ["subprograma", "area_computacao", "sistema_inscricao"]
        + COLUNAS_NUMERICAS
        if c not in df.columns
    ]
    if faltando:
        sys.exit(f"Colunas ausentes em {nome}: {faltando}")

    for c in COLUNAS_NUMERICAS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    if "aprovado" in df.columns:
        df["aprovado_bool"] = df["aprovado"].astype(str).str.strip().str.lower().eq("true")
    else:
        df["aprovado_bool"] = False

    n_total = len(df)
    df = df[df["sistema_inscricao"].notna()].copy()
    if escopo == "computacao":
        df = df[df["area_computacao"].notna()].copy()

    desconhecidas = set(df["sistema_inscricao"]) - set(CATEGORIAS)
    if desconhecidas:
        print(f"[aviso] sistema_inscricao fora da lista esperada: {sorted(desconhecidas)}")

    onde = "de computação" if escopo == "computacao" else "(todos os cursos)"
    print(
        f"{nome}: {n_total} linhas -> {len(df)} candidatos {onde} "
        f"com sistema_inscricao, em {df['subprograma'].nunique()} subprogramas."
    )
    return df


def recortes(nome: str = TABELA_PADRAO, escopos=("computacao",)):
    """Gera (df, escopo, area) para cada escopo pedido, lendo o CSV uma só vez.

    escopos: "computacao" (cursos de computação juntos), "geral" (todos os
    cursos) e "curso" (um recorte por valor de `area_computacao`).
    """
    base = carregar_alunos(nome, "geral")
    for escopo in escopos:
        if escopo == "geral":
            yield base, "geral", None
        elif escopo == "computacao":
            yield base[base["area_computacao"].notna()].copy(), "computacao", None
        elif escopo == "curso":
            for area in sorted(base["area_computacao"].dropna().unique()):
                yield base[base["area_computacao"] == area].copy(), "curso", area


def indice_lei_14723(subs: list[str], nome: str = SUBPROGRAMAS_PADRAO):
    """Posição (em `subs`) do primeiro subprograma sob a Lei 14.723/2023,
    lida da coluna `lei_14723` de subprogramas*.csv. None se não achar."""
    caminho = PARSED / nome
    if not caminho.exists():
        return None
    t = pd.read_csv(caminho, dtype=str)
    if "lei_14723" not in t.columns:
        return None
    sob_lei = set(
        t.loc[t["lei_14723"].str.strip().str.lower() == "true", "subprograma"]
    )
    for i, s in enumerate(subs):
        if s in sob_lei:
            return i
    return None


# --------------------------------------------------------------------------
# Estatística
# --------------------------------------------------------------------------
def cohen_d(ref, alvo) -> dict:
    """d de Cohen com desvio-padrão combinado e IC 95% (aproximação normal).

        d = (média_ref − média_alvo) / dp_combinado

    Sinal: d > 0 significa que o grupo de referência (Sistema Universal) está
    à frente do grupo-alvo (cotistas). NaNs são descartados antes do cálculo.
    Com n < 2 em algum dos grupos (ou variância nula) devolve d = NaN.
    """
    a = pd.to_numeric(pd.Series(ref), errors="coerce").dropna().to_numpy(float)
    b = pd.to_numeric(pd.Series(alvo), errors="coerce").dropna().to_numpy(float)
    n1, n2 = len(a), len(b)
    out = {"d": np.nan, "ic_inf": np.nan, "ic_sup": np.nan, "n_ref": n1, "n_alvo": n2}
    if n1 < 2 or n2 < 2:
        return out
    sp = np.sqrt(((n1 - 1) * a.var(ddof=1) + (n2 - 1) * b.var(ddof=1)) / (n1 + n2 - 2))
    if sp == 0:
        return out
    d = (a.mean() - b.mean()) / sp
    ep = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))
    out.update(d=d, ic_inf=d - 1.96 * ep, ic_sup=d + 1.96 * ep)
    return out


# --------------------------------------------------------------------------
# Gráficos
# --------------------------------------------------------------------------
def aplicar_estilo() -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 11,
            "legend.frameon": False,
            "figure.dpi": 110,
            "savefig.bbox": "tight",
        }
    )


def marcar_lei(ax, idx) -> None:
    """Linha vertical entre o último subprograma antes e o primeiro sob a Lei 14.723."""
    if idx is None or idx == 0:
        return
    ax.axvline(idx - 0.5, ls="--", lw=1, color="0.35", zorder=0)
    ax.text(
        idx - 0.42,
        0.98,
        "Lei 14.723/2023",
        transform=ax.get_xaxis_transform(),
        va="top",
        ha="left",
        fontsize=7,
        color="0.35",
    )


def salvar(fig, pasta: Path, nome: str) -> None:
    """Salva PNG (300 dpi) e PDF (vetorial, para o LaTeX)."""
    for ext in ("png", "pdf"):
        caminho = pasta / f"{nome}.{ext}"
        fig.savefig(caminho, dpi=300)
        print(f"  salvo: {caminho.relative_to(RAIZ)}")