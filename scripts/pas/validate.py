"""Validação das tabelas finais do artigo (parsed_data/*_sem_eng_soft.csv).

Cada teste confronta fontes diferentes, para não validar um dado com ele mesmo:

  V1  Cobertura: registros extraídos x inscrições presentes no texto do PDF
  V2  Reextração independente com outra biblioteca (pdftotext/poppler), campo a campo
  V3  Notas das etapas 1 e 2 repetidas no resultado do PAS 3 x PDFs do PAS 1 e PAS 2
  V4  Médias e desvios calculados x publicados pelo Cebraspe
  V5  Classificação em cada categoria x argumento final (ordem decrescente)
  V6  Elegibilidade: todo convocado numa cota tem classificação nessa cota
  V7  Ninguém pulado: candidato com classificação melhor que o último convocado foi convocado
  V8  Nota de corte da tabela 2 = AF do convocado com a pior classificação na célula
  V9  Regime da cascata (antes e depois da Lei 14.723/2023)
  V10 Quadro de vagas: total geral do edital, linha de Ciência da Computação e regras da Lei 12.711
  V11 Convocados na 1ª chamada x vagas do curso
  V12 Homologados contidos nos convocados; duplicatas; mudanças de curso no SISUnB

Relatório: parsed_data/validacao.md.  Uso: python3 scripts/pas/validate.py
"""
import csv
import os
import random
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))

import convocacoes
import cotas
import resultado_pas12
import resultado_pas3
import vagas
from common import PARSED, RAW, ROOT, SUBPROGRAMAS, anon_id, flat, pdf_pages

SUBS = [s for s in SUBPROGRAMAS if s != '14-16']  # escopo do artigo
T1 = os.path.join(PARSED, 'tabela1_alunos_sem_eng_soft.csv')
T2 = os.path.join(PARSED, 'tabela2_curso_cota_sem_eng_soft.csv')
CONV = os.path.join(PARSED, 'intermediarios', 'convocacoes.csv')
REL = os.path.join(PARSED, 'intermediarios', 'relacoes_selecionados.csv')
LEI_14723 = {'22-24', '23-25'}
SISUNB = {'15-17', '16-18'}
CATS = cotas.TODAS

OFICIAIS = {
    '15-17': 'raw_data/15-17/media_e_desvio_padrao.pdf',
    '16-18': 'raw_data/16-18/media_e_desvio_padrao.pdf',
    '17-19': 'raw_data/17-19/media_e_desvio_padrao.pdf',
    '18-20': 'raw_data/18-20/PAS3/media_e_desvio_padrao.pdf',
    '21-23': 'raw_data/21-23/PAS3/Resultado_final/resultado_final.pdf',
    '22-24': 'raw_data/22-24/PAS3/Resultado_final/resultado_final.pdf',
    '23-25': 'raw_data/23-25/PAS3/Resultado_final/resultado_final.pdf',
}
TOTAL_GERAL_RE = re.compile(r'TOTAL GERAL\s+([\d.]+(?:\s+[\d.]+){10})', re.I)


def fnum(x):
    return float(x) if x not in ('', None) else None


def inum(x):
    return int(x) if x not in ('', None) else None


def load_csv(path):
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))


class Report:
    def __init__(self):
        self.lines = []
        self.resumo = []

    def h(self, t):
        self.lines += ['', t, '']

    def p(self, t=''):
        self.lines.append(t)

    def table(self, header, rows):
        self.lines.append('| ' + ' | '.join(header) + ' |')
        self.lines.append('|' + '---|' * len(header))
        for r in rows:
            self.lines.append('| ' + ' | '.join(str(x) for x in r) + ' |')

    def check(self, nome, resultado, criterio, ok):
        self.resumo.append((nome, resultado, criterio, 'OK' if ok else 'ATENÇÃO'))


# ---------------------------------------------------------------- V2
def pdftotext_records(path):
    """Registros do resultado final lidos com o poppler (biblioteca independente do pypdf)."""
    out = subprocess.run(['pdftotext', '-enc', 'UTF-8', path, '-'], capture_output=True,
                         text=True, check=True).stdout
    text = ' '.join(out.replace('‐', '-').replace('–', '-').split())
    recs = {}
    for m in re.finditer(r'(?<![\d.])(\d{4}\s?\d{4})\s*,([^/]*)', text):
        fields = [f.strip() for f in m.group(2).split(',')]
        nums = []
        for f in fields[1:]:
            mm = re.match(r'^(-?\s*\d[\d\s]*(?:\.\s*\d[\d\s]*)?|-)', f)
            if not mm:
                break
            nums.append(mm.group(1).replace(' ', ''))
        if len(nums) >= 11:  # registros do resultado final (os do tipo D têm 2 números)
            recs[m.group(1).replace(' ', '')] = nums
    return recs


