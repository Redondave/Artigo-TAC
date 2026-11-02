# Análise das figuras F4, F5 e F6

Escopo: Ciência da Computação (bacharelado, diurno), Engenharia de Computação (diurno) e Computação (licenciatura, noturno), subprogramas 15-17 a 23-25. Engenharia de Software está fora do escopo porque o PAS não oferece vaga própria para ela. Os dados vêm das tabelas `*_sem_eng_soft.csv`, e os números abaixo estão nos arquivos `F4/F4_dados.csv`, `F5/F5_dados.csv` e `F6/F6_dados.csv`.

Scripts: `scripts/pas/graficos/f4_notas_corte.py`, `f5_gap_nota_corte.py` e `f6_representacao_cotistas.py`.

## Antes de ler: três cuidados

1. **O argumento final (AF) é relativo à coorte.** Ele soma z-escores (pesos 1, 2 e 3) calculados com a média e o desvio de cada prova naquele ano. Um corte maior num ano significa "mais acima da média dos candidatos daquele ano", e não "prova mais difícil" nem "candidatos melhores em termos absolutos". As comparações entre anos são de posição relativa.
2. **As células são pequenas.** Cada curso tem 20 vagas por semestre. As categorias de cota têm de 1 a 2 vagas cada, e por isso a nota de corte de uma cota é a nota de 1 a 4 pessoas por ano. Oscilações de dezenas de pontos de um ano para outro são esperadas e não devem ser lidas como tendência isolada. As categorias PcD (1 vaga, quase sempre vazia) ficam fora dos grupos na F4 e na F5.
3. **A licenciatura praticamente não tem concorrência.** Em 8 dos 9 anos, todos os candidatos que chegaram ao PAS 3 foram aprovados (de 27 a 48 candidatos para 46 vagas por ano). A exceção é 16-18, com 65 aprovados de 72 candidatos. A "nota de corte" ali é, em geral, só a nota do último candidato disponível.

## F4 — Evolução das notas de corte por sistema

**O que mostra.** Nota de corte da 1ª chamada do 1º semestre, por grupo. É o menor AF entre os convocados das categorias do grupo.

**Principais resultados**

| Curso | Grupo | 15-17 | 17-19 | 20-22 | 21-23 | 22-24 | 23-25 |
|---|---|---|---|---|---|---|---|
| CC | Universal | 95 | 94 | 139 | 144 | 139 | 136 |
| CC | Negros | 45 | 50 | 92 | 137 | 98 | 118 |
| CC | EP PPI | −20 | 12 | 12 | −8 | 11 | 0 |
| CC | EP Não-PPI | −17 | 4 | 20 | 9 | 67 | −38 |
| Eng. Comp. | Universal | 108 | 118 | 121 | 120 | 120 | 121 |
| Eng. Comp. | Negros | 107 | 143 | 45 | 47 | 120 | 71 |
| Eng. Comp. | EP PPI | −17 | 22 | 0 | 8 | −47 | −67 |

