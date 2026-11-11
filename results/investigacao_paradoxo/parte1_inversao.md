# Parte 1 — Os cotistas superaram o Sistema Universal Estrito (SUE) na Computação?

Este documento testa, uma a uma, as explicações possíveis para as "ultrapassagens" das cotas sobre o SUE vistas nas Figuras 2 e 4 do artigo (F1 e F2 da Computação). Todas as tabelas saem dos CSVs desta pasta, gerados pelos scripts de `scripts/pas/investigacao/`.

## Como ler os números

- **Argumento Final (AF):** a nota final do PAS. É padronizada dentro de cada ano, então 0 quer dizer "na média dos candidatos daquele ano". Uma diferença de 10 pontos de AF corresponde a cerca de 1/5 de desvio-padrão.
- **SUE:** candidato que concorre só no Sistema Universal. **Cotas:** Negros, EP PPI e EP Não-PPI (EP = escola pública).
- **d de Cohen:** a diferença de médias medida em desvios-padrão. d > 0 quer dizer SUE à frente. As referências usuais são 0,2 (pequeno), 0,5 (médio) e 0,8 (grande).
- **Intervalo de confiança de 95% (IC 95%):** a faixa onde o valor verdadeiro provavelmente está. Se o IC contém o zero, os dados não permitem dizer quem está à frente.
- **p-valor:** a chance de ver uma diferença desse tamanho só por acaso, se na verdade não houvesse diferença nenhuma. Abaixo de 0,05 costuma-se dizer "significativo".
- **Mediana:** a nota do candidato do meio. Diferente da média, não é puxada por notas extremas.
- **Média aparada 5%:** a média depois de tirar os 5% de notas mais altas e os 5% mais baixas.
- **Quantis:** p10 é a nota abaixo da qual estão 10% dos candidatos, e assim por diante. p90 é a nota do grupo "de cima".

---

## 0. A base tem erros? (auditoria)

| Verificação | Resultado |
|---|---|
| Candidatos duplicados (`id_aluno` repetido) | **0** em 205.001 linhas |
| Cota declarada de todos os candidatos do PAS 3 | 75.992 de 75.992 (100%) |
| O resultado publica a classificação de todos nas categorias em que concorrem? | Sim. A classificação máxima de cada categoria bate com o número de candidatos dela, em todos os cursos e anos de Computação. Ou seja, não existe um cotista "fraco" que tenha ficado sem classificação na cota e tenha sido rotulado como SUE por engano. |
| O AF da base pode ser recalculado a partir das notas brutas (EB1, EB2, Redação das 3 etapas)? | Sim. Uma regressão do AF sobre as 9 notas brutas tem R² entre **0,9995 e 0,99997** em todos os subprogramas. As notas e o AF são coerentes entre si. |
| Os d de Cohen desta investigação reproduzem a F2 do artigo? | Sim, idênticos: UnB EP 0,690 → 0,208; Computação EP 0,334 → −0,056; Computação Negros −0,096. |
| Candidatos PcD inflando EP | Só 5 candidatos PcD em Computação em 2023-25. Sem eles, o d de EP passa de −0,056 para −0,040: nenhuma diferença. A hipótese do tempo adicional de prova fica descartada sem precisar de dados externos. |

**Conclusão da auditoria:** não foi encontrado erro na base que explique o fenômeno. A rotulagem das cotas, as notas e o AF estão consistentes.

---

## H1. N pequeno e outliers: a média está sendo puxada por alguns "gênios"?

### Resultado principal: no Argumento Final, o SUE fica à frente em 8 dos 9 anos

Diferença SUE − todas as cotas, em pontos de AF, nos 3 cursos de Computação juntos (`p1_testes_sue_vs_cotas.csv`):

