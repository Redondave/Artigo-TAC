# Metodologia: extração e organização dos dados

Este documento registra como os dados do artigo foram obtidos a partir dos PDFs oficiais do PAS/UnB. Ele segue o "Prompt para o próximo Claude" de [`docs/plano-artigo.md`](docs/plano-artigo.md) e serve de base para a seção de Metodologia do artigo.

## 1. Fontes

Todos os arquivos estão em `raw_data/<subprograma>/`, nos 10 subprogramas de `14-16` a `23-25`. As regras de cada edital de abertura estão resumidas em [`raw_data/regulamentos.md`](raw_data/regulamentos.md).

| Tipo de edital | Pasta | Usado para |
|---|---|---|
| Resultado final do PAS 3 (e `SJ*`) | `PAS3/Resultado_final/` | Notas das 3 etapas, argumento final, curso e classificação em cada cota |
| Resultado final do PAS 1 e PAS 2 (e retificações) | `PAS1/` e `PAS2/Resultado_final/` | Comparecimento e notas de quem não chegou ao PAS 3 |
| Convocação para registro acadêmico | `PAS3/Convocacao_para_registro_academico/` | Quem foi aprovado, em qual chamada, semestre e cota |
| Relação das pessoas selecionadas | `PAS3/Relacao_das_pessoas_selecionadas/` | Registro acadêmico homologado (no 14-16, a lista de selecionados) |
| Edital de abertura | `PAS3/Edital_de_abertura/` | Quadro de vagas por curso, semestre e cota |
| Média e desvio padrão | `media_e_desvio_padrao.pdf` e fim do resultado final | Validação |

## 2. Como rodar

```bash
pip install pypdf
python3 scripts/pas/build_tables.py   # gera as tabelas (cerca de 3 min na 1ª vez; depois usa cache)
python3 scripts/pas/validate.py       # gera parsed_data/validacao.md
```

O texto de cada PDF fica em cache em `.cache/pdf_text/`, que não vai para o repositório.

## 3. Pipeline (`scripts/pas/`)

| Módulo | O que faz |
|---|---|
| `common.py` | Leitura dos PDFs com `pypdf`, cache, normalização de texto e anonimização |
| `cotas.py` | Vocabulário padronizado das 10 categorias, lido da descrição de cada edital |
| `resultado_pas3.py` | Resultado final do PAS 3, incluindo subseções e editais sub judice |
| `resultado_pas12.py` | Resultados do PAS 1 e PAS 2, com as retificações aplicadas |
| `convocacoes.py` | Convocações (por código de legenda ou por classificação) e relações de selecionados |
| `vagas.py` | Quadro de vagas dos editais de abertura |
| `build_tables.py` | Junta tudo e grava os CSVs |
| `validate.py` | Verificações automáticas |

Substituem os antigos `results_scrapper.py`, que perdia cerca de 13% dos registros e tinha o cabeçalho de cotas errado, e `classificated_filter.py`, que estava vazio.

### Decisões de extração

- **O texto do pypdf quebra números e palavras** (`27. 213`, `Sistema Universa l`, sinal negativo numa linha e o número na outra). As linhas são unidas sem inserir espaço, e os espaços dentro dos campos numéricos são removidos.
- **O mapa de cotas não é fixo.** A lista de categorias é lida da frase "na seguinte ordem: …" de cada resultado. Ela muda ao longo da década:
  - o `14-16` não tem as categorias PcD (6 categorias);
  - a renda passa de 1,5 para 1 SM e quilombolas entram no nível PPI a partir do `22-24`.
- **Rótulos padronizados:** `SU`, `NEG`, `EP_<renda>_<raça>[_PCD]`.
  - `R1` é a renda até o limite e `R2`, acima dele.
  - `PPI` inclui quilombolas a partir do `22-24`.
  - O agrupamento usado nos gráficos F1 a F3 está em `grupo_concorrencia`: Universal, Negros, EP PPI e EP Não-PPI.
- **Chave do aluno.** A inscrição se mantém nas 3 etapas e liga os editais entre si. Na saída ela vira `id_aluno`, um SHA-256 com sal da inscrição e do subprograma, e **nenhum nome é gravado nos CSVs**.
- **Sub judice.** Os candidatos em subseções ou editais `SJ*` ficam com `sub_judice = True`, para o grupo decidir se exclui. Quando um edital SJ retifica as notas de um candidato, a retificação substitui o registro original.
- **Retificações do PAS 1 e PAS 2** são aplicadas em ordem. Uma nota provisória nunca substitui uma final.
- **Ordem das colunas do quadro de vagas.** É deduzida dos rótulos do cabeçalho de cada edital: há três arranjos diferentes, e a coluna de total aparece no início ou no fim.
  - Em 18-20, 20-22, 21-23 e 22-24, o total extraído bate exatamente com o "TOTAL GERAL" do edital: 4.232, 4.238, 4.233 e 4.233 vagas.
  - Em 19-21 e 23-25, o total extraído (4.232 e 4.212) não foi comparado com o "TOTAL GERAL" do edital.
  - Em 15-17 a 17-19, o edital não traz total geral.

