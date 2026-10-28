"""Confere a extração e grava o relatório em parsed_data/validacao.md.

Verificações:
  1. Registros extraídos x inscrições encontradas no texto de cada PDF.
  2. Notas da etapa 1 e 2 no resultado do PAS 3 iguais às dos resultados do PAS 1 e PAS 2.
  3. Médias e desvios da Parte II e da redação comparados com os publicados pelo Cebraspe.
  4. Argumento final em ordem decrescente da classificação no Sistema Universal, por curso.
  5. Todo convocado existe no resultado final do PAS 3.
  6. Faixas de valores (notas de redação entre 0 e 10, por exemplo).

Uso:  python3 scripts/pas/validate.py   (depois de build_tables.py)
"""
import csv
import os
import re
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

import convocacoes
import resultado_pas3
import resultado_pas12
from common import PARSED, RAW, SUBPROGRAMAS, flat, pdf_pages

OFICIAIS = {
    '15-17': 'raw_data/15-17/media_e_desvio_padrao.pdf',
    '16-18': 'raw_data/16-18/media_e_desvio_padrao.pdf',
    '17-19': 'raw_data/17-19/media_e_desvio_padrao.pdf',
    '18-20': 'raw_data/18-20/PAS3/media_e_desvio_padrao.pdf',
    '21-23': 'raw_data/21-23/PAS3/Resultado_final/resultado_final.pdf',
    '22-24': 'raw_data/22-24/PAS3/Resultado_final/resultado_final.pdf',
    '23-25': 'raw_data/23-25/PAS3/Resultado_final/resultado_final.pdf',
}


def oficiais(sp):
    path = OFICIAIS.get(sp)
    if not path:
        return {}
    text = flat(' '.join(pdf_pages(os.path.join(os.path.dirname(RAW), path))))
    out = {}
    for etapa, nome in ((1, 'PRIMEIRA'), (2, 'SEGUNDA'), (3, 'TERCEIRA')):
        m = re.search(nome + r' ETAPA\s+M[ée]dia\s+Desvio-padr[ãa]o(.*?)(?:ETAPA|$)', text)
        if not m:
            continue
        bloco = m.group(1)
        p2 = re.search(r'Parte II\s+(-?\d+\.\d+)\s+(\d+\.\d+)', bloco)
        nr = re.search(r'reda[çc][ãa]o[^\d-]*(-?\d+\.\d+)\s+(\d+\.\d+)', bloco)
        if p2:
            out[(etapa, 'eb2')] = (float(p2.group(1)), float(p2.group(2)))
        if nr:
            out[(etapa, 'nr')] = (float(nr.group(1)), float(nr.group(2)))
    return out


