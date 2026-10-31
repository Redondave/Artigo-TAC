# Metodologia: extração, organização e validação dos dados

Este documento registra como os dados do artigo foram obtidos a partir dos PDFs oficiais do PAS/UnB, quais correções foram feitas e como a qualidade dos dados foi verificada. Ele serve de base para a seção de Metodologia do artigo. O significado de cada coluna está em [`docs/glossario.md`](docs/glossario.md), e o relatório completo dos testes em [`parsed_data/validacao.md`](parsed_data/validacao.md).

## 1. Escopo

- **Subprogramas:** 15-17 a 23-25 (9 triênios). O 14-16 é extraído, mas excluído das tabelas finais pelo script `remove_14-16.py` do grupo (seção 4). O motivo: não há edital de abertura (vagas), nem convocações com cota, nem resultados do PAS 1 e do PAS 2.
- **Cursos de computação analisados:** Ciência da Computação (bacharelado), Computação (licenciatura) e Engenharia de Computação. Engenharia de Software saiu do escopo porque o PAS não oferece vaga própria para ela: ela está dentro da entrada comum "Engenharias: Aeroespacial/Automotiva/Eletrônica/Energia/Software" do campus Gama (script `remove_eng_software.py`, seção 4).
- **Todos os cursos** continuam nas tabelas, para comparações como a F7.

## 2. Fontes

Os arquivos ficam em `raw_data/<subprograma>/`. As regras de cada edital de abertura estão resumidas em [`raw_data/regulamentos.md`](raw_data/regulamentos.md).

| Tipo de edital | Pasta | Usado para |
|---|---|---|
| Resultado final do PAS 3 (e `SJ*`) | `PAS3/Resultado_final/` | Notas das 3 etapas, argumento final, curso e classificação em cada categoria |
| Resultado final do PAS 1 e PAS 2 (e retificações) | `PAS1/` e `PAS2/Resultado_final/` | Comparecimento e notas de quem não chegou ao PAS 3; validação V3 |
| Convocação para registro acadêmico | `PAS3/Convocacao_para_registro_academico/` | Aprovação, chamada, semestre e categoria da vaga |
| Relação das pessoas selecionadas | `PAS3/Relacao_das_pessoas_selecionadas/` | Registro acadêmico homologado |
| Edital de abertura | `PAS3/Edital_de_abertura/` | Quadro de vagas por curso, semestre e categoria |
| Média e desvio padrão | `media_e_desvio_padrao.pdf` e fim do resultado final | Validação V4 |

## 3. Como rodar

```bash
pip install pypdf          # e o pdftotext (poppler-utils), usado só na validação V2
python3 scripts/pas/run_all.py
```

O `run_all.py` executa, em ordem:
1. `build_tables.py`, que extrai os dados e grava `tabela1_alunos.csv`, `tabela2_curso_cota.csv`, `subprogramas.csv` e `intermediarios/`;
2. `alteracoes_de_pipeline/remove_14-16.py`, que gera os arquivos `*_sem_14_16.csv`;
3. `alteracoes_de_pipeline/remove_eng_software.py`, que gera os arquivos `*_sem_eng_soft.csv`;
4. `validate.py`, que gera `parsed_data/validacao.md`.

**As tabelas do artigo são as `*_sem_eng_soft.csv`.** O texto extraído de cada PDF fica em cache em `.cache/pdf_text/`, que não vai para o repositório.

## 4. Filtros do grupo (`scripts/pas/alteracoes_de_pipeline/`)

| Script | Entrada | Saída | O que faz |
|---|---|---|---|
| `remove_14-16.py` | `tabela1_alunos.csv`, `tabela2_curso_cota.csv`, `subprogramas.csv` | `*_sem_14_16.csv` | Remove todas as linhas do subprograma 14-16: 7.343 candidatos, 166 células e 1 subprograma |
| `remove_eng_software.py` | `*_sem_14_16.csv` | `*_sem_eng_soft.csv` | Apaga a marcação `ENGENHARIAS_FGA_SOFTWARE` da coluna `area_computacao`. As linhas continuam, porque são vagas e candidatos reais |

## 5. Pipeline de extração (`scripts/pas/`)

