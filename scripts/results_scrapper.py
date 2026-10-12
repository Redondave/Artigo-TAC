# Script para pegar os arquvivos em PDF de 'resources' e extrair os dados de cada um deles, salvando em um arquivo CSV.
import os
import csv
import re
import pypdf

def extract_results_from_pdf(pdf_path):
    # define os campos que serão extraídos do PDF
    headers = ['N° de inscrição', 'Nome', 'Curso', 'Score bruto 1° parte (sub1)', 'Score bruto 2° parte (sub2)', 'Nota da redação (sub1)',
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
    current_course = ''
    course_header_pattern = re.compile(
        r'[A-ZÀ-Ú0-9][A-ZÀ-Ú0-9 .&/-]*\s+\('
        r'[^)]*(?:BACHARELADO|LICENCIATURA|PSIC)[^)]*\)'
    )
    for page in pypdf_reader.pages:
        text = page.extract_text()
        if text:
            # Mantém os cabeçalhos localizáveis mesmo quando há vários na mesma página.
            normalized_text = ' '.join(text.split())
            course_headers = []
            search_start = 0
            for line in text.splitlines():
                candidate = ' '.join(line.split())
                if course_header_pattern.fullmatch(candidate):
                    position = normalized_text.find(candidate, search_start)
                    if position >= 0:
                        course_headers.append((position, re.sub(r'\s+\(', '(', candidate)))
                        search_start = position + len(candidate)

            pattern = re.compile(
                r"(?<!\d)\d{8}\s*,\s*[^,\r\n]+?"
                r"(?:\s*,\s*(?:-?\d+(?:[.,]\d+)?|-))+"
                r"\s*/"
            )

            # encontra todas as correspondências do padrão no texto extraído
            header_index = 0
            for match in pattern.finditer(normalized_text):
                while (header_index < len(course_headers)
                       and course_headers[header_index][0] < match.start()):
                    current_course = course_headers[header_index][1]
                    header_index += 1

                # Divide o registro em campos e insere o curso após o nome.
                data = [
                    item.strip()
                    for item in match.group(0).rstrip('/ ').split(',')
                ]
                data.insert(2, current_course)
                extracted_data.append(data)

    with open('../parsed_data/extracted_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(extracted_data)

    return extracted_data

def main():
    # define o caminho para a pasta 'resources'
    resources_path = '../raw_data'

    # pergunta o PDF que o usuário deseja extrair os dados
    pdf_file = input("Digite o nome do arquivo PDF para extração")

    if not pdf_file.endswith('.pdf'):
        pdf_file += '.pdf'

    # percorre todos os arquivos na pasta 'resources'
    extracted = extract_results_from_pdf(os.path.join(resources_path, f"{pdf_file}"))
    if extracted:
        print(f"Extração concluída com sucesso. {len(extracted)} registros extraídos.")
    else:
        print("Nenhum registro foi extraído.")

main()