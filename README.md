# O Artigo

## Pergunta de pesquisa:
Como se dá a evolução do desempenho e das notas de corte no **PAS/UnB** ao longo de 10 ou
mais subprogramas, analisando comparativamente as métricas estatísticas **(média, mediana e desvio padrão)** 
prova a prova **(PAS 1, PAS 2 e PAS 3)** e subprograma a subprograma, sob a perspectiva dos diferentes sistemas de cotas?

## Bases de dados
- **Editais** oficiais e relatórios de resultados de 10 ou mais subprogramas do PAS/UnB;
- **Gráficos** construídos a partir dos dados estatísticos obtidos por meio de parsing;
- **Normas** e consultas da avaliação PAS/UnB (resumo dos editais de abertura em [`raw_data/regulamentos.md`](raw_data/regulamentos.md))

# O Projeto

## Estrutura de pastas
O projeto está estruturado da seguinte forma, considerando o uso de scrips **Python** para lidar com os dados em **PDF** e
formatá-los em **CSVs** a serem a base estatística para o trabalho:
- **/scripts** : Contém os scripts python, com as funcionalidades descritas posteriormente;
- **/resources** : Contém os PDFs que servem de base para os scripts;
- **/parsed_data** : Armazena os resultados do processamento.

## Scripts
Os extratores ficam em **`scripts/pas/`** e leem todos os PDFs de `raw_data/` de uma vez. Para gerar tudo:

```bash
pip install pypdf            # e poppler-utils (pdftotext), usado na validação
python3 scripts/pas/run_all.py
```

O `run_all.py` roda a extração (`build_tables.py`), os filtros do grupo (`alteracoes_de_pipeline/remove_14-16.py` e `remove_eng_software.py`) e a validação (`validate.py`).

**Tabelas do artigo** (em `parsed_data/`):
- **tabela1_alunos_sem_eng_soft.csv**: uma linha por candidato e subprograma, com notas das 3 etapas, argumento final, classificação em cada cota, aprovação e homologação (anonimizado, sem nomes);
- **tabela2_curso_cota_sem_eng_soft.csv**: vagas, inscritos, convocados e notas de corte por subprograma, curso, turno, semestre e categoria de cota;
- **subprogramas_sem_eng_soft.csv**: datas e regras de cada subprograma.

Documentação:
- [`docs/glossario.md`](docs/glossario.md): o que cada coluna significa e de onde vem;
- [`metodologia.md`](metodologia.md): como os dados foram extraídos, as correções feitas e o resumo da validação;
- [`parsed_data/validacao.md`](parsed_data/validacao.md): relatório completo dos 13 testes de qualidade;
- [`docs/plano-artigo.md`](docs/plano-artigo.md): o plano do artigo.