| Módulo | O que faz |
|---|---|
| `common.py` | Leitura dos PDFs com `pypdf`, cache, normalização de texto e anonimização |
| `cotas.py` | Vocabulário padronizado das 10 categorias, lido da descrição de cada edital |
| `resultado_pas3.py` | Resultado final do PAS 3, incluindo subseções e editais sub judice |
| `resultado_pas12.py` | Resultados do PAS 1 e PAS 2, com as retificações aplicadas |
| `convocacoes.py` | Convocações (por código de legenda ou por classificação) e relações de selecionados |
| `vagas.py` | Quadro de vagas dos editais de abertura |
| `build_tables.py` | Correspondência de nomes de curso e montagem das tabelas |
| `validate.py` | Testes V1 a V13 |
| `run_all.py` | Executa tudo na ordem certa |

### Decisões de extração

- **O texto do pypdf quebra números e palavras** (`27. 213`, `Sistema Universa l`, sinal negativo numa linha e o número na outra). As linhas são unidas sem inserir espaço, e os espaços dentro dos campos numéricos são removidos.
- **O mapa de categorias não é fixo.** A lista é lida da frase "na seguinte ordem: …" de cada resultado e da legenda (1)–(10) de cada convocação. Ela muda ao longo da década:
  - o `14-16` não tem as categorias PcD;
  - a partir do `22-24`, a renda passa de 1,5 para 1 SM e quilombolas entram no nível PPI.
- **Rótulos padronizados:** `SU`, `NEG`, `EP_<renda>_<raça>[_PCD]`. `R1` é a renda até o limite e `R2`, acima dele.
- **Chave do aluno.** A inscrição se mantém nas 3 etapas e liga os editais entre si. Na saída ela vira `id_aluno`, um SHA-256 com sal da inscrição e do subprograma, e **nenhum nome é gravado nos CSVs**.
- **Sub judice.** Os candidatos em subseções ou editais `SJ*` ficam com `sub_judice = True`. Quando um edital SJ retifica as notas de um candidato, a retificação substitui o registro original.
- **Retificações do PAS 1 e PAS 2** são aplicadas em ordem. Uma nota provisória nunca substitui uma final.
- **Ordem das colunas do quadro de vagas.** É deduzida dos rótulos do cabeçalho de cada edital (três arranjos diferentes). A coluna de total aparece no início ou no fim. A dedução é validada em V10.
- **Nome canônico do curso.** Os editais do mesmo subprograma escrevem o mesmo curso de formas diferentes. O nome do quadro de vagas é o canônico, e cada nome do resultado e da convocação é casado com ele (seção 6.4). Todas as decisões ficam em `intermediarios/correspondencia_cursos.csv`.
- **Curso do candidato.** Sem SISUnB (de 17-19 em diante), o curso é o da inscrição, publicado no resultado final, e as convocações são posicionadas nesse curso. Nos anos com SISUnB (15-17 e 16-18), vale o curso da convocação, e `curso_mudou_sisunb` registra a troca.

## 6. Correções feitas na validação final

Cada correção abaixo foi encontrada por um teste da seção 7, que agora passa.

### 6.1 Cabeçalhos de curso sem parênteses (pares fora de ordem)

- **Sintoma.** A classificação no Universal saía fora da ordem do argumento final em 136, 82, 62, 212, 18, 38, 32, 36, 28 e 0 pares (14-16 a 23-25).
- **Causa.** O extrator só reconhecia como curso o cabeçalho com parênteses. Cabeçalhos como "BACHARELADO EM QUÍMICA", "LICENCIATURA EM FÍSICA", "LICENCIATURA EM ARTES CÊNICAS*" e "CIÊNCIAS SOCIAIS – ANTROPOLOGIA/SOCIOLOGIA BACHARELADO/LICENCIATURA" eram ignorados. Os candidatos desses cursos iam para o curso anterior no PDF. Por exemplo, os 117 alunos de Ciências Sociais iam para Ciências Econômicas, que ficava com 282 candidatos e classificações repetidas.
- **Evidência.** Em todos os cursos afetados, a ordem alfabética recomeça no meio do "curso" e a classificação no Universal se repete (dois candidatos com posição 1).
- **Solução.** `resultado_pas3._header_kind` e `convocacoes._marker_kind` passam a tratar como curso o cabeçalho com "BACHAREL" ou "LICENCIA". Também foi tratado o caso da subseção sub judice com o nome cortado ("TECNOLÓGICA (BACHARELADO) - SUB JUDICE" logo depois de "QUÍMICA TECNOLÓGICA").
- **Efeito.** 1.339 candidatos mudaram para o curso correto. Notas, aprovação e cota não mudaram, e nenhum curso de computação foi afetado. **V5 passou a 0 pares fora de ordem e 0 classificações repetidas nos 10 subprogramas.** O que sobra são de 1 a 13 empates exatos de argumento final por ano, desempatados pelos critérios do Edital nº 1, que não está no repositório.

