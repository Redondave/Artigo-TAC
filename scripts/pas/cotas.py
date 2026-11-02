"""Vocabulário padronizado das categorias de concorrência.

Os editais descrevem as cotas por extenso e a lista muda ao longo da década
(renda de 1,5 SM ou 1 SM, inclusão de PcD e de quilombolas). Em vez de fixar um
cabeçalho, este módulo lê a descrição do próprio edital e devolve os rótulos:

    SU            Sistema Universal
    NEG           Sistema de Cotas para Negros
    EP_R1_PPI     Escola pública, renda baixa (até o limite), PPI
    EP_R1_PPI_PCD Escola pública, renda baixa, PPI, pessoa com deficiência
    EP_R1_NPPI    Escola pública, renda baixa, não PPI
    EP_R1_NPPI_PCD
    EP_R2_PPI     Escola pública, renda acima do limite, PPI
    EP_R2_PPI_PCD
    EP_R2_NPPI
    EP_R2_NPPI_PCD

"PPI" inclui quilombolas a partir do subprograma 2022 (Lei 14.723/2023).
"""
import re

from common import strip_accents

TODAS = ['SU', 'NEG',
         'EP_R1_PPI', 'EP_R1_PPI_PCD', 'EP_R1_NPPI', 'EP_R1_NPPI_PCD',
         'EP_R2_PPI', 'EP_R2_PPI_PCD', 'EP_R2_NPPI', 'EP_R2_NPPI_PCD']

DESCRICAO = {
    'SU': 'Sistema Universal',
    'NEG': 'Sistema de Cotas para Negros',
    'EP_R1_PPI': 'Escola pública, renda até o limite, PPI',
    'EP_R1_PPI_PCD': 'Escola pública, renda até o limite, PPI, com deficiência',
    'EP_R1_NPPI': 'Escola pública, renda até o limite, não PPI',
    'EP_R1_NPPI_PCD': 'Escola pública, renda até o limite, não PPI, com deficiência',
    'EP_R2_PPI': 'Escola pública, renda acima do limite, PPI',
    'EP_R2_PPI_PCD': 'Escola pública, renda acima do limite, PPI, com deficiência',
    'EP_R2_NPPI': 'Escola pública, renda acima do limite, não PPI',
    'EP_R2_NPPI_PCD': 'Escola pública, renda acima do limite, não PPI, com deficiência',
}

# Agrupamentos usados nos gráficos (F1 a F3 do plano do artigo)
GRUPO = {
    'SU': 'Universal',
    'NEG': 'Negros',
    'EP_R1_PPI': 'EP PPI', 'EP_R1_PPI_PCD': 'EP PPI',
    'EP_R2_PPI': 'EP PPI', 'EP_R2_PPI_PCD': 'EP PPI',
    'EP_R1_NPPI': 'EP Não-PPI', 'EP_R1_NPPI_PCD': 'EP Não-PPI',
    'EP_R2_NPPI': 'EP Não-PPI', 'EP_R2_NPPI_PCD': 'EP Não-PPI',
}


def _compact(text):
    return re.sub(r'\s+', '', strip_accents(text).lower())


def classify_item(item):
    """Rótulo padronizado para a descrição de uma categoria."""
    c = _compact(item)
    if 'sistemauniversal' in c and 'escolas' not in c:
        return 'SU'
    if 'cotasparanegros' in c or 'cotasparapessoasnegras' in c:
        return 'NEG'
    if 'renda' not in c:
        raise ValueError(f'categoria não reconhecida: {item!r}')
    renda = 'R1' if 'igualouinferior' in c else 'R2'
    ppi = 'NPPI' if 'naoseautodeclar' in c else 'PPI'
    pcd = '_PCD' if 'deficiencia' in c else ''
    return f'EP_{renda}_{ppi}{pcd}'


def faixa_renda(text):
    """'1,5 SM' ou '1 SM', conforme o limite de renda citado no texto."""
    c = _compact(text)
    if re.search(r'a1,5salario', c):
        return '1,5 SM'
    if re.search(r'a1salario', c):
        return '1 SM'
    return ''


def tem_quilombola(text):
    return 'quilombola' in _compact(text)


def ordem_classificacoes(sentence):
    """Lista das categorias na ordem em que aparecem nas colunas do resultado.

    `sentence` é a frase "na seguinte ordem: ..." do resultado final,
    a partir de "classificação final no Sistema Universal".
    """
    c = sentence
    i = _compact(c).find('sistemauniversal')
    if i < 0:
        raise ValueError('frase de ordem sem Sistema Universal')
    labels = ['SU']
    if 'cotasparanegros' in _compact(c) or 'cotasparapessoasnegras' in _compact(c):
        labels.append('NEG')
    # Itens de escola pública: depois de "Escolas Públicas:", separados por ';'
    partes = c.split(':')
    if len(partes) > 1:
        resto = ':'.join(partes[1:])
        for item in re.split(r';', resto):
            item = re.sub(r'^\s*e\s+', '', item.strip())
            if 'renda' in _compact(item):
                labels.append(classify_item(item))
    return labels


def legenda_convocacao(text):
    """Mapa código -> rótulo a partir da legenda '(1) Sistema Universal (2) ...'."""
    out = {}
    partes = re.split(r'\((\d{1,2})\)\s*', text)
    # partes = [antes, '1', desc1, '2', desc2, ...]
    for k in range(1, len(partes) - 1, 2):
        cod = int(partes[k])
        desc = partes[k + 1]
        try:
            out[cod] = classify_item(desc)
        except ValueError:
            continue
    return out