def _quebra_de_pagina(pages, inscricao, b):
    """O registro termina no pé de uma página cujo número impresso é `b`?"""
    for i, p in enumerate(pages[:-1]):
        if inscricao in p.replace(' ', ''):
            numeros = {p.strip().split('\n')[0].strip(), pages[i + 1].strip().split('\n')[0].strip()}
            if b in numeros:
                return True
    return False


def _tipo_divergencia(a, b, pages=None, inscricao=None):
    """Classifica uma divergência pypdf x poppler."""
    if a is None and b.isdigit() and pages and _quebra_de_pagina(pages, inscricao, b):
        return 'pagina'         # poppler insere o número da página seguinte entre os campos
    if b == '-' or a is None:
        return 'outra'
    bf = float(b)
    if abs(abs(a) - abs(bf)) < 1e-6 and a < 0 < bf:
        return 'sinal'          # poppler perde o "-" que ficou sozinho no fim da linha
    if b.endswith(f'{abs(a):.3f}') and len(b) > len(f'{abs(a):.3f}'):
        return 'pagina'         # poppler cola o número da página no valor
    return 'outra'


def v2(rep, pas3_by_sp):
    rep.h('## V2. Reextração independente (pdftotext/poppler × pypdf)')
    rep.p('Amostra aleatória (semente fixa 42) de até 300 candidatos por subprograma. Para cada um, '
          'o registro é lido de novo do PDF com o `pdftotext` (poppler), com um analisador mínimo e '
          'independente do pipeline, e comparado campo a campo com a tabela: 9 notas, argumento '
          'final e todas as classificações.')
    rep.p()
    rep.p('As divergências são classificadas. **Sinal**: o poppler descarta o "-" que o PDF '
          'coloca sozinho no fim da linha (ex.: AF -55,760 lido como 55,760). O valor do pypdf é o '
          'correto, porque só ele é compatível com a classificação publicada (V5 tem 0 pares fora de '
          'ordem com os valores do pypdf). **Página**: o poppler cola o número da página no valor '
          '(ex.: 5,034 lido como 1155,034) ou insere esse número entre os campos quando o registro '
          'termina no pé da página (conferido no próprio PDF: é o número impresso naquela página). **Outra**: divergência sem explicação, que conta como erro.')
    rows, tot, eq, outras_tot = [], 0, 0, 0
    rng = random.Random(42)
    exemplos = []
    for sp in SUBS:
        path = os.path.join(RAW, sp, 'PAS3', 'Resultado_final', 'resultado_final.pdf')
        ref = pdftotext_records(path)
        pages = pdf_pages(path)
        pas3 = [r for r in pas3_by_sp[sp] if not r['sub_judice']]
        amostra = rng.sample(pas3, min(300, len(pas3)))
        n_campos = ok = achados = 0
        tipos = Counter()
        for r in amostra:
            nums = ref.get(r['inscricao'])
            if not nums:
                continue
            achados += 1
            mine = [r[k] for k in resultado_pas3.NOTAS] + [r['argumento_final']]
            mine += [r['class_' + c] for c in pas3_meta[sp]]
            for a, b in zip(mine, nums[:len(mine)]):
                n_campos += 1
                bb = None if b == '-' else float(b)
                if (a is None and bb is None) or (a is not None and bb is not None and abs(a - bb) < 1e-6):
                    ok += 1
                else:
                    t = _tipo_divergencia(a, b, pages, r['inscricao'])
                    tipos[t] += 1
                    if t == 'outra' and len(exemplos) < 10:
                        exemplos.append(f'{sp} {anon_id(sp, r["inscricao"])}: pypdf={a} poppler={b}')
        tot += n_campos
        eq += ok
        outras_tot += tipos['outra']
        rows.append([sp, len(amostra), achados, n_campos, f'{ok / max(n_campos, 1):.3%}',
                     tipos['sinal'], tipos['pagina'], tipos['outra']])
    rep.table(['Subprograma', 'Amostra', 'Achados no poppler', 'Campos comparados',
               'Idênticos', 'Div. sinal', 'Div. página', 'Div. sem explicação'], rows)
    if exemplos:
        rep.p()
        rep.p('Divergências sem explicação: ' + '; '.join(exemplos))
    taxa = (eq + (tot - eq - outras_tot)) / max(tot, 1)
    rep.check('V2 reextração independente',
              f'{eq / max(tot, 1):.3%} idênticos; {outras_tot} divergências sem explicação em {tot} campos',
              '≥ 99,9% idênticos ou explicados', taxa >= 0.999)


