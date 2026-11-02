"""
Lê os CSVs sem o subprograma 14-16 e remove a marcação de Engenharia de Software.
Os registros são mantidos na base (pois são vagas/alunos reais da UnB), 
mas a tag na coluna 'area_computacao' é apagada.
"""
import csv
import os
import sys

# Ajuste este caminho de acordo com a pasta onde você colocou os scripts avulsos
# Supondo que o script esteja em scripts/limpeza/ e a pasta parsed_data esteja na raiz
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
PARSED = os.path.join(ROOT, 'parsed_data')

# Lê os arquivos que já passaram pelo filtro do 14-16
FILES = [
    'tabela1_alunos_sem_14_16.csv',
    'tabela2_curso_cota_sem_14_16.csv',
    'subprogramas_sem_14_16.csv'
]

def main():
    if not os.path.exists(PARSED):
        print(f"Erro: Pasta {PARSED} não encontrada.")
        sys.exit(1)

    for filename in FILES:
        filepath = os.path.join(PARSED, filename)
        # Cria o novo nome de arquivo
        out_filepath = os.path.join(PARSED, filename.replace('_sem_14_16.csv', '_sem_eng_soft.csv'))

        if not os.path.exists(filepath):
            print(f"Aviso: Arquivo de entrada não encontrado, ignorando -> {filepath}")
            continue

        linhas_totais = 0
        tags_removidas = 0

        # Lê o CSV 
        with open(filepath, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = reader.fieldnames
            
            modified_rows = []
            for row in reader:
                linhas_totais += 1
                
                # Se a tabela tiver a coluna area_computacao e for a tag de Eng. Software, limpa o campo
                if 'area_computacao' in row and row['area_computacao'] == 'ENGENHARIAS_FGA_SOFTWARE':
                    row['area_computacao'] = ''
                    tags_removidas += 1
                
                modified_rows.append(row)

        # Escreve o novo CSV
        with open(out_filepath, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(modified_rows)

        print(f"Sucesso: {filename} -> {os.path.basename(out_filepath)}")
        print(f"  - Linhas totais processadas: {linhas_totais}")
        if 'area_computacao' in fieldnames:
            print(f"  - Tags 'ENGENHARIAS_FGA_SOFTWARE' removidas: {tags_removidas}\n")
        else:
            print(f"  - (Arquivo não possui coluna 'area_computacao')\n")

if __name__ == '__main__':
    main()