### 6.2 Turno ausente na chave da tabela 2

- **Sintoma.** V8 (nota de corte) passava em só 95% das células.
- **Causa.** A chave da tabela 2 era (campus, curso). Cursos que existem no diurno e no noturno do Darcy Ribeiro (Administração, Arquitetura, Ciências Contábeis etc.) eram somados numa célula só.
- **Solução.** A chave passou a ser (campus, turno, curso), com o turno usado no Darcy Ribeiro e em Planaltina, os únicos campi com o mesmo curso em dois turnos. A coluna `turno` foi adicionada à tabela 2.
- **Efeito.** V8 passou a 99,9%. Os cursos de computação têm um único turno e não foram afetados.

### 6.3 Último registro de cada bloco das convocações de 15-17

- **Sintoma.** V11 e V12 falhavam em 15-17: 882 homologados não apareciam como convocados.
- **Causa.** No formato de 15-17 (com classificação), o último registro de cada sistema termina com ponto ("Gabriele Dantas Gontijo, 2."), e a expressão regular rejeitava um número seguido de ponto.
- **Solução.** O número pode ser seguido de ponto, desde que não seja um decimal.
- **Efeito.** As convocações de 15-17 passaram de 3.800 para 4.682 candidatos. Homologados sem convocação: de 882 para 0.

### 6.4 Nomes de curso diferentes entre editais

- **Sintoma.** Células da tabela 2 com candidatos e sem vagas, ou com vagas e sem candidatos.
- **Causa.** Exemplos de grafias diferentes:
  - "LETRAS - PORTUGUÊS DO BRASIL COMO SEGUNDA LÍNGUA" × "LETRAS PORTUGUÊS DO BRASIL COMO SEG. LÍNGUA";
  - "LICENCIATURA EM MÚSICA" × "MÚSICA (LICENCIATURA)";
  - "PSICÓLOGO" × "PSI COLOGO";
  - "DIREITO (BACHARELADO)/ CANDIDATOS SUB JUDICE";
  - em 23-25, convocações do campus Ceilândia num edital sem o cabeçalho do campus.
- **Solução (`build_tables.Canonico`).** Primeiro unifica as grafias dos quadros do 1º e do 2º semestre. Depois casa cada nome, no mesmo campus e turno, por esta ordem:
  1. nome igual;
  2. igual sem pontuação;
  3. mesmo conjunto de palavras;
  4. um único curso cujas palavras contêm as do nome, com semelhança ≥ 0,75.

  Se nada casar, procura o nome igual nos outros campi e só aceita uma opção única. Uma primeira versão por pura semelhança de caracteres foi descartada, porque casava "ARTES VISUAIS" com "ARTES CÊNICAS".
- **Efeito.** V13 tem 4 células órfãs em 16.954. Os cursos com vagas e sem candidatos são noturnos pequenos ou exigem certificação de habilidade (Música, Artes Visuais, Ciências Naturais).

### 6.5 Numeração das chamadas e semestre

- **15-17.** A 1ª chamada dos dois semestres é a "convocação geral" (Edital nº 38, de 27/1/2018). O arquivo `1_chamada_2_semestre.pdf` (Edital nº 46, de 20/6/2018) é a 2ª chamada do 2º semestre. A correção está em `convocacoes.CHAMADA_CORRIGIDA`.
- **23-25.** Os arquivos `3_`, `4_` e `5_chamada_2_semestre.pdf` eram, pelo texto, a 5ª (Edital nº 75), a 3ª (nº 64) e a 4ª chamada (nº 70). Eles foram **renomeados no repositório** para o número correto. Além disso, o extrator agora lê o número da chamada no próprio texto do edital ("em terceira chamada") e usa o nome do arquivo só como último recurso.
- **18-20.** As convocações são para o "quantitativo total das vagas", sem separar semestres, apesar do "_2_semestre" no nome do arquivo. Nesse subprograma, o semestre é `0` (ingresso único) e as vagas dos dois semestres são somadas na tabela 2.
- **Quadro de vagas das Engenharias do Gama.** Os números do 2º semestre estavam quebrados em duas linhas ("7" e "5 15 5…"), e a linha não era lida. Em 15-17 a 17-19, o total passou a 4.222, 4.222 e 4.232 vagas.

