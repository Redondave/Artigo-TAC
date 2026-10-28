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
Os extratores ficam em **`scripts/pas/`** e leem todos os PDFs de `raw_data/` de uma vez:

```bash
pip install pypdf
python3 scripts/pas/build_tables.py   # gera as tabelas em parsed_data/
python3 scripts/pas/validate.py       # gera parsed_data/validacao.md
```

Saídas principais em `parsed_data/`:
- **tabela1_alunos.csv**: uma linha por candidato e subprograma, com notas das 3 etapas, argumento final, classificação em cada cota, aprovação e homologação (anonimizado, sem nomes);
- **tabela2_curso_cota.csv**: vagas, inscritos, convocados e notas de corte por subprograma, curso, semestre e categoria de cota;
- **subprogramas.csv**: datas e regras de cada subprograma.

Como a extração foi feita, as decisões tomadas e as limitações dos dados estão em [`metodologia.md`](metodologia.md). O plano do artigo está em [`docs/plano-artigo.md`](docs/plano-artigo.md).
