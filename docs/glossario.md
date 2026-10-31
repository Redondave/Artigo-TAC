# Glossário das tabelas

Este glossário descreve cada coluna das tabelas em `parsed_data/`: o que ela mede, de qual documento vem, de que elemento do documento é tirada e, quando é calculada, a regra do cálculo. As decisões de extração e a validação estão em [`metodologia.md`](../metodologia.md).

**Tabelas do artigo:** `tabela1_alunos_sem_eng_soft.csv`, `tabela2_curso_cota_sem_eng_soft.csv` e `subprogramas_sem_eng_soft.csv`. Elas têm as mesmas colunas das tabelas sem sufixo, com dois filtros do grupo aplicados:
- `remove_14-16.py`: tira todas as linhas do subprograma 14-16;
- `remove_eng_software.py`: apaga `ENGENHARIAS_FGA_SOFTWARE` da coluna `area_computacao`, mantendo as linhas.

## Convenções

- **Célula vazia** = não se aplica ou não publicado. Nunca significa zero.
- **Booleanos:** `True` ou `False`.
- **Notas:** número com ponto decimal, 3 casas, como no PDF.
- **Documentos de origem:** sempre em `raw_data/<subprograma>/`.
  - "Resultado final PAS 3" = `PAS3/Resultado_final/resultado_final.pdf`, mais os arquivos `SJ*.pdf` da mesma pasta.
  - "Convocação" = `PAS3/Convocacao_para_registro_academico/<n>_chamada_<s>_semestre.pdf`.
  - "Quadro de vagas" = Anexo do `PAS3/Edital_de_abertura/edital_de_abertura.pdf`.
- **"Frase de ordem"** é a frase "…na seguinte ordem: …" que abre cada lista nos editais do Cebraspe. É ela que diz o significado de cada campo dos registros.

### Categorias de concorrência (sufixo `<cat>`)

| Rótulo | Significado | Elemento do documento |
|---|---|---|
| `SU` | Sistema Universal | "classificação final no Sistema Universal" (frase de ordem); código (1) da legenda da convocação; coluna "Sistema Universal" do quadro |
| `NEG` | Sistema de Cotas para Negros (política da UnB) | "classificação final no Sistema de Cotas para Negros"; código (2) |
| `EP_R1_PPI` | Escola pública, renda ≤ limite, PPI | item "renda … igual ou inferior a 1,5 [ou 1] salário mínimo … que se autodeclararam pretos, pardos ou indígenas [ou quilombolas]" |
| `EP_R1_PPI_PCD` | Idem, pessoa com deficiência | mesmo item, "e que concorrem como pessoas com deficiência" |
| `EP_R1_NPPI` | Escola pública, renda ≤ limite, não PPI | item "… que não se autodeclararam …" |
| `EP_R1_NPPI_PCD` | Idem, com deficiência | — |
| `EP_R2_PPI` | Escola pública, renda > limite, PPI | item "renda … superior a 1,5 [ou 1] salário mínimo …" |
| `EP_R2_PPI_PCD` | Idem, com deficiência | — |
| `EP_R2_NPPI` | Escola pública, renda > limite, não PPI | — |
| `EP_R2_NPPI_PCD` | Idem, com deficiência | — |

- **Limite de renda:** 1,5 salário mínimo per capita até 21-23; 1 SM a partir de 22-24 (Lei 14.723/2023).
- **PPI:** inclui quilombolas a partir de 22-24.
- **Leitura dos rótulos:** o rótulo é atribuído a partir das palavras do item, e não da posição: "igual ou inferior" vira `R1`, "não se autodeclararam" vira `NPPI`, "deficiência" vira `PCD` (`scripts/pas/cotas.py`).

## `tabela1_alunos*.csv`: uma linha por candidato e subprograma

Todo candidato que aparece em pelo menos um resultado final (PAS 1, PAS 2 ou PAS 3) do subprograma.