### 6.6 Convocações repetidas

O edital da 1ª chamada do 2º semestre de 21-23 publica duas vezes o bloco de Enfermagem do Darcy Ribeiro (20 linhas idênticas), e elas foram removidas. Editais SJ que só repetem a convocação de quem já tinha sido convocado (reenvio de documentos) marcam o registro como sub judice, sem criar uma nova convocação.

**Duplicatas no 16-18 (SISUnB).** Não há candidato convocado mais de uma vez nem em dois cursos. O repositório não mistura resultado provisório ou retificação de chamada com as convocações: só a 1ª e as chamadas seguintes de cada semestre. Os editais de chamadas posteriores trazem uma seção com a relação de quem não compareceu, e essa seção é ignorada. A troca de curso pelo SISUnB aparece em `curso_mudou_sisunb`: nenhum aprovado em 15-17 e 1 em 16-18, comparando o curso do resultado com o da convocação.

## 7. Validação (relatório completo em `parsed_data/validacao.md`)

Cada teste confronta fontes diferentes, para não validar um dado com ele mesmo. O resumo abaixo pode ser citado no artigo.

| Teste | O que confronta | Resultado | Critério |
|---|---|---|---|
| V1 Cobertura | Registros extraídos × inscrições no texto do PDF | 100% nos 9 resultados finais (o script antigo tinha 87%) | 100% |
| V2 Reextração independente | pypdf × pdftotext (poppler), 2.700 candidatos sorteados, 52.397 campos | 99,77% idênticos. Todas as divergências são falhas do poppler, conferidas no PDF (sinal "-" sozinho no fim da linha; número da página colado no valor). 0 sem explicação | ≥ 99,9% idênticos ou explicados |
| V3 Consistência entre editais | Notas das etapas 1 e 2 no resultado do PAS 3 × PDFs do PAS 1 e PAS 2 | ≥ 99,6% idênticas (o resto são retificações posteriores) | ≥ 99% |
| V4 Números oficiais | Média e DP da Parte II e da redação do PAS 3 × Cebraspe | Diferença máxima 0,005 | ≤ 0,005 |
| V5 Classificação × AF | Ordem da classificação em cada categoria × AF | 0 pares fora de ordem | 0 |
| V6 Elegibilidade | Categoria da convocação × classificação no resultado | 5 sem explicação em 36.685 (0,01%) | ≤ 0,05% |
| V7 Ninguém pulado | Candidatos melhor classificados que o último convocado e não convocados | 24 candidatos nos 9 anos (casos possíveis: heteroidentificação, avaliação biopsicossocial, sub judice) | ≈ 0 |
| V8 Nota de corte | AF do convocado com a pior classificação na célula × `nota_corte_ultima_chamada` | 99,9% das células | ≥ 99% |
| V9 Regime da cascata | Convocados por cota que, pela classificação, entrariam no Universal | 7% a 36% por ano até 21-23; **0% em 22-24 e 23-25** | > 0 antes e 0 depois da Lei 14.723 |
| V10 Quadro de vagas | Total geral do edital, linha de Ciência da Computação no PDF × CSV, regras da Lei 12.711 | Totais iguais; linha de CC idêntica nos 9 editais; a ordem usada cumpre a lei em 99% a 100% dos cursos e a ordem alternativa em 0% a 1% | ver relatório |
| V11 1ª chamada × vagas | Convocados × mín(vagas, candidatos), com a sequência dos semestres | 98% a 100% dos cursos | ≥ 95% |
| V12 Homologação | Homologados × convocados; duplicatas; SISUnB | 12 homologados sem convocação (7 em 19-21 e 5 em 22-24, 0,05% dos homologados), sem explicação nos PDFs do repositório; 0 duplicatas restantes | ≤ 1% |
| V13 Junção | Células com candidatos e sem vagas | 4 em 16.954 | ≤ 0,1% |

