"""
Lê os CSVs gerados pelo pipeline e cria novas tabelas removendo todos 
os registros vinculados ao subprograma 14-16.
"""
import csv
import os
import sys

# Configuração de caminhos baseada na estrutura do projeto
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
PARSED = os.path.join(ROOT, 'parsed_data')

# As 3 tabelas principais que serão filtradas
FILES = [
    'tabela1_alunos.csv',
    'tabela2_curso_cota.csv',
    'subprogramas.csv'
]

def main():
    if not os.path.exists(PARSED):
        print(f"Erro: Pasta {PARSED} não encontrada. Rode o build_tables.py primeiro.")
        sys.exit(1)

    for filename in FILES:
        filepath = os.path.join(PARSED, filename)
        out_filepath = os.path.join(PARSED, filename.replace('.csv', '_sem_14_16.csv'))

        if not os.path.exists(filepath):
            print(f"Aviso: Arquivo não encontrado, ignorando -> {filepath}")
            continue

        linhas_removidas = 0
        linhas_mantidas = 0

        # Lê o CSV original
        with open(filepath, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = reader.fieldnames
            
            filtered_rows = []
            for row in reader:
                if row.get('subprograma') == '14-16':
                    linhas_removidas += 1
                else:
                    filtered_rows.append(row)
                    linhas_mantidas += 1

        # Escreve o novo CSV limpo
        with open(out_filepath, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_rows)

        print(f"Sucesso: {filename} -> {os.path.basename(out_filepath)}")
        print(f"  - Linhas mantidas: {linhas_mantidas}")
        print(f"  - Linhas removidas (14-16): {linhas_removidas}\n")

if __name__ == '__main__':
    main()