| Subprograma | n SUE | n cotas | Dif. de médias (IC 95%) | Dif. de medianas | p (Welch) | p (Mann-Whitney) | d |
|---|---|---|---|---|---|---|---|
| 15-17 | 190 | 69 | +19,6 (+7,0 a +31,8) | +15,1 | 0,003 | 0,025 | 0,37 |
| 16-18 | 208 | 107 | +14,8 (+1,9 a +27,4) | −2,6 | 0,020 | 0,26 | 0,25 |
| 17-19 | 293 | 172 | +20,5 (+11,9 a +29,1) | +14,6 | <0,001 | 0,002 | 0,39 |
| 18-20 | 247 | 94 | +20,7 (+10,2 a +30,3) | +16,9 | <0,001 | 0,003 | 0,41 |
| 19-21 | 426 | 164 | +13,5 (+4,9 a +21,9) | +10,3 | 0,002 | 0,033 | 0,25 |
| 20-22 | 444 | 166 | +20,7 (+12,1 a +29,4) | +12,4 | <0,001 | <0,001 | 0,38 |
| 21-23 | 438 | 140 | +13,2 (+3,1 a +23,1) | +2,5 | 0,010 | 0,14 | 0,22 |
| 22-24 | 476 | 203 | +12,8 (+4,9 a +21,0) | +3,7 | 0,002 | 0,10 | 0,23 |
| **23-25** | 457 | 121 | **−3,9 (−13,6 a +6,0)** | −8,1 | **0,44** | 0,14 | **−0,07** |
| **Todos os anos** | 3.179 | 1.236 | **+14,7 (+11,6 a +17,9)** | +7,5 | <0,001 | <0,001 | **0,26** |

- O **único ano** em que a média das cotas fica acima da do SUE é **2023-25**. Mesmo nele, a diferença (−3,9 pontos) está dentro da margem de erro: o IC vai de −13,6 a +6,0 e p = 0,44. Estatisticamente, **é um empate**, não uma ultrapassagem.
- Com todos os anos juntos, o SUE está à frente por **14,7 pontos de AF** (d = 0,26), com p < 0,001.

### Média, mediana e média aparada contam a mesma história

Computação, todos os anos (`p1_descritivas.csv`):

| Grupo | n | Média | Mediana | Média aparada 5% | Desvio-padrão | p10 | p90 |
|---|---|---|---|---|---|---|---|
| SUE | 3.179 | 9,6 | −3,0 | 7,4 | **60,0** | −59,5 | **99,6** |
| Negros | 243 | −2,2 | −10,3 | −4,7 | 47,2 | −56,8 | 59,7 |
| EP PPI | 410 | −11,4 | −13,2 | −12,6 | 36,1 | −55,2 | 36,9 |
| EP Não-PPI | 583 | −1,9 | −9,6 | −4,5 | 46,3 | −56,6 | 61,1 |

- A média aparada fica perto da média em todos os grupos, ou seja, **não há alguns poucos "gênios" sustentando a média de ninguém**.
- O teste de "retirar os melhores" (`p1_retirar_topo.csv`) confirma isso. A ultrapassagem de 2023-25 resiste à retirada do melhor cotista. No caso de Negros, ela some ao retirar os dois melhores (de 28 candidatos), o que mostra quão frágil ela é.
- **O SUE é o grupo mais disperso:** desvio-padrão de 60, contra 36 a 47 nas cotas. O teste de Levene, que verifica se duas variâncias são iguais, dá p < 0,05 em quase todos os anos. O SUE tem ao mesmo tempo os melhores e uma cauda inferior grande. É isso que torna a média dele instável.

**Veredito H1:** o N pequeno das cotas (17 a 133 por grupo e ano) explica por que as médias oscilam tanto. Não há "gênios" isolados puxando a média. **A inversão no AF não é estatisticamente real em nenhum ano.**

---

## H2. Cauda inferior do SUE e viés de sobrevivência

### A diferença entre SUE e cotas existe só "no topo"

Diferença SUE − cotas em cada quantil, Computação, todos os anos (`p1_quantis_dif.csv`):

