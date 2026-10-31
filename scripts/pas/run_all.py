"""Roda o pipeline completo: extração, filtros do grupo e validação.

  1. build_tables.py                         -> tabela1_alunos.csv, tabela2_curso_cota.csv, subprogramas.csv
  2. alteracoes_de_pipeline/remove_14-16.py   -> *_sem_14_16.csv (exclui o subprograma 14-16)
  3. alteracoes_de_pipeline/remove_eng_software.py -> *_sem_eng_soft.csv (tira a marcação de Eng. Software)
  4. validate.py                             -> parsed_data/validacao.md (sobre as tabelas *_sem_eng_soft)

As tabelas finais usadas no artigo são as *_sem_eng_soft.csv.
Uso:  python3 scripts/pas/run_all.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PASSOS = ['build_tables.py',
          os.path.join('alteracoes_de_pipeline', 'remove_14-16.py'),
          os.path.join('alteracoes_de_pipeline', 'remove_eng_software.py'),
          'validate.py']

for passo in PASSOS:
    print(f'\n=== {passo} ===', flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, passo)], check=True)
