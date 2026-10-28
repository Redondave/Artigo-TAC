"""Extrator das convocações para registro acadêmico e das relações de selecionados.

Convocação: lista, por campus/curso, quem foi chamado em cada chamada e semestre,
com o sistema/subsistema da vaga. Há dois formatos:
  código:        "inscrição nome código" + legenda "(1) Sistema Universal (2) ..."
  classificação: cabeçalho "SISTEMA UNIVERSAL" etc. e "inscrição, nome, posição"
                 (subprograma 15-17)
Relação de selecionados: quem teve o registro acadêmico homologado.
"""
import os
import re

from common import RAW, flat, norm_key, pdf_pages
import cotas
from resultado_pas3 import MARK, build_stream, parse_campus, parse_curso, _strip_numbering

INSC = r'(\d(?:\s?\d){7})'
REC_RE = re.compile(r'(?<![\d.])' + INSC + r'\s*,?\s+([^\d\x01\x02/]+?)\s*,?\s*(\d{1,4})(?![\d.])')
NOME_INSC_RE = re.compile(r'(?<![\d.])' + INSC + r'(?![\d.])')

ORDINAIS = {'PRIMEIR': 1, 'SEGUND': 2, 'TERCEIR': 3, 'QUART': 4, 'QUINT': 5,
            'SEXT': 6, 'SETIM': 7, 'SÉTIM': 7, 'OITAV': 8, 'NON': 9, 'DECIM': 10}


def _from_name(name):
    m = re.match(r'(\d+)_chamada_(\d)_semestre', name)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def _marker_kind(h):
    k = norm_key(_strip_numbering(h))
    if k.startswith('CAMPUS'):
        return 'campus'
    if re.search(r'\bSEMESTRE\b', k) and len(k) < 40:
        return 'semestre'
    if k.startswith('SISTEMA'):
        return 'sistema'
    if 'SUB JUDICE' in k and '(' not in k:
        return 'sj'
    if '(' in k and ')' in k and not re.match(r'(DA|DO|DOS|DAS)\b', k):
        return 'curso'
    if re.match(r'(DA|DO|DOS|DAS)\b', k):
        return 'section'
    return 'other'


def parse_convocacao(path, subprograma, chamada, semestre, sj_file=False):
    pages = pdf_pages(path)
    text = flat(' '.join(pages))
    stream = build_stream(pages)
    # legenda de códigos, quando existe
    legenda = {}
    i = text.find('(1)')
    if i >= 0:
        legenda = cotas.legenda_convocacao(text[i:i + 3000].split('CAMPUS')[0])
    modo = 'codigo' if legenda else 'classificacao'
    m_ord = re.search(r'na\s*seguinte\s*ordem', stream)
    start = m_ord.end() if m_ord else 0

    rows = []
    campus = turno = curso = ''
    sem = semestre
    sistema_txt = ''
    sj = False
    last_kind = None
    pieces = MARK.split(stream[start:])
    for k, piece in enumerate(pieces):
        if k % 2 == 1:
            kind = _marker_kind(piece)
            if kind == 'other' and last_kind == 'sistema':
                sistema_txt += ' ' + piece
                continue
            if kind == 'campus':
                campus, turno = parse_campus(piece)
                sj = False
            elif kind == 'curso':
                curso, sj = parse_curso(piece)
            elif kind == 'semestre':
                kk = norm_key(piece)
                sem = 1 if 'PRIMEIRO' in kk else 2 if 'SEGUNDO' in kk else sem
            elif kind == 'sistema':
                sistema_txt = piece
            elif kind == 'sj':
                sj = True
            elif kind == 'section' and rows:
                break
            last_kind = kind
            continue
        if kind_is_texto(piece):
            last_kind = None
        for m in REC_RE.finditer(piece):
            insc = m.group(1).replace(' ', '')
            nome = flat(m.group(2)).strip(' ,')
            num = int(m.group(3))
            if modo == 'codigo':
                cota = legenda.get(num)
                classif = None
            else:
                try:
                    cota = cotas.classify_item(sistema_txt) if sistema_txt else None
                except ValueError:
                    cota = None
                classif = num
            rows.append({'subprograma': subprograma, 'inscricao': insc, 'nome': nome,
                         'campus': campus, 'turno': turno, 'curso': curso,
                         'chamada': chamada, 'semestre': sem, 'cota': cota,
                         'classificacao_cota': classif,
                         'sub_judice': bool(sj or sj_file),
                         'arquivo': os.path.relpath(path, RAW)})
    return rows, {'arquivo': os.path.relpath(path, RAW), 'modo': modo,
                  'legenda': len(legenda), 'extraidos': len(rows),
                  'sem_cota': sum(r['cota'] is None for r in rows)}