| Quantil | SUE | Cotas | SUE − Cotas | IC 95% |
|---|---|---|---|---|
| p10 (os 10% piores) | −59,5 | −56,4 | **−3,2** | −7,2 a −0,4 |
| p25 | −36,9 | −34,4 | −2,6 | −5,7 a +1,1 |
| p50 (mediana) | −3,0 | −10,5 | +7,5 | +4,0 a +11,0 |
| p75 | 50,8 | 17,2 | **+33,6** | +27,4 a +39,8 |
| p90 (os 10% melhores) | 99,6 | 53,9 | **+45,7** | +40,5 a +56,1 |

Este é o achado central da investigação:
- **Na metade de baixo, o SUE e os cotistas são iguais.** Nos 10% piores, os cotistas estão até um pouco à frente.
- **Toda a vantagem do SUE está na metade de cima:** quase 46 pontos no p90.

Outras medidas apontam na mesma direção:

| Computação, todos os anos | SUE | Negros | EP PPI | EP Não-PPI |
|---|---|---|---|---|
| % com AF > 100 (desempenho de excelência) | **10%** | 3% | 0% | 4% |
| % com AF < 0 (abaixo da média do ano) | 52% | 58% | 66% | 58% |
| % no quartil superior do próprio curso e ano (25% se fosse igual) | **29,6%** | 16,9% | 8,3% | 16,5% |

### Por que isso faz a média oscilar

- A média do SUE é a soma de dois mundos: uma "elite" grande (10% acima de 100) e uma cauda inferior tão grande quanto a das cotas.
- Na Computação, a **mediana** do candidato SUE é −3 (Ciência da Computação: −4,2), ou seja, **a média do ano**. Isso acontece apesar de a nota de corte do SUE em Ciência da Computação estar entre 136 e 144.
- Em cursos como Engenharia Elétrica, a mediana do SUE é 63 (`p1_seletividade_cursos.csv`). A Computação atrai, portanto, um SUE "aspiracional": muita gente com nota média que escolhe o curso sem chance real de passar. Depois do fim do SISUnB, escolher não custa nada.
- O número de candidatos SUE na Computação passou de 190–293 (até 17-19) para 426–476 (a partir de 19-21).

### Viés de sobrevivência nas etapas (o filtro do PAS 3)

- A cota e o curso só são declarados na inscrição do PAS 3. **Por isso não é possível medir a evasão por cota**: quem saiu no PAS 1 ou 2 não tem cota conhecida. Essa é uma limitação dos editais, não da base.
- O que dá para medir na UnB inteira é que quem desiste entre o PAS 2 e o PAS 3 tem nota bem menor (EB2 do PAS 2 de 15 a 20 pontos, contra 22 a 30 de quem fica; `p2_pandemia`). O filtro existe, mas atua sobre todos os grupos.
- Não há evidência de que ele seja mais forte nas cotas:
  - a mediana dos cotistas é menor que a do SUE;
  - a cauda inferior dos cotistas (p10) é igual à do SUE;
  - 58% a 66% dos cotistas estão abaixo da média do ano.

  Se só a "elite" dos cotistas chegasse ao PAS 3, nada disso aconteceria.

**Veredito H2:** confirmada em parte, e reformulada. O que achata a diferença não é um filtro que deixa só a elite dos cotistas. É **a cauda inferior grande do SUE na Computação**, que tem o mesmo tamanho da dos cotistas e anula, na média, a vantagem que o SUE tem no topo.

---

## H3. A cota para Negros se parece com a elite do SUE?

Teste de Kolmogorov-Smirnov (KS), que compara as distribuições inteiras: quanto maior a "distância", mais diferentes elas são (`p1_negros_ks.csv`).

| Computação, todos os anos | Distância KS | p | Mediana Negros | Mediana da referência |
|---|---|---|---|---|
| Negros × SUE | 0,124 | **0,002** (diferentes) | −10,3 | −3,0 |
| Negros × EP | 0,060 | **0,46** (indistinguíveis) | −10,3 | −10,7 |