- **O corte do Universal subiu em CC.** Passou de cerca de 95 a 104 (15-17 a 17-19) para 136 a 144 (20-22 a 23-25), cerca de 40 pontos de AF a mais. Os candidatos aprovados em CC estão, em termos relativos, cada vez mais acima da média do PAS. Isso é compatível com o aumento da procura: de 138 candidatos em 15-17 para 336 a 423 a partir de 19-21, com as mesmas 40 vagas. Em Engenharia de Computação, o corte do Universal ficou estável, em torno de 120, desde 17-19.
- **Há uma distância persistente entre o Universal e as cotas de escola pública.** Em CC, os cortes de EP PPI e EP Não-PPI ficam entre −40 e +20 na maioria dos anos (as exceções são 18-20, com −75, e EP Não-PPI em 19-21 e 22-24, com 47 e 67), em geral de 100 a 140 pontos abaixo do Universal. A reserva de vagas é o que permite a entrada de candidatos de escola pública com AF próximo da média da coorte.
- **A cota para negros fica no meio, mais perto do Universal.** Em CC, o corte de Negros subiu de 45 a 50 (15-17 a 18-20) para 92 a 137 a partir de 20-22. Isso acompanha o Universal e indica concorrência crescente entre os candidatos negros. Em Engenharia de Computação, o corte de Negros oscila muito (de 45 a 143), porque há só 1 vaga por semestre.
- **Lei 14.723 (22-24 em diante).** Com o Universal preenchido primeiro, os cotistas com nota alta entram pela ampla concorrência, e a cota fica para os seguintes. O efeito esperado é a queda do corte das cotas, e ele aparece em Engenharia de Computação: EP PPI cai para −47 e −67, os menores valores da série. Em CC, o efeito não é claro (Negros cai de 137 para 98 e sobe para 118). Com 2 anos e células de 1 a 2 vagas, não dá para afirmar uma tendência.
- **Pandemia e fim do SISUnB.** Em 18-20 (prova em março de 2021, ingresso único com 40 vagas numa só seleção), todos os cortes de CC e Eng. Comp. caem, por exemplo Universal de CC em 78 e de Eng. Comp. em 76. O mais provável é que isso venha do ingresso único, que dobra o número de vagas preenchidas numa só chamada, e não necessariamente do desempenho na pandemia. O fim do SISUnB (17-19) não produz uma quebra visível no corte do Universal.

## F5 — Respiro da nota de corte (1ª chamada × último convocado)

**O que mostra.** Quanto a nota de corte cai entre a 1ª chamada do 1º semestre e o último convocado, somando todas as chamadas e o 2º semestre.

**Principais resultados (mediana do gap nos 9 anos, em pontos de AF)**

| Curso | Universal | Negros | EP PPI | EP Não-PPI |
|---|---|---|---|---|
| CC | 34 | 49 | 40 | 25 |
| Eng. Comp. | 38 | 82 | 48 | 20 |
| Licenciatura | 68 | 0 | 0 | 0 |

- **Há respiro em todos os grupos dos dois bacharelados**, de 20 a 80 pontos de AF na mediana. O último aprovado do ano tem um AF bem menor que o corte divulgado na 1ª chamada. A F4 mostra o corte de entrada e a F5 mostra quanto ele cede depois.
- **A cota para negros tem o maior respiro.** Em Eng. Comp., a queda chega a 82 pontos na mediana (com picos de 119 em 17-19 e 108 em 20-22). Em CC, chega a 129 em 21-23. Com 1 vaga por semestre, a desistência de um único convocado leva a vaga a um candidato bem mais abaixo na lista.
- **No Universal, o respiro é menor e mais estável** (de 30 a 40 pontos a partir de 19-21), por causa da lista longa de candidatos. Os valores altos de Eng. Comp. em 15-17 e 16-18 (122 e 162) são da época do SISUnB, quando a troca de curso depois do resultado gerava mais desistências e chamadas.
- **Na licenciatura**, o gap das cotas é zero: não há candidatos na lista de espera, e todos já são chamados na 1ª chamada. O gap do Universal (de 40 a 85 pontos) é o efeito das vagas de cota não preenchidas que migram para a ampla concorrência e são ocupadas por candidatos de AF menor.
- **Depois da Lei 14.723**, não aparece mudança sistemática no respiro.

## F6 — Representação dos cotistas entre candidatos e aprovados

**O que mostra.** Para cada curso e ano:
- a % de cotistas entre os candidatos (perfil de inscrição);
- a % de cotistas entre os aprovados;
- a % de aprovados que entraram por vaga de cota;
- e, como referência, a % de vagas reservadas (55% nos bacharelados e 56,5% na licenciatura).

**Principais resultados**

| Curso | Cotistas entre candidatos | Cotistas entre aprovados | Razão aprovados/candidatos |
|---|---|---|---|
| CC | 22% a 38% | 47% a 57% | 1,4 a 2,4 |
| Eng. Comp. | 21% a 41% | 32% a 58% | 1,1 a 2,2 |
| Licenciatura | 15% a 44% | igual aos candidatos (16-18: 29% × 28%) | 1,0 |

