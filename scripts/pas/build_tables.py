"""Gera as tabelas do plano do artigo a partir dos PDFs de raw_data/.

Saídas em parsed_data/:
  tabela1_alunos.csv      uma linha por candidato e subprograma
  tabela2_curso_cota.csv  uma linha por subprograma x curso x semestre x categoria
  subprogramas.csv        regras e datas de cada subprograma
  intermediarios/         convocações, relações e vagas extraídas, sem nomes

Uso:  python3 scripts/pas/build_tables.py
"""
import csv
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

import convocacoes
import cotas
import resultado_pas3
import resultado_pas12
import vagas
from common import INTERMEDIARIOS, PARSED, SUBPROGRAMAS, anon_id, norm_key

# Informações dos editais de abertura (ver raw_data/regulamentos.md)
SUBPROGRAMA_INFO = {
    '14-16': {'data_prova_pas3': '2016-11-27', 'sisunb': True},
    '15-17': {'data_prova_pas3': '2017-12-03', 'sisunb': True},
    '16-18': {'data_prova_pas3': '2018-12-09', 'sisunb': True},
    '17-19': {'data_prova_pas3': '2019-12-01', 'sisunb': False},
    '18-20': {'data_prova_pas3': '2021-03-07', 'sisunb': False},
    '19-21': {'data_prova_pas3': '2022-01-30', 'sisunb': False},
    '20-22': {'data_prova_pas3': '2022-12-11', 'sisunb': False},
    '21-23': {'data_prova_pas3': '2023-12-17', 'sisunb': False},
    '22-24': {'data_prova_pas3': '2024-12-01', 'sisunb': False},
    '23-25': {'data_prova_pas3': '2025-11-30', 'sisunb': False},
}
# A partir de 22-24 vale a Lei 14.723/2023 (renda de 1 SM, quilombolas e
# preenchimento do Universal antes das cotas), conforme os editais de abertura.
LEI_14723 = {'22-24', '23-25'}

# Os quatro cursos de computação do artigo. Engenharia de Software não tem
# entrada própria: está na entrada comum das Engenharias do campus Gama.
AREA_COMPUTACAO = [
    ('CC_BACHARELADO', r'^CIENCIA DA COMPUTACAO'),
    ('COMPUTACAO_LICENCIATURA', r'^COMPUTACAO \(LICENCIATURA'),
    ('ENG_COMPUTACAO', r'^ENGENHARIA DE COMPUTACAO'),
    ('ENGENHARIAS_FGA_SOFTWARE', r'SOFTWARE'),
]

RESTRICAO = {'R1': 0, 'R2': 1, 'PPI': 0, 'NPPI': 1}


def curso_area(curso):
    for nome, pat in AREA_COMPUTACAO:
        if re.search(pat, curso):
            return nome
    return ''


def limpa_curso(curso):
    curso = re.sub(r'\s*-?\s*(SUB\s*)?JUDICE\s*', '', norm_key(curso)).strip(' -')
    curso = re.sub(r'\s*\(\s*\)\s*', ' ', curso).strip()
    return curso


def campus_key(campus):
    """Chave estável de campus: o nome antes do parêntese (FGA virou FCTE em 2025)."""
    c = norm_key(campus)
    c = re.sub(r'^CAMPUS\s+(UNB\s+)?', '', c)
    c = c.split('(')[0].strip(' -')
    c = re.sub(r'\s*-\s*DARCY.*', '', c)
    return c


def course_key(campus, curso):
    return (campus_key(campus), limpa_curso(curso))


def sistema_inscricao(row):
    """Categoria em que o candidato se inscreveu: a mais restritiva em que tem classificação."""
    eps = [lab for lab in cotas.TODAS[2:] if row.get('class_' + lab) is not None]
    if eps:
        def rank(lab):
            _, r, p, *pcd = lab.split('_')
            return (RESTRICAO[r], RESTRICAO[p], 0 if pcd else 1)
        return min(eps, key=rank)
    if row.get('class_NEG') is not None:
        return 'NEG'
    if row.get('class_SU') is not None:
        return 'SU'
    return ''


def write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: ('' if r.get(k) is None else r.get(k)) for k in fields})