- **A distribuição de notas da cota para Negros é estatisticamente igual à das cotas de escola pública e diferente da do SUE.** A hipótese do artigo de que a cota para Negros reúne uma "elite" por não exigir escola pública **não se confirma**.
- Ela é mais dispersa que EP PPI (dp 47 contra 36), mas no conjunto se comporta como EP.
- Em 2022-24 e 2023-25, a mediana de Negros sobe (+4,4), mas com 60 candidatos o teste não distingue Negros nem do SUE nem de EP (p = 0,29 e 0,23).

---

## H4. Licenciatura × bacharelados

Diferença SUE − todas as cotas, por curso, todos os anos:

| Curso | n cotas | Dif. de médias (IC 95%) | p | d |
|---|---|---|---|---|
| Ciência da Computação | 746 | +11,7 (+7,8 a +15,9) | <0,001 | 0,21 |
| Engenharia de Computação | 396 | +23,0 (+17,3 a +28,9) | <0,001 | 0,39 |
| Licenciatura em Computação | 94 | +10,7 (+3,9 a +17,7) | 0,002 | 0,32 |

Regressão do AF por grupo × curso, com controle do ano (`p1_regressao_curso.csv`):
- as diferenças da Licenciatura em relação a Ciência da Computação **não são significativas** (p = 0,61 a 0,85);
- as de Engenharia de Computação são maiores (o gap é cerca de 11 a 14 pontos maior, p = 0,02 e 0,002).

O que isso mostra:
- **A Licenciatura não é a origem do fenômeno.** Com todos os anos juntos, o SUE lidera também lá (d = 0,32).
- As "lideranças" de EP na Licenciatura aparecem só em anos com **5 a 13 cotistas** (por exemplo, 18-20 com n = 5 e 23-25 com n = 7). É exatamente o tamanho de amostra em que uma média oscila por acaso.
- **O curso que concentra a aproximação é Ciência da Computação.** É o único com diferença negativa em 2023-25: −15,2 pontos, d = −0,25, p entre 0,02 e 0,09 conforme o teste.
- Esse resultado é limítrofe. São 27 combinações curso × ano testadas, e com a correção para múltiplos testes (Bonferroni, que exige p < 0,002) **deixa de ser significativo**.
- Em Engenharia de Computação, o SUE está à frente em todos os anos (d de 0,29 a 0,64).

---

## H5. Fatores exógenos: Lei 14.723, flexibilização de 2022 e pandemia

### Lei 14.723/2023 (a partir de 22-24)
- **A lei não pode mudar as notas dos grupos comparados no artigo.** Ela muda a ordem de alocação das vagas, mas o grupo de cada candidato (`sistema_inscricao`) é a cota em que ele se inscreveu, que continua a mesma.
- **A "inversão" de 2023-25 já estava presente no PAS 1 e no PAS 2 dessa coorte**, provas feitas em 2023 e 2024, antes de a lei valer para ela (`p1_d_por_etapa_computacao.csv`):

| Coorte 23-25, Computação | EB2 PAS 1 | EB2 PAS 2 | EB2 PAS 3 | AF |
|---|---|---|---|---|
| d SUE × EP | 0,00 | −0,02 | −0,09 | −0,06 |
| d SUE × Negros | −0,12 | −0,13 | −0,09 | −0,10 |

- O efeito do teto de renda (1,5 → 1 salário mínimo) aparece na composição: as categorias R1 da Computação caem de 35 candidatos em 22-24 para 7 em 23-25. Mas a renda só move candidatos de R1 para R2 dentro de EP: **não muda a média de EP como um todo**.

### Flexibilização de 2022 (candidatos que já concluíram o ensino médio)
- Ela atinge as coortes 22-24 e 23-25. Em 22-24, porém, o gap da Computação é **normal** (d = 0,27 para EP, igual à média histórica). A flexibilização, sozinha, não explica 2023-25.
- O código do aluno inclui o subprograma, então não dá para seguir a mesma pessoa entre subprogramas e identificar os "veteranos". Isso fica registrado como limitação.

