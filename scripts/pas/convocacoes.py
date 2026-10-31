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

from common import RAW, flat, norm_key, pdf_pages, strip_accents
import cotas
from resultado_pas3 import MARK, build_stream, parse_campus, parse_curso, _strip_numbering

INSC = r'(\d(?:\s?\d){7})'
# o último registro de cada bloco termina com ponto final ("Gabriele Dantas Gontijo, 2."):
# o número pode ser seguido de ponto, desde que não seja um decimal
REC_RE = re.compile(r'(?<![\d.])' + INSC + r'\s*,?\s+([^\d\x01\x02/]+?)\s*,?\s*(\d{1,4})(?!\d)(?!\.\d)')
NOME_INSC_RE = re.compile(r'(?<![\d.])' + INSC + r'(?![\d.])')

ORDINAIS = {'PRIMEIR': 1, 'SEGUND': 2, 'TERCEIR': 3, 'QUART': 4, 'QUINT': 5,
            'SEXT': 6, 'SETIM': 7, 'SÉTIM': 7, 'OITAV': 8, 'NON': 9, 'DECIM': 10}


# 15-17: a 1ª convocação dos dois semestres é a "convocação geral" (Edital nº 38, de 27/1/2018).
# O Edital nº 46, de 20/6/2018 (arquivo 1_chamada_2_semestre.pdf), não traz o ordinal no texto,
# mas fica entre a geral e a "terceira convocação" do 2º semestre (Edital nº 47): é a 2ª chamada.
CHAMADA_CORRIGIDA = {('15-17', '1_chamada_2_semestre.pdf'): 2}


def chamada_no_texto(text):
    """Número da chamada dito no próprio edital ("segunda convocação", "em terceira chamada")."""
    m = re.search(r'torna[m]?\s+p[úu]blicas?\s+(?:a\s+rela[çc][ãa]o[^.]{0,200}?e\s+)?a\s+'
                  r'(?:convoca[çc][ãa]o,?\s+em\s+)?(\w+)\s+(?:convoca|chamada)', text[:3000], re.I)
    if not m:
        return None
    w = strip_accents(m.group(1)).upper()
    for k, v in ORDINAIS.items():
        if w.startswith(strip_accents(k)):
            return v
    return None


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
    if re.search(r'BACHAREL|LICENCIA', k):
        return 'curso'  # cursos sem parênteses ("LICENCIATURA EM FÍSICA")
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
            ch_texto = chamada_no_texto(text)
            if chamada is None:
                # convocação geral de 15-17: primeira chamada dos dois semestres
                chamada = 1
            if (subprograma, name) in CHAMADA_CORRIGIDA:
                chamada = CHAMADA_CORRIGIDA[(subprograma, name)]
            elif ch_texto and ch_texto != chamada:
                chamada = ch_texto
            # 18-20: as convocações são para o "quantitativo total das vagas", sem semestre
            cab = text[:2500].lower()
            if 'quantitativo total das vagas' in cab and 'semestre' not in cab:
                semestre = 0
            r, s = parse_convocacao(path, subprograma, chamada, semestre)
            s['chamada_nome_arquivo'] = _from_name(name)[0]
            s['chamada_texto'] = ch_texto
            s['chamada_usada'] = chamada
        rows += r
        stats.append(s)
    # O mesmo bloco pode aparecer duas vezes no PDF (21-23, Enfermagem no 2º semestre):
    # remove registros idênticos. Editais SJ que só repetem a convocação de quem já
    # foi convocado (reenvio de documentos) marcam o registro como sub judice.
    vistos, regulares, out = set(), {}, []
    removidos = 0
    for r in rows:
        if r['chamada'] is None:
            continue
        key = (r['inscricao'], r['campus'], r['curso'], r['semestre'], r['chamada'], r['cota'])
        if key in vistos:
            removidos += 1
            continue
        vistos.add(key)
        regulares.setdefault(r['inscricao'], []).append(r)
        out.append(r)
    sj_repetidos = 0
    for r in rows:
        if r['chamada'] is not None:
            continue
        if r['inscricao'] in regulares:
            for x in regulares[r['inscricao']]:
                x['sub_judice'] = True
            sj_repetidos += 1
        else:
            out.append(r)
    stats.append({'arquivo': '(deduplicação)', 'modo': 'dedup', 'legenda': 0,
                  'extraidos': -removidos, 'sem_cota': 0,
                  'duplicados_removidos': removidos, 'sj_ja_convocados': sj_repetidos})
    return out, stats


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
