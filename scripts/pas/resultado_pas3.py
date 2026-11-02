"""Extrator do resultado final da terceira etapa (PAS 3).

Cada registro do PDF tem a forma
    inscrição, nome, EB1 e1, EB2 e1, NR e1, EB1 e2, EB2 e2, NR e2,
    EB1 e3, EB2 e3, NR e3, argumento final, classificação SU, [cotas...] /
precedido por cabeçalhos de campus/turno e de curso. A lista de cotas é lida
da frase "na seguinte ordem: ..." do próprio edital (ver cotas.py).
"""
import os
import re

from common import (RAW, INSCRICAO_RE, count_inscricoes, flat, norm_key,
                    pdf_pages, to_float, to_int)
import cotas

NOTAS = ['eb1_pas1', 'eb2_pas1', 'nr_pas1',
         'eb1_pas2', 'eb2_pas2', 'nr_pas2',
         'eb1_pas3', 'eb2_pas3', 'nr_pas3']

TITULOS = ('UNIVERSIDADE DE BRAS', 'CENTRO BRASILEIRO', 'CENTRO DE SELE',
           'SELEÇÃO E DE PROMO', 'SELECAO E DE PROMO', 'PROGRAMA DE AVALIA',
           'SUBPROGRAMA', 'EDITAL N')

MARK = re.compile('\x01(.*?)\x02', re.S)


def _is_header(line):
    s = line.strip()
    # linhas com inscrição nunca são cabeçalho (há convocações com nomes em maiúsculas)
    if not s or re.search(r'(?<![\d.])\d{4}\s?\d{4}(?![\d.])', s):
        return False
    letters = [c for c in s if c.isalpha()]
    if len(letters) < 4:
        return False
    upper = sum(c.isupper() for c in letters)
    return upper >= 0.75 * len(letters)


def _is_page_number(line):
    return re.fullmatch(r'\s*\d{1,4}\s*', line) is not None


def build_stream(pages):
    """Texto contínuo com os cabeçalhos marcados como \\x01...\\x02."""
    parts = []
    for page in pages:
        lines = page.splitlines()
        # descarta o número da página no topo
        while lines and (not lines[0].strip() or _is_page_number(lines[0])):
            lines.pop(0)
        for ln in lines:
            s = flat(ln)
            if _is_header(ln) and not s.startswith(TITULOS):
                parts.append('\x01' + s + '\x02')
            elif _is_page_number(ln):
                continue
            else:
                parts.append(ln.replace('‐', '-').replace('–', '-')
                             .replace('−', '-'))
    stream = ''.join(parts)
    # junta cabeçalhos quebrados em duas linhas, ex.: "ENGENHARIAS ..." + "(BACHARELADOS)"
    stream = re.sub('\x02\\s*\x01(?=\\()', ' ', stream)
    stream = re.sub('\x02\\s*\x01(?=- ?SUB JUDICE)', ' ', stream)
    # cabeçalho de curso com parêntese aberto continua na linha seguinte
    def _join(m):
        a = m.group(1)
        return a + ' ' if a.count('(') > a.count(')') or re.search(r'[-/,–]\s*$', a) else m.group(0)
    stream = re.sub('(\x01[^\x02]*)\x02\\s*\x01(?=[A-ZÇÃÕÁÉÍÓÚÂÊÔ(])', _join, stream)
    return stream


def _strip_numbering(h):
    return re.sub(r'^\d+(\.\d+)*\s+', '', h).strip()


def _header_kind(h):
    k = norm_key(_strip_numbering(h))
    if 'SUB JUDICE' in k and '(' not in k:
        return 'sj'
    if k.startswith('CAMPUS'):
        return 'campus'
    if re.search(r'RESULTADO|DISPOSI|MEDIA E DESVIO|PRIMEIRA ETAPA|SEGUNDA ETAPA|'
                 r'TERCEIRA ETAPA|DECANO', k):
        return 'section'
    if '(' in k and ')' in k:
        return 'curso'
    # cursos sem parênteses: "BACHARELADO EM QUÍMICA", "LICENCIATURA EM FÍSICA",
    # "CIÊNCIAS SOCIAIS - ANTROPOLOGIA/SOCIOLOGIA BACHARELADO/LICENCIATURA"
    if re.search(r'BACHAREL|LICENCIA', k):
        return 'curso'
    return 'other'


