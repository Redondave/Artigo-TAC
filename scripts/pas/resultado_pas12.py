"""Extrator dos resultados finais da primeira e da segunda etapa (PAS 1 e PAS 2).

Há dois formatos ao longo da década:
  completo:  inscrição, nome, EB parte 1, EB parte 2, soma, tipo D, redação
  reduzido:  inscrição, nome, tipo D, redação   (15-17 a 17-19 em algumas etapas)
O formato de cada bloco é lido da frase "na seguinte ordem: ..." que o precede.
Retificações são aplicadas em ordem (retificacao_1, retificacao_2, ...).
"""
import os
import re

from common import RAW, flat, pdf_pages, to_float

ORDEM_RE = re.compile(r'na\s*seguinte\s*o\s*rdem\s*:')
NUM_RE = re.compile(r'\s*(-?\s*\d[\d\s]*\.\s*\d[\d\s]*|-)')


def _formato(sentence):
    c = re.sub(r'\s', '', sentence.lower())
    completo = 'escorebrutonaparte1' in c
    sj = 'subjudice' in c
    provisoria = 'notaprovis' in c
    return completo, sj, provisoria


def parse_file(path, etapa):
    pages = []
    for page in pdf_pages(path):
        lines = page.splitlines()
        # descarta o número da página no topo
        while lines and re.fullmatch(r'\s*\d{0,4}\s*', lines[0]):
            lines.pop(0)
        pages.append('\n'.join(lines))
    text = flat(' '.join(pages))
    # blocos: cada frase de ordem até a próxima
    marks = list(ORDEM_RE.finditer(text))
    rows, problems, expected = [], [], 0
    for k, m in enumerate(marks):
        end = marks[k + 1].start() if k + 1 < len(marks) else len(text)
        dot = text.find('.', m.end())  # fim da frase de ordem
        sentence = text[m.start():dot]
        completo, sj, provisoria = _formato(text[max(0, m.start() - 300):dot])
        if 'nome' not in sentence:
            continue
        n_fields = 7 if completo else 4
        body = text[dot + 1:end]
        body = re.sub(r'(?<=\d)\s+(?=\d{4}\s?\d{4}\s*,)', ' / ', body)
        for rec in body.split('/'):
            mi = re.search(r'(?<![\d.])(\d{4}\s?\d{4})\s*,', rec)
            if not mi:
                continue
            expected += 1
            rec = rec[mi.start():]
            # corta o texto que vem depois do último registro de um bloco
            rec = re.split(r'(?<=\d{3})\.(?:\s|$)|\s\[\.\.\.\]', rec)[0]
            rec = re.split(r'(?<=\d)\s+\d+(?:\.\d+)*\s+[A-ZÀ-Ú]{2,}', rec)[0]
            fields = [f.strip() for f in rec.split(',')]
            fields[0] = fields[0].replace(' ', '')
            if len(fields) < n_fields:
                problems.append(rec[:140])
                continue
            # o nome pode ter vírgula: os números são os últimos n-2 campos
            nums = fields[-(n_fields - 2):]
            m_last = NUM_RE.match(nums[-1])
            if not m_last:
                problems.append(rec[:140])
                continue
            nums[-1] = m_last.group(1)
            try:
                vals = [to_float(x) for x in nums]
            except ValueError:
                problems.append(rec[:140])
                continue
            row = {'inscricao': fields[0], 'etapa': etapa,
                   'sub_judice': sj, 'provisoria': provisoria}
            if completo:
                row.update(eb1=vals[0], eb2=vals[1], soma=vals[2], tipo_d=vals[3], nr=vals[4])
            else:
                row.update(eb1=None, eb2=None, soma=None, tipo_d=vals[0], nr=vals[1])
            rows.append(row)
    return rows, {'arquivo': os.path.relpath(path, RAW), 'esperados': expected,
                  'extraidos': len(rows), 'problemas': problems}


def _ordem_arquivo(name):
    if name.startswith('resultado_final'):
        return (0, 0)
    m = re.search(r'(\d+)', name)
    return (1, int(m.group(1)) if m else 0)


def extract(subprograma, etapa):
    """Dicionário inscrição -> notas da etapa, com retificações aplicadas."""
    d = os.path.join(RAW, subprograma, f'PAS{etapa}', 'Resultado_final')
    if not os.path.isdir(d):
        return {}, []
    files = sorted((f for f in os.listdir(d) if f.endswith('.pdf')), key=_ordem_arquivo)
    out, stats = {}, []
    for name in files:
        rows, st = parse_file(os.path.join(d, name), etapa)
        st['retificacao'] = not name.startswith('resultado_final')
        aplicadas = 0
        for row in rows:
            old = out.get(row['inscricao'])
            if old is None:
                out[row['inscricao']] = row
                continue
            # retificação: atualiza os campos presentes; não troca nota final por provisória
            if row['provisoria'] and not old['provisoria']:
                continue
            for key in ('eb1', 'eb2', 'soma', 'tipo_d', 'nr'):
                if row[key] is not None:
                    old[key] = row[key]
            old['provisoria'] = row['provisoria']
            old['sub_judice'] = old['sub_judice'] or row['sub_judice']
            aplicadas += 1
        st['aplicadas'] = aplicadas
        stats.append(st)
    return out, stats


if __name__ == '__main__':
    import sys
    from common import SUBPROGRAMAS
    for sp in sys.argv[1:] or SUBPROGRAMAS:
        for etapa in (1, 2):
            res, stats = extract(sp, etapa)
            for s in stats:
                print(sp, f'PAS{etapa}', s['arquivo'].split('/')[-1], 'esperados', s['esperados'],
                      'extraidos', s['extraidos'], 'problemas', len(s['problemas']),
                      'aplicadas', s.get('aplicadas'))
                for p in s['problemas'][:2]:
                    print('    ', p)
            if res:
                comp = sum(r['eb1'] is not None for r in res.values())
                print(sp, f'PAS{etapa}', 'TOTAL', len(res), 'com EB', comp,
                      'sj', sum(r['sub_judice'] for r in res.values()))
