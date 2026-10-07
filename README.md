# O Artigo

## Pergunta de pesquisa:
Como se dá a evolução do desempenho e das notas de corte no **PAS/UnB** ao longo de 10 ou
mais subprogramas, analisando comparativamente as métricas estatísticas **(média, mediana e desvio padrão)** 
prova a prova **(PAS 1, PAS 2 e PAS 3)** e subprograma a subprograma, sob a perspectiva dos diferentes sistemas de cotas?

## Bases de dados
- **Editais** oficiais e relatórios de resultados de 10 ou mais subprogramas do PAS/UnB;
- **Gráficos** construídos a partir dos dados estatísticos obtidos por meio de parsing;
- **Normas** e consultas da avaliação PAS/UnB

# O Projeto

## Estrutura de pastas
O projeto está estruturado da seguinte forma, considerando o uso de scrips **Python** para lidar com os dados em **PDF** e
formatá-los em **CSVs** a serem a base estatística para o trabalho:
- **/scripts** : Contém os scripts python, com as funcionalidades descritas posteriormente;
- **/resources** : Contém os PDFs que servem de base para os scripts;
- **/parsed_data** : Armazena os resultados do processamento.

## Scripts
Usamos os seguintes scripts python para o parsing / filtragem:
- **results_scrapper.py** : Responsável por fazer o parse do arquivo de **Resultados finais do 3°subprograma do PAS**, 
o que gera diversos metadados _(notas por subprograma, posição, argumento final...)_;
- **classificated_filter.py** : Responsável por fazer o parse do arquivo de **Convocados para os cursos de graduação**, gerando
metadados sobre os convocados por categoria de cota, com número de vagas detalhado por curso.