def parse_campus(h):
    """'CAMPUS DARCY RIBEIRO – DIURNO' -> ('CAMPUS DARCY RIBEIRO', 'DIURNO')."""
    k = norm_key(_strip_numbering(h))
    m = re.match(r'(.*?)\s*-\s*(DIURNO|NOTURNO|INTEGRAL)\s*$', k)
    if m:
        return m.group(1), m.group(2)
    return k, ''


def parse_curso(h):
    k = norm_key(_strip_numbering(h))
    sj = 'SUB JUDICE' in k
    k = re.sub(r'\s*/\s*CANDIDATOS\s+SUB JUDICE.*$', '', k)  # "DIREITO (BACHARELADO)/ CANDIDATOS SUB JUDICE"
    k = re.sub(r'\s*-?\s*SUB JUDICE\s*', '', k).strip(' -*')
    return k, sj


def find_ordem(stream):
    """Frase de ordem do resultado final e a posição onde os registros começam."""
    idx = [m.start() for m in re.finditer(r'argumento\s*final', stream)]
    for i in idx:
        cands = [m.start() for m in re.finditer(r'na\s*seguinte\s*ordem', stream[max(0, i - 1500):i])]
        if not cands:
            continue
        j = max(0, i - 1500) + cands[-1]
        # a frase termina no primeiro cabeçalho ou registro depois dela
        m = re.search('\x01|' + INSCRICAO_RE.pattern, stream[i:])
        end = i + (m.start() if m else 0)
        return flat(stream[j:end]), end
    raise ValueError('frase de ordem do resultado final não encontrada')


def parse_resultado(path, subprograma, sub_judice_file=False, fallback=None):
    pages = pdf_pages(path)
    stream = build_stream(pages)
    try:
        ordem, start = find_ordem(stream)
        labels = cotas.ordem_classificacoes(ordem[ordem.find('argumento'):])
        meta = {'faixa_renda': cotas.faixa_renda(ordem),
                'quilombola': cotas.tem_quilombola(ordem),
                'cotas': labels}
    except ValueError:
        # editais sub judice curtos repetem o formato do resultado principal
        if fallback is None:
            raise
        meta, start = fallback, 0
        labels = meta['cotas']
    n_fields = 2 + len(NOTAS) + 1 + len(labels)

    rows, problems = [], []
    campus = turno = curso = ''
    sj_secao = False
    region = stream[start:]
    pieces = MARK.split(region)
    expected = 0
    for k, piece in enumerate(pieces):
        if k % 2 == 1:  # cabeçalho
            kind = _header_kind(piece)
            if kind == 'campus':
                campus, turno = parse_campus(piece)
                sj_secao = False
            elif kind == 'curso':
                novo, sj_novo = parse_curso(piece)
                # subseção sub judice com o nome do curso cortado ("TECNOLÓGICA (BACHARELADO) -
                # SUB JUDICE" logo depois de "QUÍMICA TECNOLÓGICA (BACHARELADO)"): mesmo curso
                if not (sj_novo and curso and curso.endswith(novo)):
                    curso = novo
                sj_secao = sj_novo
            elif kind == 'sj':
                sj_secao = True
            elif kind == 'section' and rows:
                break  # fim da seção de resultados
            continue
        expected += count_inscricoes(piece)
        # subseções dentro do curso ("Resultado final dos candidatos sub judice
        # não eliminados no PAS, na seguinte ordem: ...") repetem a frase de ordem
        recs = []
        for sub in re.split(r'(?<=[\d-])\.\s*(?=(?:\d+(?:\.\d+)*\s+)?Resultado\s*final)', piece):
            if re.match(r'(?:\d+(?:\.\d+)*\s+)?Resultado\s*final', sub):
                cab = sub[:sub.find('(se houver).') + 1] if '(se houver).' in sub else sub[:300]
                sj_sub = 'subjudice' in re.sub(r'\s', '', cab.lower())
                sub = sub[len(cab):]
            else:
                sj_sub = None
            # registros colados sem a barra separadora
            sub = re.sub(r'(,\s*(?:-|\d+))\s+(?=\d{4}\s?\d{4}\s*,)', r'\1 /', sub)
            for rec in sub.split('/'):
                recs.append((rec, sj_sub))
        sj_atual = None
        for rec, sj_sub in recs:
            if sj_sub is not None:
                sj_atual = sj_sub
            rec = rec.split('*')[0]  # notas de rodapé ("* Cursos que exigem...")
            if not INSCRICAO_RE.search(rec):
                continue
            fields = [f.strip() for f in rec.split(',')]
            # o último campo é uma classificação (inteiro ou '-'); descarta o que
            # vier depois dele (ponto final, notas de rodapé, '[...]')
            m_last = re.match(r'\s*(-|\d+)', fields[-1])
            if m_last:
                fields[-1] = m_last.group(1)
            # sinal negativo separado do número por vírgula: "-, 2.843"
            for q in range(len(fields) - 1):
                if (fields[q] == '-' and len(fields) == n_fields + 1
                        and re.fullmatch(r'\d+\.\d{3}', fields[q + 1].replace(' ', ''))):
                    fields[q:q + 2] = ['-' + fields[q + 1]]
                    break
            # descarta lixo antes da inscrição (texto de cabeçalho, '[...]')
            while fields:
                m_insc = re.search(r'(\d[\d ]{6,9}\d)\s*$', fields[0])
                if m_insc and len(m_insc.group(1).replace(' ', '')) == 8:
                    fields[0] = m_insc.group(1).replace(' ', '')
                    break
                fields.pop(0)
            if len(fields) != n_fields:
                # nome com vírgula: junta os campos excedentes no nome
                if len(fields) > n_fields and len(fields) - n_fields <= 2 and not any(
                        re.search(r'\d', f) for f in fields[2:2 + len(fields) - n_fields]):
                    extra = len(fields) - n_fields
                    fields = [fields[0], ', '.join(fields[1:2 + extra])] + fields[2 + extra:]
                if len(fields) != n_fields:
                    problems.append(flat(rec)[:160])
                    continue
            try:
                notas = [to_float(x) for x in fields[2:2 + len(NOTAS)]]
                af = to_float(fields[2 + len(NOTAS)])
                cls = [to_int(x) for x in fields[3 + len(NOTAS):]]
            except ValueError:
                problems.append(flat(rec)[:160])
                continue
            row = {'subprograma': subprograma,
                   'inscricao': fields[0].replace(' ', ''),
                   'nome': flat(fields[1]),
                   'campus': campus, 'turno': turno, 'curso': curso,
                   'sub_judice': bool(sub_judice_file or sj_secao or sj_atual)}
            row.update(dict(zip(NOTAS, notas)))
            row['argumento_final'] = af
            for lab in cotas.TODAS:
                row['class_' + lab] = None
            for lab, v in zip(labels, cls):
                row['class_' + lab] = v
            rows.append(row)
    stats = {'arquivo': os.path.relpath(path, RAW), 'esperados': expected,
             'extraidos': len(rows), 'problemas': problems}
    return rows, meta, stats


