# Script para pegar os arquvivos em PDF de 'resources' e extrair os dados de cada um deles, salvando em um arquivo CSV.
import os
import csv
import re
import pypdf

def extract_results_from_pdf(pdf_path):
    # define os campos que serão extraídos do PDF
    headers = ['N° de inscrição','Nome', 'Score bruto 1° parte (sub1)', 'Score bruto 2° parte (sub2)', 'Nota da redação (sub1)',
               'Score bruto 1° parte (sub1)', 'Score bruto 2° parte (sub2)', 'Nota da redação (sub2)',
               'Score bruto 1° parte (sub3)', 'Score bruto 2° parte (sub3)', 'Nota da redação (sub3)',
               'Argumento final', 'Classificação (SU)', 'Classificação (NE)', 'Classificação (EP / PPI / < 1SM)'
               'Classificação (EP / PPI / PCD / < 1SM)', 'Classificação (EP / < 1SM)', 'Classificação (EP / PCD / < 1SM)',
               'Classificação (PCD)', 'Classificação (EP / PPI / > 1SM)', 'Classificação (EP / PPI / PCD / > 1SM)',
               'Classificação (EP / > 1SM)', 'Classificação (EP / PCD / > 1SM)']

    # extrai os dados do PDF e salva em um arquivo CSV
    extracted_data = []

    # abre o arquivo PDF e extrai o texto de cada página
    pypdf_reader = pypdf.PdfReader(pdf_path)
    for page in pypdf_reader.pages:
        text = page.extract_text()
        if text:
            # remove quebras de linha do texto extraído
            text = text.replace('\n', ' ')
            pattern = re.compile(
                r"(?<!\d)\d{8}\s*,\s*[^,\r\n]+?"
                r"(?:\s*,\s*(?:-?\d+(?:[.,]\d+)?|-))+"
                r"\s*/"
            )

            # encontra todas as correspondências do padrão no texto extraído
            matches = pattern.findall(text)
            for match in matches:
                # remove espaços extras e divide os dados em uma lista
                data = [item.strip() for item in match.split('/')]
                extracted_data.append(data)

    with open('../parsed_data/extracted_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(extracted_data)

    return extracted_data

def main():
    # define o caminho para a pasta 'resources'
    resources_path = '../resources'

    # percorre todos os arquivos na pasta 'resources'
    extracted = extract_results_from_pdf(os.path.join(resources_path, 'notas_e_classificacao_sub3_2025.pdf'))
    if extracted:
        print(f"Extração concluída com sucesso. {len(extracted)} registros extraídos.")
    else:
        print("Nenhum registro foi extraído.")

main()