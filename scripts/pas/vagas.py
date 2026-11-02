"""Extrator do quadro de vagas dos editais de abertura da terceira etapa.

Cada linha do quadro tem o curso seguido de 10 números (Negros, 8 subsistemas de
escola pública e Universal) e, a partir de 2020, também o total, que aparece no
fim (2020, 2021, 2025) ou no começo (2022 a 2024). A ordem das 8 colunas de
escola pública muda conforme o cabeçalho do quadro; ela é deduzida da ordem em
que os rótulos de renda e de raça aparecem no cabeçalho de cada edital.
"""
import os
import re

from common import RAW, flat, norm_key, pdf_pages, strip_accents


def _compact(t):
    return re.sub(r'\s+', '', strip_accents(t).lower())


def ordem_ep(header):
    """Lista com os 8 rótulos de escola pública, na ordem das colunas."""
    c = _compact(header)
    renda = [('R1' if m.group(1) == 'igualouinferior' else 'R2') for m in
             re.finditer(r'renda\w*?bruta(igualouinferior|superior)a1(?:,5)?salario', c)]
    raca = [('NPPI' if m.group(1) else 'PPI') for m in
            re.finditer(r'(nao)?seautodeclararam', c)]
    if len(renda) == 4 and len(raca) == 4:
        cells = list(zip(renda, raca))
    elif len(raca) == 2 and len(renda) == 4:
        cells = [(renda[0], raca[0]), (renda[1], raca[0]), (renda[2], raca[1]), (renda[3], raca[1])]
    elif len(renda) == 2 and len(raca) == 4:
        cells = [(renda[0], raca[0]), (renda[0], raca[1]), (renda[1], raca[2]), (renda[1], raca[3])]
    else:
        raise ValueError(f'cabeçalho do quadro de vagas não reconhecido: renda={renda} raça={raca}')
    out = []
    for r, p in cells:
        out += [f'EP_{r}_{p}_PCD', f'EP_{r}_{p}']
    return out


HEADER_WORDS = re.compile(r'Candidat|Pessoas|Sistema|SISTEMA|renda|Geral|defici|QUADRO|Campus/|CAMPUS/|'
                          r'Grupo|autodeclar|indígenas|quilombolas|per capita|salário|Total|TOTAL|'
                          r'Ofertadas|Cotas|Negr|Universal|^\s*capita|^\s*DE\s*$|^\s*VAGAS\s*$|ANEXO')
ROW_RE = re.compile(r'^(.*?)((?:\s*\d+){10,11})\s*$')


def _limpa_curso(name):
    name = re.sub(r'^\s*\d+\s+', '', name)  # número de página colado
    name = re.sub(r'^\s*(?:I{1,3}|IV|V)\s+', '', name)
    name = name.replace('*', ' ')
    return norm_key(name)


def _junta_numeros(lines):
    """Une linhas só de números quando a fileira do quadro foi quebrada (ex.: "7" + "5 15 5 ...")."""
    out = []
    for ln in lines:
        s = ' '.join(ln.split())
        if (out and re.fullmatch(r'(\d+\s*)+', s) and re.fullmatch(r'(\d+\s*){1,3}', out[-1])
                and len((out[-1] + ' ' + s).split()) in (10, 11)):
            out[-1] = out[-1] + ' ' + s
        else:
            out.append(s)
    return out


def parse_quadro(lines, ordem):
    lines = _junta_numeros(lines)
    rows = []
    campus = turno = ''
    buf = []
    for ln in lines:
        s = ' '.join(ln.split())
        if not s:
            continue
        if re.fullmatch(r'(Diurno|Noturno|Integral)', s, re.I):
            turno = s.upper()
            buf = []
            continue
        if re.match(r'Campus\b', s, re.I) and not re.search(r'\d', s):
            parts = re.split(r'\s*[–-]\s*(?=(?:Diurno|Noturno|Integral)\s*$)', s, flags=re.I)
            campus = norm_key(parts[0])
            turno = parts[1].upper() if len(parts) > 1 else ''
            buf = []
            continue
        if re.match(r'\s*TOTAL\b', s):
            buf = []
            continue
        m = ROW_RE.match(s)
        if m and len(m.group(2).split()) >= 10 and not (buf or m.group(1).strip()):
            # números do TOTAL quebrados na linha seguinte
            buf = []
            continue
        if m and len(m.group(2).split()) >= 10:
            nums = [int(x) for x in m.group(2).split()]
            name = ' '.join(buf + [m.group(1)])
            buf = []
            if re.match(r'\s*total\b', name, re.I):
                continue  # subtotais por campus ("Total Darcy - diurno") e total geral
            if len(nums) == 11:
                if nums[0] == sum(nums[1:]):
                    total, vals = nums[0], nums[1:]
                elif nums[-1] == sum(nums[:-1]):
                    total, vals = nums[-1], nums[:-1]
                else:
                    # um dígito do nome (ex.: "Turma 2") colado nos números
                    total, vals = nums[-1], nums[-11:-1]
            else:
                total, vals = sum(nums), nums
            labels = ['NEG'] + ordem + ['SU']
            rows.append({'campus': campus, 'turno': turno, 'curso': _limpa_curso(name),
                         'total': total, **dict(zip(labels, vals))})
            continue
        if HEADER_WORDS.search(s):
            buf = []
            continue
        buf.append(s)
    return rows


def extract(subprograma):
    path = os.path.join(RAW, subprograma, 'PAS3', 'Edital_de_abertura', 'edital_de_abertura.pdf')
    if not os.path.exists(path):
        return [], {'arquivo': None, 'linhas': 0}
    lines = [l for p in pdf_pages(path) for l in p.splitlines()]
    idx = [i for i, l in enumerate(lines) if re.search(r'QUADRO DE VAGAS\s*\d', l.upper())]
    out = []
    for n, i in enumerate(idx):
        sem = 1 if re.search(r'1\s*[ºo°]', lines[i]) else 2
        end = idx[n + 1] if n + 1 < len(idx) else len(lines)
        for j in range(i + 1, end):
            if re.match(r'\s*ANEXO\s+[IVX]+', lines[j]):
                end = j
                break
        seg = lines[i:end]
        # cabeçalho: do título até a primeira linha de curso
        first = next(k for k, l in enumerate(seg) if ROW_RE.match(' '.join(l.split()) or 'x'))
        ordem = ordem_ep(' '.join(seg[:first]))
        for r in parse_quadro(seg, ordem):
            r.update(subprograma=subprograma, semestre=sem)
            out.append(r)
    return out, {'arquivo': os.path.relpath(path, RAW), 'linhas': len(out)}


if __name__ == '__main__':
    import sys
    from common import SUBPROGRAMAS
    for sp in sys.argv[1:] or SUBPROGRAMAS:
        rows, st = extract(sp)
        tot = sum(r['total'] for r in rows)
        print(sp, st['arquivo'], 'linhas', len(rows), 'vagas', tot,
              'cursos', len({(r['campus'], r['turno'], r['curso']) for r in rows}))
        for r in rows:
            if 'COMPUTA' in r['curso'] or 'SOFTWARE' in r['curso']:
                print('    ', r['semestre'], r['campus'], r['turno'], r['curso'], r['total'], r['SU'], r['NEG'])