def files_for(subprograma):
    d = os.path.join(RAW, subprograma, 'PAS3', 'Resultado_final')
    out = []
    for name in sorted(os.listdir(d)):
        if name.endswith('.pdf'):
            out.append((os.path.join(d, name), name.upper().startswith('SJ')))
    # resultado principal primeiro
    out.sort(key=lambda x: x[1])
    return out


def extract(subprograma):
    rows, metas, stats = [], [], []
    by_insc = {}
    for path, sj in files_for(subprograma):
        r, m, s = parse_resultado(path, subprograma, sub_judice_file=sj,
                                  fallback=metas[0] if metas else None)
        for row in r:
            old = by_insc.get(row['inscricao'])
            if old is not None and sj:
                # retificação por decisão judicial: mantém o curso se o SJ não trouxer
                for key in ('campus', 'turno', 'curso'):
                    if not row[key]:
                        row[key] = old[key]
                old.update(row)
                s['retificados'] = s.get('retificados', 0) + 1
            elif old is None:
                by_insc[row['inscricao']] = row
                rows.append(row)
        metas.append(m)
        stats.append(s)
    return rows, metas[0], stats


if __name__ == '__main__':
    import sys
    from common import SUBPROGRAMAS
    for sp in sys.argv[1:] or SUBPROGRAMAS:
        rows, meta, stats = extract(sp)
        for s in stats:
            print(sp, s['arquivo'], 'esperados', s['esperados'], 'extraidos', s['extraidos'],
                  'problemas', len(s['problemas']))
            for p in s['problemas'][:3]:
                print('   ', p)
        print('   cotas:', meta['cotas'], meta['faixa_renda'], 'quilombola' if meta['quilombola'] else '')