def build_subprograma(sp, log):
    pas3, meta, st3 = resultado_pas3.extract(sp)
    pas1, st1 = resultado_pas12.extract(sp, 1)
    pas2, st2 = resultado_pas12.extract(sp, 2)
    conv, stc = convocacoes.extract_convocacoes(sp)
    rel, str_ = convocacoes.extract_relacoes(sp)
    vag, stv = vagas.extract(sp)
    log[sp] = {'pas3': st3, 'pas1': st1, 'pas2': st2, 'convocacoes': stc,
               'relacoes': str_, 'vagas': stv, 'meta': meta}

    # 14-16 não tem editais de convocação: a "relação dos selecionados" faz esse papel
    if not conv:
        conv = [{'subprograma': sp, 'inscricao': r['inscricao'], 'campus': '', 'turno': '',
                 'curso': '', 'chamada': r['chamada'], 'semestre': r['semestre'], 'cota': None,
                 'classificacao_cota': None, 'sub_judice': r['sub_judice'], 'arquivo': r['arquivo']}
                for r in rel if r['tipo'] == 'selecionado']
    homologados = {r['inscricao'] for r in rel if r['tipo'] == 'homologado'}
    tem_homologacao = bool(homologados)

    conv_by = defaultdict(list)
    for c in conv:
        conv_by[c['inscricao']].append(c)

    p3 = {r['inscricao']: r for r in pas3}
    todos = set(p3) | set(pas1) | set(pas2)
    alunos = []
    for insc in sorted(todos):
        r3 = p3.get(insc)
        r1, r2 = pas1.get(insc), pas2.get(insc)
        row = {'subprograma': sp, 'id_aluno': anon_id(sp, insc)}
        row['compareceu_pas1'] = (r1 is not None) if pas1 else None
        row['compareceu_pas2'] = (r2 is not None) if pas2 else None
        row['compareceu_pas3'] = r3 is not None
        if r3:
            for k in resultado_pas3.NOTAS + ['argumento_final', 'campus', 'turno', 'curso', 'sub_judice']:
                row[k] = r3[k]
            for lab in cotas.TODAS:
                row['class_' + lab] = r3['class_' + lab]
            row['curso'] = limpa_curso(r3['curso'])
        else:
            for etapa, r in ((1, r1), (2, r2)):
                if r:
                    row[f'eb1_pas{etapa}'] = r['eb1']
                    row[f'eb2_pas{etapa}'] = r['eb2']
                    row[f'nr_pas{etapa}'] = r['nr']
            row['sub_judice'] = bool((r1 and r1['sub_judice']) or (r2 and r2['sub_judice']))
        row['area_computacao'] = curso_area(row.get('curso') or '')
        row['sistema_inscricao'] = sistema_inscricao(row) if r3 else ''
        row['grupo_concorrencia'] = cotas.GRUPO.get(row['sistema_inscricao'], '')
        cs = sorted(conv_by.get(insc, []), key=lambda c: ((c['chamada'] or 99), c['semestre'] or 9))
        row['aprovado'] = bool(cs)
        if cs:
            first = cs[0]
            row['chamada_aprovacao'] = first['chamada']
            row['semestre_aprovacao'] = first['semestre']
            row['cota_aprovacao'] = first['cota']
            row['curso_aprovacao'] = limpa_curso(first['curso']) if first['curso'] else row.get('curso', '')
            row['n_convocacoes'] = len(cs)
        row['homologado'] = (insc in homologados) if tem_homologacao else None
        row['faixa_renda_regra'] = meta['faixa_renda'] if not sp in LEI_14723 else '1 SM'
        alunos.append(row)

    # tabela 2
    af = {r['inscricao']: r['argumento_final'] for r in pas3}
    insc_curso = {r['inscricao']: course_key(r['campus'], r['curso']) for r in pas3}
    inscritos = defaultdict(int)
    for r in pas3:
        k = course_key(r['campus'], r['curso'])
        for lab in cotas.TODAS:
            if r['class_' + lab] is not None:
                inscritos[(k, lab)] += 1
    conv_cell = defaultdict(list)
    for c in conv:
        k = course_key(c['campus'], c['curso']) if c['curso'] else insc_curso.get(c['inscricao'])
        if k is None:
            continue
        conv_cell[(k, c['semestre'], c['cota'] or 'DESCONHECIDA')].append(c)
    cells = {}
    for v in vag:
        k = course_key(v['campus'], v['curso'])
        for lab in cotas.TODAS:
            cells[(k, v['semestre'], lab)] = {'vagas': v[lab], 'campus': v['campus'], 'turno': v['turno']}
    for (k, sem, lab) in conv_cell:
        cells.setdefault((k, sem, lab), {'vagas': None, 'campus': '', 'turno': ''})
    linhas = []
    for (k, sem, lab), info in sorted(cells.items(), key=lambda x: (x[0][0], x[0][1] or 0, x[0][2])):
        cs = conv_cell.get((k, sem, lab), [])
        notas1 = [af[c['inscricao']] for c in cs if c['chamada'] == 1 and af.get(c['inscricao']) is not None]
        notas = [af[c['inscricao']] for c in cs if af.get(c['inscricao']) is not None]
        linhas.append({
            'chave': f'{sp}|{k[0]}|{k[1]}|{sem}|{lab}',
            'subprograma': sp, 'campus': k[0], 'curso': k[1], 'semestre': sem,
            'categoria': lab, 'grupo_concorrencia': cotas.GRUPO.get(lab, ''),
            'area_computacao': curso_area(k[1]),
            'vagas': info['vagas'],
            'inscritos': inscritos.get((k, lab), 0) if lab != 'DESCONHECIDA' else None,
            'convocados': len(cs),
            'convocados_1a_chamada': sum(c['chamada'] == 1 for c in cs),
            'ultima_chamada': max((c['chamada'] or 0 for c in cs), default=None) or None,
            'nota_corte_1a_chamada': min(notas1) if notas1 else None,
            'nota_corte_ultima_chamada': min(notas) if notas else None,
        })
    conv_out = [{**{k: c[k] for k in ('subprograma', 'campus', 'turno', 'curso', 'chamada',
                                      'semestre', 'cota', 'classificacao_cota', 'sub_judice', 'arquivo')},
                 'id_aluno': anon_id(sp, c['inscricao'])} for c in conv]
    rel_out = [{**{k: r[k] for k in ('subprograma', 'chamada', 'semestre', 'tipo', 'sub_judice', 'arquivo')},
                'id_aluno': anon_id(sp, r['inscricao'])} for r in rel]
    info = dict(SUBPROGRAMA_INFO[sp])
    info.update(subprograma=sp, faixa_renda=('1 SM' if sp in LEI_14723 else meta['faixa_renda']),
                quilombola_no_nivel_ppi=sp in LEI_14723,
                lei_14723=sp in LEI_14723,
                categorias_resultado=' '.join(meta['cotas']),
                candidatos_pas1=len(pas1) or None, candidatos_pas2=len(pas2) or None,
                candidatos_pas3=len(pas3), convocados=len({c['inscricao'] for c in conv}),
                vagas=sum(v['total'] for v in vag) or None,
                tem_homologacao=tem_homologacao)
    return alunos, linhas, conv_out, rel_out, vag, info