def main():
    rep = Report()
    t1 = [r for r in load_csv(T1) if r['subprograma'] in SUBS]
    t2 = [r for r in load_csv(T2) if r['subprograma'] in SUBS]
    conv = [r for r in load_csv(CONV) if r['subprograma'] in SUBS]
    rel = [r for r in load_csv(REL) if r['subprograma'] in SUBS]
    alunos = {(r['subprograma'], r['id_aluno']): r for r in t1}

    global pas3_meta
    pas3_meta = {}
    pas3_by_sp, stats_by_sp = {}, {}
    for sp in SUBS:
        rows, meta, st = resultado_pas3.extract(sp)
        pas3_by_sp[sp], stats_by_sp[sp] = rows, st
        pas3_meta[sp] = meta['cotas']

    rep.p('# Relatório de validação dos dados')
    rep.p()
    rep.p('Gerado por `scripts/pas/validate.py` sobre as tabelas finais do artigo '
          '(`tabela1_alunos_sem_eng_soft.csv` e `tabela2_curso_cota_sem_eng_soft.csv`; subprogramas '
          '15-17 a 23-25). Cada teste compara fontes diferentes; os critérios de aceitação estão '
          'declarados no resumo. Candidatos são identificados só pelo `id_aluno` anonimizado.')
    rep.p('')
    rep.p('<!-- RESUMO -->')

    # ------------------------------------------------------------ V1
    rep.h('## V1. Cobertura da extração')
    rep.p('Registros extraídos do resultado final do PAS 3 × inscrições de 8 dígitos seguidas de '
          'vírgula no texto da seção de resultados (contagem bruta, sem interpretar o registro).')
    rows, minimo = [], 1
    for sp in SUBS:
        for s in stats_by_sp[sp]:
            if s['arquivo'].endswith('resultado_final.pdf'):
                cov = s['extraidos'] / max(s['esperados'], 1)
                minimo = min(minimo, cov)
                rows.append([sp, s['esperados'], s['extraidos'], len(s['problemas']), f'{cov:.2%}'])
    rep.table(['Subprograma', 'Inscrições no texto', 'Extraídos', 'Não interpretados', 'Cobertura'], rows)
    rep.check('V1 cobertura do resultado final', f'mínimo {minimo:.2%}', '100%', minimo >= 0.9999)

    # ------------------------------------------------------------ V2
    v2(rep, pas3_by_sp)

    # ------------------------------------------------------------ V3
    rep.h('## V3. Consistência entre editais de etapas diferentes')
    rep.p('As notas das etapas 1 e 2 aparecem de novo no resultado do PAS 3. Elas são comparadas com '
          'os resultados finais do PAS 1 e do PAS 2 (outros editais, publicados um e dois anos antes). '
          'Diferenças residuais vêm de retificações publicadas depois.')
    rows, worst = [], 1
    for sp in SUBS:
        p3 = {r['inscricao']: r for r in pas3_by_sp[sp]}
        for etapa in (1, 2):
            res, _ = resultado_pas12.extract(sp, etapa)
            if not res:
                continue
            n = ok = 0
            for insc, r in res.items():
                p = p3.get(insc)
                if not p or r['nr'] is None:
                    continue
                n += 1
                same = abs((p[f'nr_pas{etapa}'] or 0) - r['nr']) < 1e-3
                if r['eb2'] is not None:
                    same = same and abs((p[f'eb2_pas{etapa}'] or 0) - r['eb2']) < 1e-3
                    same = same and abs((p[f'eb1_pas{etapa}'] or 0) - r['eb1']) < 1e-3
                ok += same
            worst = min(worst, ok / max(n, 1))
            rows.append([sp, etapa, n, ok, f'{ok / max(n, 1):.2%}'])
    rep.table(['Subprograma', 'Etapa', 'Comparados', 'Idênticos', '%'], rows)
    rep.check('V3 notas iguais entre editais', f'mínimo {worst:.2%}', '≥ 99%', worst >= 0.99)

    # ------------------------------------------------------------ V4
    rep.h('## V4. Médias e desvios × números oficiais do Cebraspe')
    rep.p('Média e desvio padrão (populacional) da Parte II e da redação do PAS 3, calculados a partir '
          'da tabela, comparados com os publicados pelo Cebraspe (edital de média e desvio ou fim do '
          'resultado final). A Parte I não entra porque a média oficial é por língua estrangeira, que '
          'não é publicada por candidato. As etapas 1 e 2 não entram porque os PDFs dessas etapas '
          'incluem ausentes com nota zero, excluídos do cálculo oficial.')
    rows, maxdif = [], 0
    for sp in SUBS:
        path = OFICIAIS.get(sp)
        if not path:
            continue
        text = flat(' '.join(pdf_pages(os.path.join(ROOT, path))))
        m = re.search(r'TERCEIRA ETAPA\s+M[ée]dia\s+Desvio-padr[ãa]o(.*?)(?:ETAPA|[A-Z]{5,} [A-Z]{5,}|$)', text)
        if not m:
            continue
        bloco = m.group(1)
        of = {}
        p2 = re.search(r'Parte II\s+(-?\d+\.\d+)\s+(\d+\.\d+)', bloco)
        nr = re.search(r'reda[çc][ãa]o[^\d-]*(-?\d+\.\d+)\s+(\d+\.\d+)', bloco)
        if p2:
            of['eb2'] = (float(p2.group(1)), float(p2.group(2)))
        if nr:
            of['nr'] = (float(nr.group(1)), float(nr.group(2)))
        for prova, (mo, do) in of.items():
            vals = [r[f'{prova}_pas3'] for r in pas3_by_sp[sp] if r[f'{prova}_pas3'] is not None]
            mc, dc = statistics.mean(vals), statistics.pstdev(vals)
            maxdif = max(maxdif, abs(mc - mo), abs(dc - do))
            rows.append([sp, 'Parte II' if prova == 'eb2' else 'Redação', len(vals),
                         f'{mc:.3f}', f'{mo:.3f}', f'{dc:.3f}', f'{do:.3f}'])
    rep.table(['Subprograma', 'Prova', 'n', 'Média calc.', 'Média oficial', 'DP calc.', 'DP oficial'], rows)
    rep.check('V4 médias e desvios oficiais (PAS 3)', f'maior diferença {maxdif:.3f}', '≤ 0,005',
              maxdif <= 0.005)

    # ------------------------------------------------------------ V5
    rep.h('## V5. Classificação × argumento final')
    rep.p('Dentro de cada curso e categoria, a classificação publicada deve seguir o argumento final em '
          'ordem decrescente. Antes da correção do cabeçalho de curso (ver `metodologia.md`, seção 4) '
          'havia 136, 82, 62, 212, 18, 38, 32, 36, 28 e 0 pares fora de ordem no Universal (14-16 a 23-25). '
          'Empates exatos de AF são listados à parte: o desempate segue o Edital nº 1 de cada subprograma.')
    rows, total_bad, total_dup = [], 0, 0
    for sp in SUBS:
        bad = ties = dup = pares = 0
        grupos = defaultdict(list)
        for r in t1:
            if r['subprograma'] != sp or r['compareceu_pas3'] != 'True' or r['sub_judice'] == 'True':
                continue
            for c in CATS:
                v = inum(r['class_' + c])
                if v is not None:
                    grupos[(r['campus'], r['turno'], r['curso'], c)].append((v, float(r['argumento_final'])))
        for g in grupos.values():
            g.sort()
            dup += len(g) - len({x[0] for x in g})
            for a, b in zip(g, g[1:]):
                pares += 1
                if b[1] > a[1] + 1e-6:
                    bad += 1
                elif abs(b[1] - a[1]) < 1e-6:
                    ties += 1
        total_bad += bad
        total_dup += dup
        rows.append([sp, len(grupos), pares, bad, dup, ties])
    rep.table(['Subprograma', 'Grupos curso×categoria', 'Pares comparados', 'Fora de ordem',
               'Classificação repetida', 'Empates de AF'], rows)
    rep.check('V5 ordem classificação × AF', f'{total_bad} pares fora de ordem, {total_dup} repetidas',
              '0', total_bad == 0 and total_dup == 0)

    # ------------------------------------------------------------ V6
    rep.h('## V6. Elegibilidade da aprovação (convocação × resultado)')
    rep.p('A categoria de cada convocação vem da legenda (1)–(10) do edital de convocação; a classificação '
          'por categoria vem do resultado final. Todo convocado numa categoria precisa ter classificação '
          'nela (ou seja, concorria naquela vaga).')
    rows, tot_v, tot_n = [], 0, 0
    for sp in SUBS:
        n = viol = semcota = ausente = sj = 0
        for c in conv:
            if c['subprograma'] != sp:
                continue
            a = alunos.get((sp, c['id_aluno']))
            if not c['cota']:
                semcota += 1
                continue
            if a is None or a['compareceu_pas3'] != 'True':
                ausente += 1  # não está em nenhum resultado do PAS 3 do repositório
                continue
            n += 1
            if a['class_' + c['cota']] == '':
                if c['sub_judice'] == 'True' or a['sub_judice'] == 'True':
                    sj += 1
                else:
                    viol += 1
        tot_v += viol
        tot_n += n
        rows.append([sp, n, viol, sj, ausente, semcota])
    rep.table(['Subprograma', 'Convocações verificáveis', 'Sem classificação na categoria',
               'Idem, sub judice', 'Convocado fora do resultado do PAS 3', 'Convocação SJ sem categoria'], rows)
    rep.p()
    rep.p('"Convocado fora do resultado do PAS 3": a inscrição não aparece em nenhum resultado final do '
          'repositório, nem pelo nome. São candidatos incluídos depois por editais de retificação ou '
          'sub judice que não estão no repositório. Eles não têm argumento final e por isso não entram '
          'nas notas de corte. "Idem, sub judice": a convocação ou o candidato é sub judice (decisão '
          'judicial que garante a vaga independentemente da classificação).')
    rep.check('V6 elegibilidade da cota de aprovação', f'{tot_v} violações em {tot_n} convocações',
              '≤ 0,05% (sem explicação)', tot_v <= 0.0005 * tot_n)

    # índices para V7–V9
    conv_by_aluno = defaultdict(list)
    for c in conv:
        conv_by_aluno[(c['subprograma'], c['id_aluno'])].append(c)

    # ------------------------------------------------------------ V7
    rep.h('## V7. Ninguém pulado na ordem de classificação')
    rep.p('Para cada curso e categoria, encontra a pior classificação entre os convocados naquela '
          'categoria e conta os candidatos do mesmo curso com classificação melhor na categoria que '
          'nunca foram convocados. Pelas regras do edital esse número deve ser zero, exceto quando o '
          'candidato perde a vaga reservada na validação da autodeclaração (heteroidentificação, a '
          'partir de 21-23) ou na avaliação biopsicossocial. Em 15-17 e 16-18 (SISUnB) a classificação '
          'publicada é da pré-opção de curso, então o teste é feito só para quem não mudou de curso.')
    rows, tot_skip, tot_cand = [], 0, 0
    for sp in SUBS:
        worst = defaultdict(int)
        for a in t1:
            if a['subprograma'] != sp:
                continue
            for c in conv_by_aluno.get((sp, a['id_aluno']), []):
                if c['cota'] and a['class_' + c['cota']] and a.get('curso_mudou_sisunb') != 'True':
                    k = (a['campus'], a['turno'], a['curso'], c['cota'])
                    worst[k] = max(worst[k], int(a['class_' + c['cota']]))
        skip = cand = 0
        for a in t1:
            if a['subprograma'] != sp or a['compareceu_pas3'] != 'True' or a['aprovado'] == 'True':
                continue
            for cat in CATS:
                v = inum(a['class_' + cat])
                w = worst.get((a['campus'], a['turno'], a['curso'], cat))
                if v is not None and w:
                    cand += 1
                    if v < w:
                        skip += 1
                        break
        tot_skip += skip
        tot_cand += cand
        rows.append([sp, len(worst), skip])
    rep.table(['Subprograma', 'Células curso×categoria com convocados', 'Não convocados acima do último convocado'], rows)
    rep.check('V7 ninguém pulado', f'{tot_skip} candidatos', '≈ 0 (exceções explicáveis)', tot_skip <= 0.005 * len(t1))

    # ------------------------------------------------------------ V8
    rep.h('## V8. Nota de corte da tabela 2')
    rep.p('Para cada célula (curso, semestre, categoria), toma o convocado com a **pior classificação na '
          'categoria** (informação do resultado final, independente do AF) e compara o AF dele com a '
          '`nota_corte_ultima_chamada` da tabela 2 (o menor AF entre os convocados da célula). Se a '
          'classificação e o AF forem coerentes e a célula estiver bem montada, os dois coincidem. '
          'O teste vale para as duas regras de preenchimento (cotas antes do Universal até 21-23; '
          'Universal antes das cotas a partir de 22-24), porque compara posição e nota dentro da mesma '
          'categoria.')
    t2_by = {}
    for r in t2:
        t2_by[(r['subprograma'], r['campus'], r['turno'], r['curso'], r['semestre'], r['categoria'])] = r
    sys.path.insert(0, os.path.dirname(__file__))
    import build_tables
    cell = defaultdict(list)
    for c in conv:
        a = alunos.get((c['subprograma'], c['id_aluno']))
        if not a or not c['cota'] or not a['class_' + c['cota']] or a['argumento_final'] == '':
            continue
        k = (build_tables.course_key(c['campus'], c['curso'], c['turno']) if c['curso']
             else build_tables.course_key(a['campus'], a['curso'], a['turno']))
        cell[(c['subprograma'], k[0], k[1], k[2], c['semestre'], c['cota'])].append(
            (int(a['class_' + c['cota']]), float(a['argumento_final'])))
    rows = []
    tot_ok = tot_n = 0
    for sp in SUBS:
        n = ok = 0
        for key, lst in cell.items():
            if key[0] != sp:
                continue
            t = t2_by.get(key)
            if not t or t['nota_corte_ultima_chamada'] == '':
                continue
            n += 1
            pior = max(lst)[1]
            ok += abs(pior - float(t['nota_corte_ultima_chamada'])) < 1e-6
        tot_ok += ok
        tot_n += n
        rows.append([sp, n, ok, f'{ok / max(n, 1):.2%}'])
    rep.table(['Subprograma', 'Células com nota de corte', 'Corte = AF do pior classificado', '%'], rows)
    rep.check('V8 nota de corte coerente com a classificação', f'{tot_ok / max(tot_n, 1):.2%} das células',
              '≥ 99%', tot_ok / max(tot_n, 1) >= 0.99)

    # ------------------------------------------------------------ V9
    rep.h('## V9. Regime da cascata de preenchimento')
    rep.p('Até 21-23 as vagas de cota eram preenchidas antes do Universal; a partir de 22-24 (Lei '
          '14.723/2023) o Universal é preenchido primeiro e o cotista só ocupa vaga reservada se não '
          'alcançar a ampla concorrência. Consequência observável, no 1º semestre e na 1ª chamada: '
          'convocados **por cota** cuja classificação no Universal está dentro do número de vagas do '
          'Universal do curso (ou seja, que teriam entrado pela ampla concorrência). Antes da lei esse '
          'número deve ser positivo; depois, zero. A comparação usa a posição e não o AF, porque vagas '
          'de cota não preenchidas migram para o Universal e baixam o corte dele. Os dados não usam a '
          'regra na construção das tabelas, então o teste confronta os dados com a regra de cada edital.')
    rows = []
    vagas_su = {}
    for key, r in t2_by.items():
        if r['categoria'] == 'SU' and r['semestre'] in ('0', '1') and r['vagas'] != '':
            vagas_su[key[:4]] = int(r['vagas'])
    regime_ok = True
    for sp in SUBS:
        n = dentro = 0
        for c in conv:
            if (c['subprograma'] != sp or c['chamada'] != '1' or c['semestre'] not in ('0', '1')
                    or not c['cota'] or c['cota'] == 'SU'):
                continue
            a = alunos.get((sp, c['id_aluno']))
            if not a or a['class_SU'] == '':
                continue
            k = build_tables.course_key(c['campus'], c['curso'], c['turno'])
            vs = vagas_su.get((sp,) + k)
            if vs is None:
                continue
            n += 1
            dentro += int(a['class_SU']) <= vs
        frac = dentro / max(n, 1)
        ok = (dentro == 0) if sp in LEI_14723 else (dentro > 0 or n == 0)
        regime_ok &= ok
        rows.append([sp, 'Universal primeiro' if sp in LEI_14723 else 'cotas primeiro', n, dentro,
                     f'{frac:.1%}', '0' if sp in LEI_14723 else '> 0'])
    rep.table(['Subprograma', 'Regra do edital', 'Convocados por cota (1º sem., 1ª chamada)',
               'Dentro das vagas do Universal pela classificação', '%', 'Esperado'], rows)
    rep.check('V9 regime da cascata coerente com o edital', 'antes: > 0 em todos os anos; depois: 0 em 22-24 e 23-25',
              '> 0 antes e 0 depois da Lei 14.723', regime_ok)

    # ------------------------------------------------------------ V10
    rep.h('## V10. Quadro de vagas')
    rep.p('(a) Soma das vagas extraídas × "TOTAL GERAL" impresso no edital (quando existe). '
          '(b) Linha de Ciência da Computação do PDF × CSV. (c) Regras da Lei 12.711, que não dependem '
          'da ordem das colunas: metade das vagas de escola pública vai para a renda mais baixa '
          '(|R1 − R2| ≤ 1 por curso) e a parcela PPI é ≥ não PPI. O teste (c) também é aplicado à ordem '
          'alternativa das colunas, para mostrar que ele distingue as duas leituras.')
    A = ['EP_R1_PPI_PCD', 'EP_R1_PPI', 'EP_R2_PPI_PCD', 'EP_R2_PPI',
         'EP_R1_NPPI_PCD', 'EP_R1_NPPI', 'EP_R2_NPPI_PCD', 'EP_R2_NPPI']
    B = ['EP_R1_PPI_PCD', 'EP_R1_PPI', 'EP_R1_NPPI_PCD', 'EP_R1_NPPI',
         'EP_R2_PPI_PCD', 'EP_R2_PPI', 'EP_R2_NPPI_PCD', 'EP_R2_NPPI']

    def lei(rows_v, ordem=None):
        okr = okp = 0
        for r in rows_v:
            usados = [k for k in r if k.startswith('EP_')]
            vals = [r[k] for k in usados]
            labs = ordem or usados
            d = dict(zip(labs, vals))
            r1 = sum(v for k, v in d.items() if '_R1_' in k)
            r2 = sum(v for k, v in d.items() if '_R2_' in k)
            ppi = sum(v for k, v in d.items() if k.endswith('_PPI') or k.endswith('_PPI_PCD'))
            nppi = sum(v for k, v in d.items() if 'NPPI' in k)
            okr += abs(r1 - r2) <= 1
            okp += ppi >= nppi
        return okr / max(len(rows_v), 1), okp / max(len(rows_v), 1)

    rows, all_ok = [], True
    for sp in SUBS:
        vr, st = vagas.extract(sp)
        path = os.path.join(RAW, sp, 'PAS3', 'Edital_de_abertura', 'edital_de_abertura.pdf')
        text = flat(' '.join(pdf_pages(path)))
        tg = 0
        for m in TOTAL_GERAL_RE.finditer(text):
            nums = [int(x.replace('.', '')) for x in m.group(1).split()]
            tg += nums[0] if nums[0] == sum(nums[1:]) else nums[-1] if nums[-1] == sum(nums[:-1]) else sum(nums[:10])
        total = sum(r['total'] for r in vr)
        # linha de CC no PDF
        lines = [' '.join(l.split()) for p in pdf_pages(path) for l in p.splitlines()]
        joined = [a + ' ' + b for a, b in zip(lines, lines[1:] + [''])]
        cc_pdf = []
        for l1, l2 in zip(lines, joined):
            if re.match(r'(?:I{1,2}\s+)?Ciência da Computação \(Bacharelado\)\s+\d', l1):
                cc_pdf.append(l1)
            elif re.fullmatch(r'(?:I{1,2}\s+)?Ciência da Computação', l1) and re.match(r'.*\(Bacharelado\)(\s+\d+){10,11}\s*$', l2):
                cc_pdf.append(l2)
        cc_pdf = [re.sub(r'^.*?\(Bacharelado\)', '', l) for l in cc_pdf]
        cc_csv = [r for r in vr if r['curso'].startswith('CIENCIA DA COMPUTACAO')]
        cc_ok = bool(cc_pdf) and all(
            sorted(int(x) for x in re.findall(r'\b\d+\b', l)) ==
            sorted([r['total']] + [r[k] for k in r if k.startswith('EP_')] + [r['NEG'], r['SU']])
            or sorted(int(x) for x in re.findall(r'\b\d+\b', l)) ==
            sorted([r[k] for k in r if k.startswith('EP_')] + [r['NEG'], r['SU']])
            for l, r in zip(cc_pdf, cc_csv))
        ordem = [k for k in vr[0] if k.startswith('EP_')]
        alt = B if ordem == A else A
        u = lei(vr)
        a = lei(vr, alt)
        ok = (not tg or tg == total) and cc_ok and min(u) >= 0.98 and min(a) < 0.5
        all_ok &= ok
        rows.append([sp, total, tg or '—', 'sim' if cc_ok else 'NÃO', f'{u[0]:.0%} / {u[1]:.0%}',
                     f'{a[0]:.0%} / {a[1]:.0%}'])
    rep.table(['Subprograma', 'Vagas extraídas', 'TOTAL GERAL do edital', 'Linha de CC idêntica',
               'Lei 12.711 (renda / PPI), ordem usada', 'Idem, ordem alternativa'], rows)
    rep.check('V10 quadro de vagas', 'ver tabela', 'totais iguais, CC idêntica, ordem usada ≥ 98% e alternativa < 50%', all_ok)

    # ------------------------------------------------------------ V11
    rep.h('## V11. Convocados na 1ª chamada × vagas e candidatos')
    rep.p('Por curso, o número de convocados na 1ª chamada (editais de convocação) é comparado com o '
          'esperado pelas regras: no 1º semestre, o menor valor entre as vagas (edital de abertura) e os '
          'candidatos não eliminados do curso (resultado final); no 2º semestre, o menor valor entre as '
          'vagas e os candidatos que sobraram depois de todas as chamadas do 1º semestre. As vagas que '
          'sobram numa categoria migram para outra do mesmo curso. Três documentos independentes. '
          'Diferença de 1 a 2 é esperada quando há candidato sub judice ou convocação posterior '
          'por decisão judicial.')
    # por curso e semestre: vagas, convocados na 1ª chamada e convocados em todas as chamadas
    vag, c1, call, cand = defaultdict(int), defaultdict(int), defaultdict(int), {}
    for r in t2:
        k = (r['subprograma'], r['campus'], r['turno'], r['curso'])
        sem = r['semestre']
        if r['vagas'] != '':
            vag[(k, sem)] += int(r['vagas'])
        c1[(k, sem)] += int(r['convocados_1a_chamada'] or 0)
        call[(k, sem)] += int(r['convocados'] or 0)
        if r['categoria'] == 'SU' and r['inscritos'] != '':
            cand[k] = int(r['inscritos'])  # todo candidato tem classificação no Universal

    def esperado(k):
        # 1º semestre: até as vagas; 2º semestre: o que sobra depois de todas as chamadas do 1º
        if (k, '0') in vag:  # ingresso único (18-20)
            return min(vag[(k, '0')], cand[k])
        e1 = min(vag[(k, '1')], cand[k])
        e2 = min(vag[(k, '2')], max(cand[k] - call[(k, '1')], 0))
        return e1 + e2

    cursos = {k for (k, _sem) in vag}
    rows, fr = [], []
    for sp in SUBS:
        ks = [k for k in cursos if k[0] == sp and k in cand and (c1[(k, '0')] + c1[(k, '1')] + c1[(k, '2')])]
        obs = {k: c1[(k, '0')] + c1[(k, '1')] + c1[(k, '2')] for k in ks}
        eq = sum(obs[k] == esperado(k) for k in ks)
        perto = sum(0 < abs(obs[k] - esperado(k)) <= 2 for k in ks)
        longe = [k for k in ks if abs(obs[k] - esperado(k)) > 2]
        fr.append((eq + perto) / max(len(ks), 1))
        rows.append([sp, len(ks), eq, perto, len(longe),
                     '; '.join(f'{k[3][:30]} ({obs[k]} conv., esperado {esperado(k)})' for k in longe[:3])])
    rep.table(['Subprograma', 'Cursos', 'Igual', 'Diferença ≤ 2', 'Diferença > 2', 'Exemplos'], rows)
    rep.p()
    rep.p('Em 18-20 as convocações são para o total de vagas, sem separar semestres (semestre 0 na '
          'tabela 2); o esperado usa a soma das vagas dos dois semestres.')
    ok11 = all(f >= 0.95 for f in fr)
    rep.check('V11 1ª chamada = mín(vagas, candidatos)', ', '.join(f'{sp}: {f:.0%}' for sp, f in zip(SUBS, fr)),
              '≥ 95% dos cursos com diferença ≤ 2', ok11)

    # ------------------------------------------------------------ V12
    rep.h('## V12. Homologação, duplicatas e SISUnB')
    rep.p('Homologados (relação de selecionados) devem ter sido convocados (editais de convocação). '
          'Convocações repetidas foram removidas no pipeline (o edital da 1ª chamada do 2º semestre de '
          '21-23 publica duas vezes o bloco de Enfermagem). Em 15-17 e 16-18 o SISUnB permitia trocar '
          'de curso depois do resultado: conta quantos aprovados mudaram de curso.')
    conv_ids = {(c['subprograma'], c['id_aluno']) for c in conv}
    rows, orf_tot = [], 0
    for sp in SUBS:
        h = {(r['subprograma'], r['id_aluno']) for r in rel if r['subprograma'] == sp and r['tipo'] == 'homologado'}
        orf = len(h - conv_ids)
        orf_tot += orf
        rep_conv = Counter((c['id_aluno'], c['curso'], c['semestre'], c['chamada'], c['cota']) for c in conv if c['subprograma'] == sp)
        dup = sum(v - 1 for v in rep_conv.values() if v > 1)
        apr = [a for a in t1 if a['subprograma'] == sp and a['aprovado'] == 'True']
        mud = sum(a['curso_mudou_sisunb'] == 'True' for a in apr)
        rows.append([sp, len(h) or '—', orf if h else '—', dup, len(apr), mud if sp in SISUNB else f'{mud} (sem SISUnB)'])
    rep.table(['Subprograma', 'Homologados', 'Homologados sem convocação', 'Convocações duplicadas',
               'Aprovados', 'Aprovados que mudaram de curso'], rows)
    rep.check('V12 homologados ⊆ convocados e sem duplicatas', f'{orf_tot} homologados sem convocação',
              '≤ 1% dos homologados', orf_tot <= 0.01 * max(1, sum(r['tipo'] == 'homologado' for r in rel)))

    # ------------------------------------------------------------ V13
    rep.h('## V13. Junção entre edital de abertura e resultado final')
    rep.p('O nome do curso é escrito de formas diferentes nos editais; o pipeline casa cada nome com o '
          'do quadro de vagas (ver `intermediarios/correspondencia_cursos.csv`). Conta as células da '
          'tabela 2 que ficaram órfãs: com candidatos ou convocados e sem vagas (junção falhou), e '
          'cursos com vagas e nenhum candidato no resultado (pode ser real: cursos noturnos pequenos ou '
          'que exigem certificação de habilidade específica).')
    rows, orf_tot, cel_tot = [], 0, 0
    for sp in SUBS:
        cel = [r for r in t2 if r['subprograma'] == sp and r['semestre'] != '']
        orf = [r for r in cel if r['vagas'] == '' and (r['convocados'] != '0' or r['inscritos'] not in ('0', ''))]
        sem = sorted({r['curso'][:40] for r in cel if r['categoria'] == 'SU' and r['vagas'] not in ('', '0')
                      and r['inscritos'] == '0'})
        orf_tot += len(orf)
        cel_tot += len(cel)
        rows.append([sp, len(cel), len(orf), len(sem), '; '.join(sem[:4])])
    rep.table(['Subprograma', 'Células', 'Com candidatos e sem vagas', 'Cursos com vagas e sem candidatos', 'Exemplos'], rows)
    rep.check('V13 junção vagas × resultado', f'{orf_tot} células órfãs em {cel_tot}', '≤ 0,1%', orf_tot <= 0.001 * cel_tot)

    # resumo no topo
    resumo = ['## Resumo', '', '| Teste | Resultado | Critério | Situação |', '|---|---|---|---|']
    resumo += [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in rep.resumo]
    i = rep.lines.index('<!-- RESUMO -->')
    rep.lines[i:i + 1] = resumo
    path = os.path.join(PARSED, 'validacao.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rep.lines) + '\n')
    print('\n'.join(resumo))


if __name__ == '__main__':
    main()