| Coluna | Tipo | Definição | Origem e elemento | Regra |
|---|---|---|---|---|
| `subprograma` | texto | Triênio, por exemplo `20-22` | Nome da pasta em `raw_data/` | — |
| `id_aluno` | texto (16 hex) | Identificador anônimo do candidato | 1º campo de cada registro (número de inscrição, que é o mesmo nas 3 etapas) | SHA-256 de `sal\|subprograma\|inscrição`, 16 primeiros caracteres. Nome e inscrição não são gravados |
| `campus` | texto | Campus do curso, com o nome do quadro de vagas | Cabeçalho "CAMPUS …" que antecede o bloco do curso no resultado final do PAS 3 | Nome canônico (ver `curso`) |
| `turno` | texto | `DIURNO`, `NOTURNO` ou vazio (campus de turno único) | Sufixo "– DIURNO/NOTURNO" do cabeçalho de campus | — |
| `curso` | texto | Curso em que o candidato concorreu, com o nome do quadro de vagas | Cabeçalho do curso no resultado final do PAS 3 | Casado com o nome do quadro de vagas (`build_tables.Canonico`). Vazio para quem não chegou ao PAS 3 |
| `curso_pdf` | texto | O mesmo curso com a grafia do resultado final | Cabeçalho do curso no resultado final | Só normalização de maiúsculas e acentos |
| `area_computacao` | texto | `CC_BACHARELADO`, `COMPUTACAO_LICENCIATURA`, `ENG_COMPUTACAO` ou vazio | Derivado de `curso` | Expressão regular sobre o nome. Nas tabelas `_sem_eng_soft`, `ENGENHARIAS_FGA_SOFTWARE` foi apagado |
| `compareceu_pas1` | booleano | O candidato está no resultado final da 1ª etapa | `PAS1/Resultado_final/resultado_final.pdf` (+ retificações) | Vazio quando o PDF da etapa não existe (`sem_dados.txt`) |
| `compareceu_pas2` | booleano | Idem, 2ª etapa | `PAS2/Resultado_final/…` | Idem |
| `compareceu_pas3` | booleano | Está no resultado final do PAS 3 (não eliminado na 3ª etapa) | Resultado final PAS 3 | — |
| `eb1_pas1`, `eb1_pas2`, `eb1_pas3` | número | Escore bruto da Parte I (língua estrangeira) na etapa N | Para quem está no PAS 3: campos 3, 6 e 9 do registro do resultado final PAS 3 ("escore bruto da parte 1 na primeira/segunda/terceira etapa"). Para os demais: 3º campo do registro do resultado da etapa | — |
| `eb2_pas1`, `eb2_pas2`, `eb2_pas3` | número | Escore bruto da Parte II (inclui os itens tipo D) | Campos 4, 7 e 10 do resultado final PAS 3; ou 4º campo do resultado da etapa | — |
| `nr_pas1`, `nr_pas2`, `nr_pas3` | número | Nota da redação (0 a 10) | Campos 5, 8 e 11 do resultado final PAS 3; ou último campo do resultado da etapa | — |
| `argumento_final` | número | Argumento final do PAS (padronizado; pode ser negativo) | Campo 12 do registro do resultado final PAS 3 ("argumento final") | — |
| `class_<cat>` | inteiro | Posição do candidato na categoria, dentro do curso | Campos 13 em diante do registro do resultado final PAS 3, na ordem da frase de ordem daquele edital; "-" = não concorre | Vazio = não concorre na categoria. O candidato de escola pública tem classificação na própria categoria e em todas as menos restritivas, além do Universal |
| `sistema_inscricao` | categoria | Categoria em que o candidato se inscreveu | Derivada de `class_<cat>` | A categoria mais restritiva com classificação. Ordem de restrição: renda (R1 antes de R2), depois raça (PPI antes de NPPI), depois deficiência (PCD antes da geral). Sem EP: `NEG` se tem classificação em NEG; senão `SU` |
| `grupo_concorrencia` | texto | `Universal`, `Negros`, `EP PPI`, `EP Não-PPI` | Derivado de `sistema_inscricao` | `cotas.GRUPO` (linhas da F1) |
| `aprovado` | booleano | Foi convocado para o registro acadêmico em alguma chamada | Convocações (todas as chamadas e semestres) e editais SJ de convocação | Inscrição presente em alguma convocação |
| `cota_aprovacao` | categoria | Categoria da vaga da primeira convocação | Código (1)–(10) ao lado do nome na convocação, traduzido pela legenda do próprio edital. Em 15-17: título do bloco ("SISTEMA DE COTAS PARA NEGROS"…) | Primeira convocação por (chamada, semestre). Vazio em convocações SJ |
| `chamada_aprovacao` | inteiro | Número da chamada da primeira convocação | Texto do edital ("em terceira chamada", "segunda convocação"); nome do arquivo como último recurso | 15-17: a convocação geral é a 1ª dos dois semestres; o `1_chamada_2_semestre.pdf` é a 2ª (ver metodologia, 6.5) |
| `semestre_aprovacao` | inteiro | 1, 2 ou 0 (ingresso único, 18-20) | Texto do edital ("vagas relativas ao segundo semestre"), nome do arquivo e, em 15-17, o título "PRIMEIRO/SEGUNDO SEMESTRE DE 2018" | — |
| `curso_aprovacao` | texto | Curso da primeira convocação | Cabeçalho do curso na convocação | Nome canônico. A partir de 17-19 é igual a `curso` (sem SISUnB) |
| `curso_mudou_sisunb` | booleano | Aprovado em curso diferente da pré-opção (SISUnB) | `curso` × `curso_aprovacao` | Só em 15-17 e 16-18 |
| `n_convocacoes` | inteiro | Número de convocações do candidato | Convocações | Depois da remoção de duplicatas |
| `homologado` | booleano | Registro acadêmico homologado | "Relação final das pessoas candidatas selecionadas … cujo registro acadêmico foi homologado" (`Relacao_das_pessoas_selecionadas/`); em 15-17, "resultado do pré-registro" | Vazio quando o subprograma não tem relação (16-18) |
| `sub_judice` | booleano | Candidato com situação decidida judicialmente | Subseção "Resultado final dos candidatos sub judice…" ou cabeçalho "– SUB JUDICE" do resultado final; editais `SJ*` | — |
| `faixa_renda_regra` | texto | Limite de renda vigente: `1,5 SM` ou `1 SM` | Frase de ordem do resultado final; Lei 14.723 a partir de 22-24 | — |