### Pandemia
- A diferença entre o gap da Computação e o gap da UnB não tem padrão nos anos de pandemia: varia de −0,15 a +0,12, todos dentro da margem de erro (`p1_did_computacao_unb.csv`).

### O que de fato mudou em 2023-25: quem se inscreveu em Ciência da Computação

Candidatos de Ciência da Computação por faixa de AF:

| | AF < −50 | −50 a 0 | 0 a 50 | 50 a 100 | > 100 | Total |
|---|---|---|---|---|---|---|
| Cotas 22-24 | 18 | 61 | 32 | 10 | 2 | 123 |
| Cotas 23-25 | 5 | 23 | 26 | 16 | 3 | 73 |
| SUE 22-24 | 51 | 104 | 65 | 34 | 30 | 284 |
| SUE 23-25 | 54 | 96 | 54 | 32 | 27 | 263 |

- **De 22-24 para 23-25, o número de cotistas abaixo da média do ano em Ciência da Computação caiu de 79 para 28.** O número de cotistas acima da média ficou igual (44 → 45).
- A distribuição do SUE não mudou.
- A média das cotas subiu porque **cerca de 50 cotistas com nota abaixo da média deixaram de escolher o curso**, não porque os cotistas melhoraram. É um efeito de composição de quem se inscreve.
- Os dados não dizem *por que* esses candidatos escolheram outro curso. Hipóteses possíveis:
  - a nota de corte alta de Ciência da Computação, divulgada a cada ano;
  - mudanças de renda por causa do novo teto;
  - outras escolhas de carreira.
- Essa queda é a mesma que aparece na F6: os cotistas passam de 38% para 22% dos candidatos de Ciência da Computação.

---

## H6. Melhora real ou ruído?

### As ultrapassagens das figuras F1 são as que o acaso produziria

São 243 comparações de médias nas figuras F1 da Computação (9 anos × 3 etapas × 3 provas × 3 grupos). A simulação abaixo supõe que a diferença verdadeira entre SUE e cada cota é **constante** (o valor médio da série, sempre a favor do SUE). Ela sorteia 10.000 vezes as médias com o erro de cada célula e conta quantas vezes a cota "ultrapassa" o SUE só por acaso (`p1_ultrapassagens_simulacao.csv`):

| Prova | Comparações | Ultrapassagens observadas | Esperadas só pelo acaso | Faixa de 90% do acaso | p |
|---|---|---|---|---|---|
| Todas | 243 | **47** | 42 | 33 a 51 | 0,22 |
| EB2 (peso de 83%) | 81 | **9** | 5,5 | 2 a 9 | 0,09 |
| Redação | 81 | **24** | 21 | 15 a 27 | 0,25 |

**As ultrapassagens vistas nos gráficos estão dentro do que o puro acaso produziria se o SUE tivesse sempre a mesma vantagem.** Elas não são evidência de inversão.

### Tendência do d (meta-regressão)

Uma reta ajustada aos d de cada ano, dando mais peso aos anos com mais candidatos (`p1_tendencia_d.csv`). A estatística I² diz quanto da variação entre os anos é real e não acaso (0% = tudo acaso).

| Escopo | Grupo | Anos | d médio | Inclinação por ano (p) | I² |
|---|---|---|---|---|---|
| UnB inteira | EP | 15-17 a 23-25 | 0,42 | **−0,058 (p < 0,001)** | 98% |
| UnB inteira | Negros | 15-17 a 23-25 | 0,35 | **−0,035 (p < 0,001)** | 84% |
| Computação | EP | 15-17 a 23-25 | 0,27 | −0,032 (p = 0,036) | 39% |
| Computação | EP | 15-17 a **22-24** | 0,31 | −0,012 (p = 0,50) | **0%** |
| Computação | Negros | 15-17 a 23-25 | 0,20 | −0,054 (p = 0,049) | 0% |
| Computação | Negros | 15-17 a **22-24** | 0,24 | −0,042 (p = 0,20) | 0% |