TAB1 = (['subprograma', 'id_aluno', 'campus', 'turno', 'curso', 'area_computacao',
         'compareceu_pas1', 'compareceu_pas2', 'compareceu_pas3']
        + resultado_pas3.NOTAS + ['argumento_final']
        + ['class_' + l for l in cotas.TODAS]
        + ['sistema_inscricao', 'grupo_concorrencia', 'aprovado', 'cota_aprovacao',
           'chamada_aprovacao', 'semestre_aprovacao', 'curso_aprovacao', 'n_convocacoes',
           'homologado', 'sub_judice', 'faixa_renda_regra'])
TAB2 = ['chave', 'subprograma', 'campus', 'curso', 'semestre', 'categoria', 'grupo_concorrencia',
        'area_computacao', 'vagas', 'inscritos', 'convocados', 'convocados_1a_chamada',
        'ultima_chamada', 'nota_corte_1a_chamada', 'nota_corte_ultima_chamada']
SUBP = ['subprograma', 'data_prova_pas3', 'sisunb', 'lei_14723', 'faixa_renda',
        'quilombola_no_nivel_ppi', 'categorias_resultado', 'candidatos_pas1', 'candidatos_pas2',
        'candidatos_pas3', 'convocados', 'vagas', 'tem_homologacao']


def main(subprogramas=SUBPROGRAMAS):
    log = {}
    t1, t2, cv, rl, vg, sb = [], [], [], [], [], []
    for sp in subprogramas:
        a, l, c, r, v, i = build_subprograma(sp, log)
        t1 += a; t2 += l; cv += c; rl += r; vg += v; sb.append(i)
        print(f'{sp}: {len(a)} candidatos, {i["candidatos_pas3"]} no PAS 3, '
              f'{i["convocados"]} convocados, {len(l)} linhas na tabela 2')
    write_csv(os.path.join(PARSED, 'tabela1_alunos.csv'), t1, TAB1)
    write_csv(os.path.join(PARSED, 'tabela2_curso_cota.csv'), t2, TAB2)
    write_csv(os.path.join(PARSED, 'subprogramas.csv'), sb, SUBP)
    write_csv(os.path.join(INTERMEDIARIOS, 'convocacoes.csv'), cv,
              ['subprograma', 'id_aluno', 'campus', 'turno', 'curso', 'chamada', 'semestre',
               'cota', 'classificacao_cota', 'sub_judice', 'arquivo'])
    write_csv(os.path.join(INTERMEDIARIOS, 'relacoes_selecionados.csv'), rl,
              ['subprograma', 'id_aluno', 'chamada', 'semestre', 'tipo', 'sub_judice', 'arquivo'])
    write_csv(os.path.join(INTERMEDIARIOS, 'vagas.csv'), vg,
              ['subprograma', 'semestre', 'campus', 'turno', 'curso', 'total'] + cotas.TODAS)
    return log


if __name__ == '__main__':
    main(sys.argv[1:] or SUBPROGRAMAS)