## `tabela2_curso_cota*.csv`: uma linha por subprograma × campus × turno × curso × semestre × categoria

Todos os cursos ofertados no PAS. Uma célula também existe quando há convocados e não há vagas publicadas (V13).

| Coluna | Tipo | Definição | Origem e elemento | Regra |
|---|---|---|---|---|
| `chave` | texto | `subprograma\|campus\|turno\|curso\|semestre\|categoria` | — | — |
| `subprograma`, `campus`, `turno`, `curso` | texto | Identificação do curso | Quadro de vagas (nome canônico) | `campus` sem o prefixo "CAMPUS UnB" e sem a sigla, por exemplo `DARCY RIBEIRO`, `CEILANDIA`, `GAMA` (a FGA virou FCTE em 2025) |
| `semestre` | inteiro | 1, 2, ou 0 (ingresso único em 18-20) | Título "QUADRO DE VAGAS 1º/2º SEMESTRE" | Em 18-20, vagas dos dois semestres somadas |
| `categoria` | categoria | Categoria de concorrência | — | — |
| `grupo_concorrencia` | texto | Agrupamento da categoria | — | `cotas.GRUPO` |
| `area_computacao` | texto | Como na tabela 1 | — | — |
| `vagas` | inteiro | Vagas ofertadas na categoria | Linha do curso no quadro de vagas, coluna da categoria | Ordem das colunas deduzida dos rótulos do cabeçalho de cada edital (validada em V10). Vazio = sem quadro de vagas para a célula |
| `inscritos` | inteiro | Candidatos não eliminados do curso com classificação na categoria | Resultado final PAS 3, campos `class_<cat>` | O mesmo valor nos dois semestres. Para `SU` = todos os candidatos do curso |
| `convocados` | inteiro | Convocações na categoria e no semestre, somando todas as chamadas | Convocações (código da categoria) | Depois da remoção de duplicatas. A categoria é a da vaga (após migrações), não a da inscrição |
| `convocados_1a_chamada` | inteiro | Idem, só na 1ª chamada | Convocações da 1ª chamada | — |
| `ultima_chamada` | inteiro | Maior chamada com convocado na célula | Convocações | — |
| `nota_corte_1a_chamada` | número | Menor argumento final entre os convocados da 1ª chamada na célula | `argumento_final` (tabela 1) dos convocados | Vale para as duas regras de preenchimento (V8, V9) |
| `nota_corte_ultima_chamada` | número | Menor argumento final entre todos os convocados da célula | Idem | É o AF do convocado com a pior classificação na categoria em 99,9% das células (V8) |