- **Na UnB inteira, a queda da desigualdade é real**, contínua e muito significativa.
- **Na Computação, de 15-17 a 22-24 o gap é constante** (cerca de 0,3 para EP): inclinação nula e I² = 0%. Toda a "tendência" vem de um único ano, 2023-25.
- Esse ano é, sim, atípico para EP: −0,06 contra a média anterior de 0,31, uma diferença de 3 erros-padrão (p = 0,002). Mas ele não é uma inversão, porque não é significativamente menor que zero. E a seção H5 mostra que a causa é a mudança de quem se inscreveu.

**Veredito H6:** não há tendência contínua de melhora dos cotistas da Computação. Há um gap estável de cerca de 0,3 desvio-padrão por oito anos e um ano atípico explicado por composição.

---

## H7 (hipótese nova). População × candidatos de um mesmo curso

A OCDE compara **populações inteiras**: todos os alunos de escolas públicas contra todos os de escolas privadas. O artigo compara **candidatos que escolheram o mesmo curso**. Testei se isso, por si só, reduz a distância (`p1_decomposicao_unb.csv`, `p1_gap_controlando_curso.csv`):

- A distância entre SUE e cotas **dentro de cada curso da UnB** (média ponderada de 46 a 82 cursos por ano) é praticamente igual à da UnB inteira: 0,44 contra 0,41 em todos os anos.
- A escolha de curso explica de 0% a 20% da distância, conforme o ano.
- A distância é **maior** nos cursos cujo SUE é mais forte: correlação de Spearman de +0,58 para EP e +0,67 para Negros, p < 0,001 (`p1_seletividade_vs_gap.csv`).
- **Ciência da Computação** tem um gap baixo (0,25, posição 29 de 58 cursos), porque o seu SUE tem mediana igual à média do ano. Engenharia de Computação tem 0,41, como os cursos de perfil parecido.

**Veredito H7:** o simples fato de comparar candidatos do mesmo curso não explica o fenômeno. O que diferencia Ciência da Computação é **o perfil do seu SUE** (H2): muito procurado, com uma parte grande de candidatos sem chance real, o que encolhe a média do grupo.

## H8 (hipótese nova). O SUE como categoria "padrão"

- Quem não declara cota cai no SUE. Isso inclui alunos de escola pública que não pediram a cota e qualquer candidato sem intenção real de ingresso.
- Desde o fim do SISUnB, o curso é escolhido antes de conhecer a nota, então não custa nada escolher o curso mais concorrido.
- Os dados mostram:
  - o SUE da Computação mais que dobrou (190 → 476);
  - a proporção do SUE abaixo da média do ano ficou entre 48% e 57% em todo o período;
  - o p10 do SUE desceu de −54 para −65.
- A composição real do SUE (escola privada ou pública sem cota) **não está nos editais**. Fica como limitação, e esse é o ponto que separa esta análise da comparação da OCDE.

---

## Síntese da Parte 1

| Hipótese | Resultado |
|---|---|
| Erro na base | **Descartado** (auditoria completa, AF recalculado com R² > 0,999) |
| N pequeno / outliers | N pequeno **explica a oscilação**; "gênios" isolados **não** |
| Cauda inferior do SUE | **Confirmada**: é o principal mecanismo |
| Filtro de sobrevivência só nos cotistas | **Não confirmado** (as caudas inferiores são iguais) |
| Negros = elite parecida com o SUE | **Refutada** (Negros é estatisticamente igual a EP) |
| Licenciatura como origem | **Refutada** (a aproximação vem de Ciência da Computação em 23-25) |
| Lei 14.723 | **Descartada como causa** (o efeito já existia no PAS 1 e não muda o grupo de inscrição) |
| Flexibilização 2022 | **Insuficiente** (22-24 tem gap normal) |
| Melhora contínua dos cotistas da Computação | **Não**: gap estável e um ano atípico |
| Ruído estatístico | **Sim**: as ultrapassagens das figuras estão dentro do esperado pelo acaso |
| PcD | **Descartado** (5 casos, sem efeito) |