## 4. Tabelas geradas (`parsed_data/`)

### `tabela1_alunos.csv`: uma linha por candidato e subprograma (212.344 linhas)

| Coluna | Descrição |
|---|---|
| `subprograma`, `id_aluno` | Chave anonimizada |
| `campus`, `turno`, `curso` | Curso do resultado final do PAS 3 (vazio para quem não chegou ao PAS 3) |
| `area_computacao` | `CC_BACHARELADO`, `COMPUTACAO_LICENCIATURA`, `ENG_COMPUTACAO` ou `ENGENHARIAS_FGA_SOFTWARE` |
| `compareceu_pas1..3` | Se aparece no resultado daquela etapa (vazio quando o PDF da etapa não existe) |
| `eb1_pasN`, `eb2_pasN`, `nr_pasN` | Escore bruto da parte 1, da parte 2 e nota da redação de cada etapa |
| `argumento_final` | Argumento final |
| `class_<categoria>` | Classificação em cada uma das 10 categorias (vazio = não concorreu) |
| `sistema_inscricao` | Categoria mais restritiva em que o candidato tem classificação, ou seja, a da inscrição (inferida) |
| `grupo_concorrencia` | Agrupamento para os gráficos |
| `aprovado` | Aparece em alguma convocação |
| `cota_aprovacao`, `chamada_aprovacao`, `semestre_aprovacao`, `curso_aprovacao`, `n_convocacoes` | Dados da primeira convocação |
| `homologado` | Registro acadêmico homologado (vazio quando não há relação para o subprograma) |
| `sub_judice`, `faixa_renda_regra` | Marcação sub judice e limite de renda vigente |

### `tabela2_curso_cota.csv`: subprograma × campus × curso × semestre × categoria (16.591 linhas, todos os cursos)

| Coluna | Descrição |
|---|---|
| `chave` | `subprograma\|campus\|curso\|semestre\|categoria` |
| `vagas` | Vagas ofertadas no edital de abertura |
| `inscritos` | Não eliminados no PAS 3 com classificação na categoria (o mesmo número nos dois semestres) |
| `convocados`, `convocados_1a_chamada`, `ultima_chamada` | Convocações na categoria e no semestre |
| `nota_corte_1a_chamada` | Menor argumento final entre os convocados na 1ª chamada |
| `nota_corte_ultima_chamada` | Menor argumento final entre todos os convocados (usado na F5) |

### `subprogramas.csv`

Regras e datas de cada subprograma: data da prova do PAS 3, SISUnB, Lei 14.723, faixa de renda, categorias, contagem de candidatos, convocados e vagas. Serve para os marcadores de eventos da RQ4.

### `intermediarios/`

Convocações, relações e vagas extraídas, já anonimizadas, para auditoria.

## 5. Validação (detalhes em `parsed_data/validacao.md`)

1. **Cobertura.** 100% das inscrições do texto foram extraídas em todos os 10 resultados finais do PAS 3, contra 87% do script antigo. Nos PAS 1 e PAS 2, ficam de fora só linhas que não são notas.
2. **Consistência entre etapas.** As notas das etapas 1 e 2 repetidas no resultado do PAS 3 batem com os resultados do PAS 1 e PAS 2 em 99,6% a 100% dos candidatos. As diferenças são retificações posteriores.
3. **Médias oficiais.** A média e o desvio padrão da Parte II e da redação do PAS 3, calculados a partir da tabela, coincidem com os publicados pelo Cebraspe até a 3ª casa decimal em todos os anos com dado oficial.
   - Nas etapas 1 e 2, as médias calculadas ficam abaixo das oficiais, porque os PDFs dessas etapas incluem candidatos com nota zero que o Cebraspe exclui do cálculo (ausentes ou eliminados).
   - A Parte I não é comparada, porque a média oficial é por língua e a língua de cada candidato não é publicada.
4. **Ordem do argumento final.** A classificação no Universal segue o argumento final em mais de 97% dos pares de candidatos de cada curso. Ficam fora de ordem entre 0 e 212 pares por subprograma, e a causa ainda não foi investigada (pode ser empate ou reclassificação).
5. **Convocados órfãos.** Menos de 10 por subprograma não aparecem no resultado do PAS 3 (candidatos sub judice). A exceção é o `14-16`: lá a fonte é a relação de selecionados, que tem números de inscrição quebrados, e 202 de 3.559 ficam sem correspondência.

## 6. Conferência das colunas contra os gráficos e os editais de regras