def main():
    lines = ['# Relatório de validação da extração', '',
             'Gerado por `scripts/pas/validate.py`. Os números abaixo são recalculados a partir dos PDFs.', '']
    resumo = []

    # 1. contagens
    lines += ['## 1. Registros extraídos por arquivo', '',
              '| Subprograma | Arquivo | Inscrições no texto | Extraídos | Problemas |', '|---|---|---|---|---|']
    for sp in SUBPROGRAMAS:
        rows, meta, stats = resultado_pas3.extract(sp)
        for s in stats:
            if s['arquivo'].endswith('resultado_final.pdf'):
                lines.append(f"| {sp} | {s['arquivo']} | {s['esperados']} | {s['extraidos']} | {len(s['problemas'])} |")
                resumo.append(s['extraidos'] / max(s['esperados'], 1))
        for etapa in (1, 2):
            _, st = resultado_pas12.extract(sp, etapa)
            for s in st:
                if not s['retificacao']:
                    lines.append(f"| {sp} | {s['arquivo']} | {s['esperados']} | {s['extraidos']} | {len(s['problemas'])} |")
    lines += ['', f'Cobertura mínima nos resultados finais do PAS 3: **{min(resumo):.2%}**.', '']

    t1 = list(csv.DictReader(open(os.path.join(PARSED, 'tabela1_alunos.csv'), encoding='utf-8')))
    by_sp = defaultdict(list)
    for r in t1:
        by_sp[r['subprograma']].append(r)

    # 2. consistência entre etapas
    lines += ['## 2. Notas das etapas 1 e 2: resultado do PAS 3 x resultados do PAS 1 e PAS 2', '',
              'Compara EB parte 2 e redação das etapas anteriores repetidos no resultado do PAS 3.', '',
              '| Subprograma | Etapa | Comparados | Iguais (dif. < 0,001) |', '|---|---|---|---|']
    for sp in SUBPROGRAMAS:
        pas3 = {r['inscricao']: r for r in resultado_pas3.extract(sp)[0]}
        for etapa in (1, 2):
            res, _ = resultado_pas12.extract(sp, etapa)
            if not res:
                continue
            n = ok = 0
            for insc, r in res.items():
                p = pas3.get(insc)
                if not p or r['nr'] is None:
                    continue
                n += 1
                same = abs((p[f'nr_pas{etapa}'] or 0) - r['nr']) < 1e-3
                if r['eb2'] is not None:
                    same = same and abs((p[f'eb2_pas{etapa}'] or 0) - r['eb2']) < 1e-3
                ok += same
            lines.append(f'| {sp} | {etapa} | {n} | {ok} ({ok / max(n, 1):.1%}) |')
    lines += ['']

    # 3. médias oficiais
    lines += ['## 3. Médias e desvios: calculados x publicados', '',
              'Calculados sobre todos os candidatos de cada etapa (PAS 1 e PAS 2) ou sobre os não eliminados '
              '(PAS 3). A Parte I não entra porque a média oficial é por língua estrangeira e os PDFs não '
              'informam a língua de cada candidato.', '',
              '| Subprograma | Etapa | Prova | Média calc. | Média oficial | DP calc. | DP oficial |',
              '|---|---|---|---|---|---|---|']
    for sp in SUBPROGRAMAS:
        of = oficiais(sp)
        if not of:
            continue
        pas3 = resultado_pas3.extract(sp)[0]
        for (etapa, prova), (mo, do) in sorted(of.items()):
            if etapa == 3:
                vals = [r[f'{prova}_pas3'] for r in pas3 if r[f'{prova}_pas3'] is not None]
            else:
                res, _ = resultado_pas12.extract(sp, etapa)
                vals = [r[prova] for r in res.values() if r[prova] is not None]
            if len(vals) < 2:
                continue
            m, d = statistics.mean(vals), statistics.pstdev(vals)
            lines.append(f'| {sp} | {etapa} | {prova.upper()} | {m:.3f} | {mo:.3f} | {d:.3f} | {do:.3f} |')
    lines += ['']

    # 4. ordem do argumento final
    lines += ['## 4. Argumento final x classificação no Sistema Universal', '',
              'Dentro de cada curso, a classificação no Universal deve seguir o argumento final em ordem '
              'decrescente. Conta os pares de candidatos fora de ordem.', '',
              '| Subprograma | Cursos | Pares fora de ordem |', '|---|---|---|']
    for sp in SUBPROGRAMAS:
        grupos = defaultdict(list)
        for r in by_sp[sp]:
            if r['class_SU'] and r['argumento_final'] and r['sub_judice'] == 'False':
                grupos[(r['campus'], r['turno'], r['curso'])].append((int(r['class_SU']), float(r['argumento_final'])))
        bad = 0
        for g in grupos.values():
            g.sort()
            bad += sum(1 for a, b in zip(g, g[1:]) if b[1] > a[1] + 1e-6)
        lines.append(f'| {sp} | {len(grupos)} | {bad} |')
    lines += ['']

    # 5. convocados órfãos
    lines += ['## 5. Convocados encontrados no resultado final', '',
              '| Subprograma | Convocações | Sem correspondência no PAS 3 |', '|---|---|---|']
    for sp in SUBPROGRAMAS:
        insc3 = {r['inscricao'] for r in resultado_pas3.extract(sp)[0]}
        conv, _ = convocacoes.extract_convocacoes(sp)
        if not conv:
            conv = [r for r in convocacoes.extract_relacoes(sp)[0] if r['tipo'] == 'selecionado']
        orf = [c for c in conv if c['inscricao'] not in insc3]
        lines.append(f'| {sp} | {len(conv)} | {len(orf)} |')
    lines += ['']

    # 6. faixas
    lines += ['## 6. Faixas de valores', '']
    fora = defaultdict(int)
    for r in t1:
        for e in (1, 2, 3):
            v = r[f'nr_pas{e}']
            if v and not 0 <= float(v) <= 10:
                fora[f'nr_pas{e}'] += 1
        if r['argumento_final'] and not -400 < float(r['argumento_final']) < 400:
            fora['argumento_final'] += 1
    lines.append('Valores fora da faixa esperada: ' + (', '.join(f'{k}: {v}' for k, v in fora.items()) or 'nenhum') + '.')
    lines.append('')

    path = os.path.join(PARSED, 'validacao.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