**Como interpretar o V9.** É a evidência mais forte de que as categorias de aprovação e de inscrição estão corretas. Os dados não usam a regra de preenchimento na construção das tabelas. Mesmo assim, reproduzem exatamente a quebra prevista pela Lei 14.723/2023:
- até 21-23, de 7% a 36% dos convocados por cota tinham classificação suficiente para entrar pelo Universal (cotas preenchidas primeiro);
- a partir de 22-24, nenhum (Universal preenchido primeiro).

**Nota de corte e as duas regras de preenchimento.** A `nota_corte_*` de cada célula é o menor AF entre os convocados naquela categoria. O V8 mostra que esse candidato é também o de pior classificação na categoria nas duas regras: das mais restritivas para as menos restritivas até 21-23, e o inverso a partir de 22-24.

## 8. Conferência das colunas contra os gráficos e os editais de regras

### Colunas adicionadas ao plano original

| Coluna | Para quê |
|---|---|
| `campus`, `turno` | O mesmo curso existe em campi e turnos diferentes |
| `curso_pdf` | Auditoria da correspondência de nomes |
| `nota_corte_1a_chamada` e `nota_corte_ultima_chamada` | A F5 precisa das duas |
| `area_computacao` | Filtra os cursos do artigo |
| `grupo_concorrencia` | Dá as 4 linhas da F1 |
| `sub_judice`, `faixa_renda_regra`, `curso_mudou_sisunb` | Permitem excluir ou controlar os casos que a regra trata de forma especial |
| `subprogramas.csv` | Datas das provas (eixo X da F1) e marcos regulatórios da RQ4 |

### Esclarecimentos (afetam a interpretação)

- **"Inscritos" são os não eliminados no PAS 3** com classificação na categoria. Os editais não publicam inscritos por curso nem eliminados.
- **O curso e a cota só aparecem no resultado do PAS 3.** Quem desistiu no PAS 1 ou no PAS 2 tem comparecimento e notas, mas não tem curso nem cota (limita a F9 e a continuidade por cota).
- **A cota de aprovação não é a cota de inscrição.** Use `sistema_inscricao` para o perfil e `cota_aprovacao` para a via de entrada.
- **"Comparecimento"** é a presença no resultado da etapa. Para os ausentes, não se distingue falta de eliminação.
- **18-20** tem ingresso único: semestre `0` na tabela 2.

### Lacunas dos dados

| Item | Situação |
|---|---|
| Edital de abertura do `14-16` | Não encontrado (Edital nº 21, de 6/9/2016). O 14-16 está fora do escopo |
| PAS 1 e PAS 2 do `14-16` e PAS 1 do `15-17` | Marcados como `sem_dados.txt` |
| Notas EB do PAS 1 e PAS 2 em `15-17` a `17-19` | Esses PDFs só têm tipo D e redação. Para quem chegou ao PAS 3, o EB vem do resultado do PAS 3 |
| Homologação do `16-18` | Não há relação no site (`nao_ha_dados_no_site_do_Cebraspe.txt`) |
| Convocados fora do resultado do PAS 3 | De 0 a 8 por ano (V6). Foram incluídos por editais de retificação ou SJ que não estão no repositório. Sem AF, ficam fora das notas de corte |
| Língua estrangeira de cada candidato | Não publicada. Impede recalcular o AF e comparar a média da Parte I |
| Critério de desempate | Está no Edital nº 1 de cada subprograma, que não está no repositório |

### O que retirar ou marcar como limitado no plano

- **"booleano de homologação":** existe para 15-17 e para 17-19 a 23-25. Não existe para 16-18.
- **T2 (simulação sem cotas):** viável com `argumento_final` e `sistema_inscricao`, mas não reproduz a migração de vagas. Deve ser apresentada como aproximação.
- **Engenharia de Software:** fora do escopo (seção 1).

## 9. Próximos passos

1. Gerar os gráficos e tabelas da Metodologia II a partir das tabelas `*_sem_eng_soft.csv`.
2. Obter os Editais nº 1 de cada subprograma (fórmula do argumento final e critério de desempate).