- **Nos bacharelados, os cotistas são minoria entre os candidatos e quase metade dos aprovados.** Em CC, eles são de 22% a 38% de quem chega ao PAS 3, mas de 47% a 57% dos aprovados, perto dos 55% de vagas reservadas. A reserva de vagas mais que dobra a presença dos cotistas entre os aprovados (razão de até 2,4 em 21-23 e 23-25). Sem ela, a F4 mostra que os cortes do Universal (de 95 a 144) ficariam muito acima dos AFs com que os cotistas são aprovados.
- **A proporção de cotistas entre os candidatos de CC cai desde 17-19** (38% → 22% em 23-25), enquanto a procura total cresce. O aumento da procura por CC vem principalmente de não cotistas. A política mantém a proporção entre os aprovados, mas a "demanda inicial" de cotistas não acompanha.
- **Em Engenharia de Computação, a representação melhora com o tempo.** Até 18-20, os cotistas aprovados ficavam entre 32% e 46%, abaixo da reserva, porque faltavam candidatos cotistas e as vagas migravam para o Universal. De 19-21 em diante, ficam entre 45% e 58%.
- **Na licenciatura, todos os candidatos são aprovados (exceto em 16-18).** A % de cotistas entre os aprovados é a mesma dos candidatos (de 15% a 44%) e fica sempre abaixo da reserva de 56,5%. As vagas reservadas sobram por falta de candidatos e migram para o Universal. Ali, o problema não é acesso, é demanda.
- **Lei 14.723.** A diferença entre "cotistas entre os aprovados" e "aprovados por vaga de cota" (cotistas que entram pelo Universal) é de 0 a 2 pontos antes da lei e de 2 a 3 pontos depois, em CC e Eng. Comp. Poucos cotistas alcançam o corte do Universal nesses cursos, então a mudança de regra quase não altera a proporção total de cotistas aprovados. Ela muda por qual vaga eles entram.

## Parágrafo sugerido para os Resultados

> Nos dois bacharelados, a nota de corte do Sistema Universal ficou entre 76 e 144 pontos de argumento final, com alta de cerca de 40 pontos em Ciência da Computação a partir de 20-22, acompanhando o crescimento da procura (de 138 para até 423 candidatos com as mesmas 40 vagas). Os cortes das cotas de escola pública ficaram de 100 a 140 pontos abaixo, perto da média da coorte, e a cota para negros ficou numa posição intermediária, aproximando-se do Universal nos anos recentes. As chamadas suplementares reduziram a nota do último aprovado em 20 a 80 pontos (mediana), com o maior recuo na cota para negros, que tem uma vaga por semestre. Embora os cotistas sejam de 21% a 41% dos candidatos que concluem o PAS nesses cursos, eles chegam a 45%–58% dos aprovados, perto dos 55% de vagas reservadas: a reserva praticamente dobra sua presença entre os ingressantes. Na licenciatura em Computação, a procura é menor que a oferta, quase todos os candidatos são aprovados e as vagas reservadas não preenchidas migram para a ampla concorrência. A Lei 14.723/2023 alterou a via de entrada (os cotistas com nota alta passam a ocupar vagas do Universal), mas, com dois anos observados e categorias de uma a duas vagas, não é possível afirmar mudanças nas notas de corte das cotas.

## Limitações a citar

- AF padronizado por coorte (comparações entre anos são de posição relativa).
- Células de cota com 1 a 2 vagas por semestre; os grupos EP agregam as duas faixas de renda.
- 18-20 com ingresso único (40 vagas numa só seleção) não é diretamente comparável aos outros anos na F4 e na F5.
- Na era do SISUnB (15-17 e 16-18), o número de candidatos por curso reflete a pré-opção, não a escolha final.
- "Aprovado" = convocado, não necessariamente matriculado.
