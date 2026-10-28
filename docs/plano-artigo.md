# Plano do Artigo

## Sumário

1. [Prompt para o próximo Claude](#1-prompt-para-o-próximo-claude)
2. [RQs](#2-rqs)
3. [Metodologia I — parsing correto dos dados que precisamos](#3-metodologia-i--parsing-correto-dos-dados-que-precisamos)
4. [Metodologia II — gráficos a serem feitos, dados que usam e como eles respondem às RQs](#4-metodologia-ii--gráficos-a-serem-feitos-dados-que-usam-e-como-eles-respondem-às-rqs)

---

## 1. Prompt para o próximo Claude

- Enviar artigo atual, repositório e o prompt abaixo
- Pedir pra ver se os dados necessários para a análise são mesmo os listados e ver se eles de fato estão disponíveis nos PDFs do repositório (manda ele pesquisar no site do Cebraspe pra ver se faltou algo e consultar os editais de regras). Se faltar algo, adicione ou pare a execução caso não seja possível adicionar e peça para a gente.
- Pedir pra ver se as tabelas CSV requisitadas têm todas as colunas necessárias pros gráficos, e ler os editais de regra pra ver se tem que adicionar/retirar/esclarecer alguma coluna
- Pedir para criar os scripts que formatem os dados no formato que falamos abaixo
- Pedir para conferir se os dados foram bem extraídos (talvez um script só pra ver isso)
- Pedir pra anotar tudo que foi feito em um `metodologia.md`

---

## 2. RQs

- **RQ1:** Como evoluíram o desempenho médio e a distância de desempenho dos candidatos a cursos de computação entre o Sistema Universal e os demais sistemas de cotas (argumento final, EB1, EB2, NR por etapa)?
- **RQ2:** Como evoluíram as notas de corte em geral e por sistema de cotas nos quatro cursos de computação da UnB?
- **RQ3:** Como evoluiu a demanda pelos quatro cursos, no total e por sistema de concorrência?
- **RQ4:** Como fatores exógenos se associam às mudanças observadas nas RQs de 1 a 3?

> **Obs:** modificar o artigo para podar tudo que foge a elas.

---

## 3. Metodologia I — parsing correto dos dados que precisamos

### Tabela 1: uma linha por aluno

Para todos os alunos, ter uma linha na tabela CSV que diz, com as colunas:

- chave do aluno anonimizada
- curso escolhido
- booleano de status por etapa (compareceu ou não)
- uma coluna por nota em cada etapa do PAS (EB1, EB2 e NR, 1 2 e 3)
- argumento final
- uma coluna para cada classificação nas cotas
- coluna para o sistema no qual o candidato de fato concorreu às vagas (talvez redundante com "cota em que foi aprovado")
- booleano de aprovação
- booleano de homologação (?)
- chamada em que foi aprovado
- semestre de aprovação
- cota em que foi aprovado

### Tabela 2: uma linha por subprograma × curso × semestre × categoria de cotas

Para cada subprogramaXcursoXsemestreXcategoria_de_cotas, uma linha na tabela CSV que diz, com as colunas:

- chave
- vagas
- número de inscritos
- notas de corte (calculada por meio dos dados acima)

> **Obs:** o ideal é extrair isso pra todos os cursos, não só os 4 analisados, para podermos estabelecer comparações dos 4 cursos com os demais.

---

## 4. Metodologia II — gráficos a serem feitos, dados que usam e como eles respondem às RQs

**Pacote de Gráficos e Tabelas — Propósitos**

### Atrelados à RQ1 (Desempenho e Distância de Desempenho)

#### Figura 1 (F1) — Evolução do Escore Bruto Médio por Componente

- **Estrutura:** 3 figuras separadas (uma para EB1, uma para EB2 e uma para Nota de Redação). Cada figura possui 3 painéis (PAS 1, PAS 2 e PAS 3), com o eixo X representando a data de aplicação da prova e 4 linhas de grupos de concorrência: Universal, Negros, Escola Pública PPI e Escola Pública Não-PPI.
- **O que responde:** Mostra se o desempenho médio em cada tipo de prova mudou ao longo do tempo entre os diferentes perfis de alunos.

#### Figura 2 (F2) — Evolução do Gap de Desempenho em Desvios Padrão (d de Cohen)

- **Estrutura:** Gráfico de linhas temporais medindo a distância exata em desvios padrão do Argumento Final e dos Escores Brutos (EB1, EB2, NR) entre os alunos de cotas de escola pública e o Sistema Universal.
- **O que responde:** Quantifica se a desigualdade/distância de desempenho nas provas de cada componente está aumentando ou diminuindo com os anos.

#### Figura 3 (F3) — Heatmap do Gap por Categoria de Cotas

- **Estrutura:** Matriz de calor (heatmap) cruzando as 10 categorias de concorrência com os 10 subprogramas.
- **O que responde:** Permite analisar pontualmente se alguma das 8 subcategorias específicas de escola pública destoa das demais, sem poluir os gráficos de linha principais.

#### Tabela 1 (T1) — Tabela Completa de Estatísticas Descritivas (Apêndice)

- **Estrutura:** Tabela completa com média, desvio padrão, mediana e n (número de candidatos) para cada combinação de prova, etapa e cota.

### Atrelados à RQ2 (Notas de Corte e Acesso aos Cursos)

#### Figura 4 (F4) — Evolução das Notas de Corte por Sistema nos 4 Cursos

- **Estrutura:** Séries temporais das notas de corte no Argumento Final (AF) para os quatro cursos analisados (Ciência da Computação Bacharelado e Licenciatura, Engenharia de Computação, Engenharia de Software), separadas por sistema de concorrência.
- **O que responde:** Revela como a exigência mínima para aprovação evoluiu em cada cota e curso.

#### Figura 5 (F5) — Gap da Nota de Corte (1º Semestre vs. Última Chamada)

- **Estrutura:** Gráfico de linhas ou barras mostrando a diferença entre a nota de corte do 1º semestre e a nota do último candidato convocado após todas as chamadas.
- **O que responde:** Avalia o nível de "respiro" ou queda da nota de corte ao longo das chamadas suplementares em cada cota.

#### Figura 6 (F6) — Representação Proporcional dos Cotistas nos Aprovados

- **Estrutura:** Comparativo de barras entre a porcentagem de cotistas que prestaram a prova e a porcentagem de cotistas efetivamente aprovados em cada curso.
- **O que responde:** Revela o grau de representatividade e acesso real dos cotistas em relação à demanda inicial.

#### Figura 7 (F7) — Ranking de Seletividade dos 4 Cursos na UnB

- **Estrutura:** Gráfico de posição relativa (percentil) em que os 4 cursos de TI se posicionam dentro do ranking geral de notas de corte de todos os cursos da UnB.
- **O que responde:** Mostra se os cursos de TI se tornaram proporcionalmente mais elitizados/concorridos em relação aos demais cursos da universidade.

#### Tabela 2 (T2) — Simulação de Aprovação Sem Cotas

- **Estrutura:** Ranquear todos os candidatos do subprograma apenas pelo Argumento Final geral (AF puro) e simular quantas vagas seriam ocupadas por cotistas sem a reserva de vagas.
- **O que responde:** Mede o impacto direto e o efeito protetivo da política de cotas na garantia de vagas.

### Atrelados à RQ3 (Demanda pelos Cursos de Computação)

#### Figura 8 (F8) — Concorrência Real (Candidatos por Vaga)

- **Estrutura:** Gráfico combinado com barras (total de inscritos e total de vagas) e linha (razão candidato/vaga) ao longo dos anos para os 4 cursos.
- **O que responde:** Responde de forma direta se houve um "boom" de procura pelos cursos de TI sem confundir aumento de inscrições com variação no número de vagas ofertadas.

#### Figura 9 (F9) — Composição dos Inscritos por Sistema de Concorrência

- **Estrutura:** Gráfico de área/porcentagem mostrando a distribuição dos candidatos inscritos por categoria de cota no momento da inscrição ao longo dos anos.
- **O que responde:** Mostra se o perfil demográfico dos interessados pelos cursos de TI mudou.

### Atrelados à RQ4 (Impacto Transversal de Eventos Exógenos)

#### Marcadores Visuais de Eventos (Inseridos nas Figuras F1, F4 e F8)

- **Estrutura:** Linhas/faixas verticais e marcadores de cor única aplicados diretamente sobre as séries temporais dos gráficos das RQs 1, 2 e 3 indicando os momentos exatos dos eventos (Pandemia, fim do SISUnB, flexibilização de 2022 e Lei 14.723).
- **O que responde:** Permite correlacionar visualmente e imediatamente se as quebras de tendência nas notas ou demandas coincidem com alterações regulatórias ou históricas.

#### Tabela 3 (T3) — Matriz de Hipóteses e Vereditos

- **Estrutura:** Tabela cruzando cada evento com seu observável esperado, métrica analisada e a conclusão do estudo (Sustentada, Não Sustentada ou Inconclusiva).

Para a RQ4: vamos respondê-la de acordo com essa tabela de hipóteses, que também resolve o "onde ficam as conclusões":

| Evento | Observável esperado | Métrica |
|---|---|---|
| Pandemia (provas aplicadas entre 2020 e 2022, incluindo as 3ªs etapas adiadas para jul/2021 e jan/2022) | Queda de comparecimento ou de EB nessas provas; mais desistência | EB em % do máximo por prova, comparecimento, continuidade |
| Fim do SISUnB (ingresso 2020) | Demanda inscrita passa a coincidir com a demanda final | Inscritos por curso na inscrição vs. no registro |
| Flexibilização de ago/2022 | Mais inscritos e coorte mais heterogênea | Inscritos, DP dos EB |
| Lei 14.723 e inversão da cascata (ago/2024) | Corte do Universal sobe, o das cotas desce, mais aprovados pela ampla concorrência | Corte por sistema, % aprovados por via |
| Popularização da IA | Crescimento de candidatos/vaga em TI | Candidatos/vaga (sem pretensão causal) |

---

Por último, vamos manter no artigo somente os gráficos úteis, mas vamos fazer todos primeiro antes de qualquer coisa para ver quais de fato são úteis ou não.