**Leitura das notas de corte por regime.**
- **Até 21-23:** as cotas eram preenchidas antes do Universal, das categorias mais restritivas para as menos restritivas. O corte de uma cota reflete os cotistas daquela categoria; o corte do Universal inclui cotistas não aproveitados na cota.
- **A partir de 22-24:** o Universal é preenchido primeiro, e as cotas vão da menos restritiva para a mais restritiva. Cotistas com nota alta entram pelo Universal (V9: 0% entram por cota), o que tende a baixar o corte das cotas.
- **Migração de vagas:** vagas não preenchidas numa categoria migram para outra do mesmo curso. Por isso `convocados` pode ser maior que `vagas` numa categoria e menor em outra.

## `subprogramas*.csv`: uma linha por subprograma

| Coluna | Definição | Origem |
|---|---|---|
| `subprograma` | Triênio | — |
| `data_prova_pas3` | Data de aplicação da prova da 3ª etapa | Cronograma do edital de abertura ([`raw_data/regulamentos.md`](../raw_data/regulamentos.md)) |
| `sisunb` | O candidato podia trocar de curso depois do resultado (até 16-18) | Edital de abertura, item do SISUnB |
| `lei_14723` | Vale a Lei 14.723/2023 (22-24 em diante) | Editais de abertura de 2024 e 2025, item 8.7 |
| `faixa_renda` | Limite de renda das cotas de escola pública | Frase de ordem do resultado final |
| `quilombola_no_nivel_ppi` | Quilombolas entram no nível PPI | Editais de 2024 e 2025 |
| `categorias_resultado` | Categorias publicadas no resultado final, na ordem do edital | Frase de ordem do resultado final |
| `candidatos_pas1`, `candidatos_pas2`, `candidatos_pas3` | Candidatos em cada resultado final | Contagem das inscrições extraídas |
| `convocados` | Candidatos convocados (únicos) | Convocações |
| `vagas` | Total de vagas do PAS no subprograma | Soma do quadro de vagas (igual ao "TOTAL GERAL" do edital, quando ele existe) |
| `tem_homologacao` | Há relação de homologados no repositório | — |

## `intermediarios/`

| Arquivo | Conteúdo |
|---|---|
| `convocacoes.csv` | Uma linha por convocação: `id_aluno`, campus, turno, curso (canônico), chamada, semestre, `cota` (código da legenda traduzido), `classificacao_cota` (só 15-17, onde o edital publica a posição), `sub_judice` e `arquivo` de origem |
| `relacoes_selecionados.csv` | Uma linha por candidato e relação: `tipo` (`homologado` ou `selecionado`), chamada, semestre e arquivo |
| `vagas.csv` | O quadro de vagas extraído: linha por curso e semestre, colunas por categoria e total |
| `correspondencia_cursos.csv` | Cada nome de curso que não era idêntico ao do quadro de vagas: nome no PDF, nome canônico escolhido, método (`sem pontuação`, `mesmas palavras`, `palavras contidas`, `outro campus/turno`, `sem correspondência`) e semelhança |