def kind_is_texto(piece):
    return bool(piece.strip())


def parse_sj_convocacao(path, subprograma):
    """Editais curtos de convocação sub judice: só a inscrição e o semestre."""
    text = flat(' '.join(pdf_pages(path)))
    rows = []
    for m in re.finditer(r'inscri\w*\s*n\s*[º°o]\s*' + INSC, text):
        trecho = text[m.end():m.end() + 400]
        sem = 1 if 'primeiro semestre' in trecho.lower() else 2 if 'segundo semestre' in trecho.lower() else None
        rows.append({'subprograma': subprograma, 'inscricao': m.group(1).replace(' ', ''),
                     'nome': '', 'campus': '', 'turno': '', 'curso': '',
                     'chamada': None, 'semestre': sem, 'cota': None,
                     'classificacao_cota': None, 'sub_judice': True,
                     'arquivo': os.path.relpath(path, RAW)})
    return rows, {'arquivo': os.path.relpath(path, RAW), 'modo': 'sub judice',
                  'legenda': 0, 'extraidos': len(rows), 'sem_cota': len(rows)}


def extract_convocacoes(subprograma):
    d = os.path.join(RAW, subprograma, 'PAS3', 'Convocacao_para_registro_academico')
    rows, stats = [], []
    if not os.path.isdir(d):
        return rows, stats
    for name in sorted(os.listdir(d)):
        if not name.endswith('.pdf'):
            continue
        path = os.path.join(d, name)
        text = flat(' '.join(pdf_pages(path)))
        if name.upper().startswith('SJ'):
            r, s = parse_sj_convocacao(path, subprograma)
        elif 'RELAÇÃO DOS CANDIDATOS EM LISTA DE ESPERA' in text.upper() or \
                'curso/turno.' in text and 'Nome do candidato Inscrição' in text:
            # lista de espera (15-17) e relação de homologados arquivada aqui (18-20)
            continue
        else:
            chamada, semestre = _from_name(name)
            if chamada is None:
                # convocação geral de 15-17: primeira chamada dos dois semestres
                chamada = 1
            r, s = parse_convocacao(path, subprograma, chamada, semestre)
        rows += r
        stats.append(s)
    return rows, stats


def extract_relacoes(subprograma):
    """Inscrições com registro homologado (ou selecionadas, em 14-16), por arquivo."""
    out, stats = [], []
    dirs = [os.path.join(RAW, subprograma, 'PAS3', 'Relacao_das_pessoas_selecionadas')]
    # 18-20 guarda uma retificação de homologados na pasta de convocação
    extra = os.path.join(RAW, subprograma, 'PAS3', 'Convocacao_para_registro_academico', 'retificacao.pdf')
    for d in dirs:
        if not os.path.isdir(d):
            continue
        files = [os.path.join(d, n) for n in sorted(os.listdir(d)) if n.endswith('.pdf')]
        if os.path.exists(extra):
            files.append(extra)
        for path in files:
            name = os.path.basename(path)
            text = flat(' '.join(pdf_pages(path)))
            chamada, semestre = _from_name(name)
            m = re.search(r'na\s*seguinte\s*ordem', text)
            body = text[m.end():] if m else text
            body = re.sub(r'Processo\s*n\s*[º°o]\s*[\d\s.\-]+', ' ', body)
            body = re.sub(r'Edital\s*n\s*[º°o][^,]*', ' ', body)
            inscs = {x.replace(' ', '') for x in NOME_INSC_RE.findall(body)}
            homologacao = 'homolog' in text.lower()[:3000] or 'pré-registro' in text.lower()[:3000]
            for insc in sorted(inscs):
                out.append({'subprograma': subprograma, 'inscricao': insc,
                            'chamada': chamada, 'semestre': semestre,
                            'tipo': 'homologado' if homologacao else 'selecionado',
                            'sub_judice': name.upper().startswith('SJ'),
                            'arquivo': os.path.relpath(path, RAW)})
            stats.append({'arquivo': os.path.relpath(path, RAW), 'extraidos': len(inscs),
                          'tipo': 'homologado' if homologacao else 'selecionado'})
    return out, stats


if __name__ == '__main__':
    import sys
    from common import SUBPROGRAMAS
    for sp in sys.argv[1:] or SUBPROGRAMAS:
        rows, stats = extract_convocacoes(sp)
        for s in stats:
            print(sp, s['arquivo'].split('/')[-1], s['modo'], 'legenda', s['legenda'],
                  'extraidos', s['extraidos'], 'sem_cota', s['sem_cota'])
        rel, st2 = extract_relacoes(sp)
        print(sp, 'CONVOCADOS', len(rows), 'RELACOES', len(rel), {s['tipo'] for s in st2})