Este é o item acrescentado ao prompt do `plano-artigo.md`. Compara o que o plano pede com o que as tabelas têm e com o que os editais permitem medir.

### Colunas adicionadas ao plano original

- **`campus` e `turno`.** O mesmo curso existe em campi e turnos diferentes, por exemplo a Licenciatura em Computação, que é noturna.
- **`nota_corte_1a_chamada` e `nota_corte_ultima_chamada`.** A F5 precisa das duas.
- **`area_computacao`.** Filtra os 4 cursos do artigo e mantém todos os outros para a F7.
- **`grupo_concorrencia`.** Dá as 4 linhas da F1 (Universal, Negros, EP PPI, EP Não-PPI).
- **`sub_judice` e `faixa_renda_regra`.** Os editais mudam a regra de renda, e o grupo precisa poder excluir os casos judiciais.
- **`subprogramas.csv`.** Traz a data das provas (eixo X da F1) e os marcos regulatórios da RQ4.

### Esclarecimentos (afetam a interpretação)

- **Engenharia de Software não tem entrada própria no PAS.** Os editais oferecem "Engenharias: Aeroespacial/Automotiva/Eletrônica/Energia/Software" no campus Gama, com a escolha da habilitação feita ao longo do curso. A F4 e a F8 só podem usar essa entrada comum, marcada como `ENGENHARIAS_FGA_SOFTWARE`, e o artigo deve dizer isso.
- **"Inscritos" são os não eliminados no PAS 3.** Os editais não publicam o número de inscritos por curso, nem os candidatos eliminados.
- **A F9 e a continuidade por cota estão limitadas.** O curso e a cota só aparecem no resultado do PAS 3. Quem desistiu no PAS 1 ou no PAS 2 tem comparecimento e notas, mas não tem curso nem cota.
- **SISUnB (até `16-18`).** O curso do resultado final é a pré-opção. Depois do resultado, o candidato podia trocar de curso, por isso `curso_aprovacao` pode ser diferente de `curso`.
- **A cota de aprovação não é a cota de inscrição.**
  - Até `21-23`, a seleção ia das cotas para o Universal e as vagas não preenchidas migravam.
  - A partir de `22-24`, o Universal é preenchido primeiro e as cotas vão do subsistema menos restritivo para o mais restritivo.
  - Por isso, `convocados` por categoria não precisa ser igual a `vagas`. Para a F6 e a T2, use `sistema_inscricao` (o perfil do candidato) e `cota_aprovacao` (por onde ele entrou).
- **`sistema_inscricao` é inferido.** É a categoria mais restritiva em que o candidato tem classificação, porque ele concorre na própria categoria e em todas as menos restritivas. Um candidato da cota para negros também tem classificação no Universal.
- **"Comparecimento" é observável só pela presença no resultado da etapa.** Para os ausentes não se distingue falta de eliminação.

### Lacunas dos dados (o que não dá para obter dos PDFs do repositório)

| Item | Situação |
|---|---|
| Edital de abertura do `14-16` (vagas) | Não encontrado (Edital nº 21, de 6/9/2016). A rede desta sessão bloqueia o site do Cebraspe |
| PAS 1 e PAS 2 do `14-16` e PAS 1 do `15-17` | Marcados como `sem_dados.txt` |
| Notas EB do PAS 1 e PAS 2 em `15-17` a `17-19` | Esses PDFs só têm tipo D e redação. Para quem chegou ao PAS 3, o EB vem do resultado do PAS 3 |
| Convocações do `14-16` | Usadas as relações de selecionados, sem cota. Falta a 1ª chamada do 1º semestre |
| Convocações do 1º semestre do `18-20` | Só há arquivos do 2º semestre (ingresso concentrado em 2021, na pandemia) |
| Homologação do `16-18` | Não há relação no site (`nao_ha_dados_no_site_do_Cebraspe.txt`) |
| Língua estrangeira de cada candidato | Não publicada, o que impede recalcular o argumento final de forma independente |

### O que retirar ou marcar como limitado no plano

- **"booleano de homologação":** existe para 15-17 e para 17-19 a 23-25. Não existe para 14-16 nem 16-18.
- **T2 (simulação sem cotas):** viável com `argumento_final` e `sistema_inscricao`, mas não reproduz a migração de vagas. Deve ser apresentada como aproximação.
- **F5 no `14-16`:** sem a 1ª chamada do 1º semestre, a nota de corte da 1ª chamada desse subprograma fica incompleta.

## 7. Próximos passos

1. Gerar todos os gráficos e tabelas da Metodologia II a partir de `tabela1_alunos.csv`, `tabela2_curso_cota.csv` e `subprogramas.csv`.
2. Investigar os pares fora de ordem da validação 4 e os 202 órfãos do `14-16`.
3. Tentar obter o Edital nº 21/2016 e os Editais nº 1 de cada subprograma, que têm a fórmula do argumento final.
