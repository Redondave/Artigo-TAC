# Parte 2a — Revisão do texto do artigo contra os CSVs

Cada afirmação numérica ou interpretativa das Seções I a V foi conferida contra a base. As sugestões abaixo são **propostas** para o grupo decidir: nenhum texto de colega foi alterado. Os números vêm das tabelas desta pasta e das tabelas da F2 em `results/geral/` e `results/computacao/`.

Legenda: ✅ confere · ⚠️ confere, mas a redação exagera ou precisa de ressalva · ❌ não confere com os dados.

## Resumo, Introdução e Questões de Pesquisa

| Trecho | Situação | O que os dados mostram | Sugestão |
|---|---|---|---|
| "nos quatro cursos de computação" (resumo, RQ 2 e RQ 3) | ❌ | O escopo tem **três** cursos. Engenharia de Software foi excluída, como diz a Metodologia. | Trocar "quatro" por "três". |

## Seção II-C — Fatores exógenos

| Trecho | Situação | O que os dados mostram | Sugestão |
|---|---|---|---|
| PAS 3 de 2018–2020 "remarcado para março de 2021 [...] aplicado apenas em julho de 2021" | ⚠️ conferir | O edital usado na base (Edital nº 19, de 10/12/2020) marca o PAS 3 para **7/3/2021**. A base não tem registro de uma reaplicação em julho. | Confirmar a data efetiva no acervo do Cebraspe antes de manter "julho de 2021". |
| SISUnB vigente de 2016 a 2019 | ✅ | O SISUnB vale para 15-17 e 16-18 (ingressos de 2018 e 2019) e acaba a partir de 17-19. | — |
| Teto de renda de 1,5 → 1 SM a partir de 22-24 | ✅ | `subprogramas.csv`: o teto de 1 SM vale para 22-24 e 23-25. | — |

## Seção V-A — Evolução do desempenho (F1)

| Trecho | Situação | O que os dados mostram | Sugestão |
|---|---|---|---|
| UnB: "SUE no topo, seguido pelo EP Não-PPI e pela cota para Negros [...] por fim, pelo EP PPI" | ⚠️ | Vale até 20-22. **De 21-23 em diante, EP PPI fica à frente de EP Não-PPI** no AF (21-23: −11,5 contra −12,3; 22-24: −8,8 contra −11,0; 23-25: −7,0 contra −7,8) e no EB2 do PAS 3 (21-23: 24,3 contra 23,8; 22-24: 30,0 contra 28,8; 23-25: 29,1 contra 28,5). | "[...] e, até 2020–2022, pelo EP PPI, que nos subprogramas recentes passa a superar o EP Não-PPI." Isso converge com a F3, onde as categorias PPI têm a maior queda do d. |
| "resiliência das notas gerais durante a pandemia" | ⚠️ | Ver `parte2_pandemia.md`: as médias brutas ficaram na faixa normal, mas no PAS 3 de 18-20 só 28% dos candidatos do PAS 2 compareceram (contra cerca de 52% nos outros anos). | Acrescentar a ressalva da seleção dos participantes e de que médias brutas de anos diferentes não medem o nível absoluto. |
| Computação: "No PAS 1 do subprograma 2021–2023, a categoria **EP Não-PPI** registrou a maior média absoluta" | ❌ | No EB2 do PAS 1 de 21-23 quem tem a maior média é **EP PPI** (25,7, com n = 36). O SUE tem 23,8 e o **EP Não-PPI tem a menor**, 20,0. | Trocar por "EP PPI" e citar o n: "(n = 36)". |
| "No PAS 3 de 2022–2024, a cota para Negros superou o SUE de forma inédita" | ⚠️ | Correto, mas por 0,18 ponto (33,78 contra 33,60; d = −0,01). É um empate. | "[...] a cota para Negros igualou o SUE (diferença inferior a 0,2 ponto) [...]". |
| "No último subprograma, a média do SUE no EB2 terminou em posições inferiores ou equiparáveis [...] sugerindo uma **expressiva elevação** no nível competitivo dos candidatos cotistas" | ❌ na interpretação | As médias conferem (EP Não-PPI 34,8; Negros 33,9; SUE 32,5). Mas a "elevação" **não é uma melhora dos cotistas**: em Ciência da Computação, o número de cotistas abaixo da média do ano caiu de 79 para 28, enquanto o de cotistas acima da média ficou igual (44 → 45). Ver `parte1_inversao.md`, H5. | "[...] o que se deve sobretudo à redução do número de candidatos cotistas com desempenho abaixo da média, e não a uma elevação do desempenho dos cotistas que já disputavam o curso." |
| Hipótese da "composição heterogênea" da cota para Negros (sem exigência de escola pública) | ❌ | A distribuição de notas de Negros na Computação é **estatisticamente igual à de EP** (teste KS, p = 0,46) e diferente da do SUE (p = 0,002). | Retirar a hipótese ou dizer que ela não se confirmou: "a distribuição de notas da cota para Negros é estatisticamente indistinguível da de Escola Pública". |
| Licenciatura: "alta variância intra-grupo, com lideranças frequentes das categorias de escola pública sobre o SUE" | ⚠️ | Com todos os anos juntos, o SUE lidera também na Licenciatura (diferença de +10,7 pontos de AF, p = 0,002). As "lideranças" ocorrem em anos com 5 a 13 cotistas (18-20: n = 5; 23-25: n = 7). | "[...] apresenta lideranças pontuais das categorias de escola pública, restritas a anos com menos de 15 cotistas e, portanto, compatíveis com flutuação amostral." |

## Seção V-B — d de Cohen (F2)

| Trecho | Situação | O que os dados mostram | Sugestão |
|---|---|---|---|
| UnB: EP 0,69 → 0,21; Negros 0,45 → 0,23 | ✅ | Reproduzido exatamente. | — |
| UnB: "em nenhum dos nove subprogramas o IC do AF incluiu o zero" | ✅ | O menor limite inferior é 0,036 (Negros, 22-24). | — |
| UnB: "redução contínua" | ✅ | A meta-regressão confirma: −0,058 por ano para EP (p < 0,001). | Dá para citar a inclinação como reforço. |
| Computação: EP parte de 0,33 e cai para −0,06; Negros chega a −0,10 | ✅ | Reproduzido exatamente. | — |
| "Nesses subprogramas recentes, o intervalo de confiança **finalmente** engloba e ultrapassa a linha do zero" | ❌ | Para Negros, o IC contém o zero **em todos os 9 anos** (limites inferiores de −0,02 a −0,48). Para EP, já continha em 16-18 (−0,002). | "Para Negros, o IC inclui o zero em toda a série, por causa do n reduzido; para EP, volta a incluí-lo em 2023–2025." |
| "indicando a diluição da vantagem técnica do SUE" | ⚠️ | O d de 2023-25 é estatisticamente igual a zero (IC −0,28 a +0,17), mas também é **atípico** em relação aos anos anteriores (3 erros-padrão abaixo da média de 0,31, p = 0,002). De 15-17 a 22-24, o gap da Computação foi **constante** (inclinação nula, I² = 0%). | "[...] o gap, estável em torno de 0,3 desvio-padrão de 2015–2017 a 2022–2024, torna-se estatisticamente nulo em 2023–2025." |
| "essa inversão é impulsionada majoritariamente por CIC" | ✅ com ressalva | Ciência da Computação em 23-25: d = −0,25 (p entre 0,02 e 0,09, conforme o teste); Engenharia de Computação: d = +0,34. Corrigido para múltiplos testes, nem o resultado de Ciência da Computação é significativo. | Evitar "inversão"; usar "aproximação" ou "anulação do gap". |
| "a superação técnica já se manifestava nas etapas 1 e 2 [...] não é efeito direto do mecanismo da prova recente" | ✅ (com troca de palavra) | d da coorte 23-25 para EP no EB2: PAS 1 = 0,00; PAS 2 = −0,02. É um **empate** desde o PAS 1, e isso de fato descarta a Lei 14.723 como causa. | Trocar "superação" por "equiparação". Acrescentar: "a Lei nº 14.723/2023 altera a alocação das vagas, mas não o grupo de inscrição dos candidatos, e por isso não pode alterar essas médias". |

## Seção V-C — Mapas de calor (F3)

| Trecho | Situação | Observação |
|---|---|---|
| UnB: EP R2 PPI 0,76 e EP R1 PPI 0,68 em 15-17; EP R1 Não-PPI de 455 para 144 | ✅ | As contagens conferem: 455 em 21-23 e 144 em 23-25. |
| Computação: Negros −0,10 (n = 28); EP R2 Não-PPI −0,10 (n = 66); EP R2 PPI 0,11 (n = 16); R1 de 35 para 7; R2 Não-PPI com cerca de 70% dos EP | ✅ | 66 de 93 = 71%. |

## Seção V-D — Seletividade (F7)

| Trecho | Situação | O que os dados mostram | Sugestão |
|---|---|---|---|
| Licenciatura "muito concorrida na categoria de EP/PPI" | ❌ | Na Licenciatura, quase todos os candidatos são aprovados (F4 e F6). Em 8 de 9 anos, 100% dos que chegaram ao PAS 3 foram aprovados. A posição alta da "nota de corte" de EP PPI no ranking reflete a nota do último candidato disponível, não a concorrência. | "[...] a posição da nota de corte de EP PPI da Licenciatura no ranking é alta, mas não decorre de concorrência: como a procura é inferior à oferta, o corte corresponde à nota do último candidato disponível (Seção V-G)." |

## Seção V-E — Candidatos por vaga (F8)

| Trecho | Situação | O que os dados mostram | Sugestão |
|---|---|---|---|
| "estudantes [...] de cotas [...] têm diminuído em número, o que mostra uma certa **seletividade maior** nas categorias de cotas" | ❌ | Menos candidatos por vaga significa **menos** concorrência, não mais seletividade. Com menos candidatos que vagas, todos são aprovados. | "[...] a redução do número de cotistas inscritos diminui a concorrência nessas categorias, e as vagas reservadas não preenchidas migram para a ampla concorrência (Seção V-I)." |
| "queda abrupta na admissão de todos os cursos no subprograma de 2020" | ⚠️ | Correto para o subprograma **2018–2020** (prova em 2021): 5.954 presentes no PAS 3 e 2.902 convocados, contra cerca de 9.900 e 4.300 no ano anterior. "Subprograma de 2020" é ambíguo. | Escrever "no subprograma 2018–2020". |

## Seção V-F — Composição dos inscritos (F9)

| Trecho | Situação | O que os dados mostram | Sugestão |
|---|---|---|---|
| "crescimento dos alunos **ingressantes** pelo Sistema Universal" | ❌ | A F9 mostra a composição dos **inscritos**, não dos ingressantes. Entre os aprovados, os cotistas continuam com cerca de 50% em Ciência da Computação (F6). | Trocar "ingressantes" por "inscritos". |
| "denota uma certa ineficiência do sistema em alavancar o acesso" | ⚠️ contradiz a F6 | A F6 mostra que a reserva **mantém** cerca de 50% de cotistas entre os aprovados dos bacharelados e mais que dobra a presença deles em relação aos inscritos. O que cai é a **procura**, não o acesso. | "[...] o sistema mantém a representação dos cotistas entre os aprovados (Seção V-I), mas não amplia a sua participação na demanda inicial, que se concentra no Sistema Universal." |

## Seções V-G a V-I (F4, F5, F6)

Conferidas anteriormente contra `F4_dados.csv`, `F5_dados.csv` e `F6_dados.csv`. ✅

Uma sugestão: a F4 reforça o argumento central desta investigação. A nota de corte do SUE em Ciência da Computação (136 a 144) fica 100 a 140 pontos acima das cotas, e isso é coerente com a vantagem do SUE **no topo** da distribuição (p90 do SUE ≈ 100 contra ≈ 54 nas cotas).

## Nova subseção sugerida para a Seção V-B (texto pronto, sem novas referências)

> **Robustez da aproximação na Computação.** Para verificar se a anulação do gap em 2023–2025 representa uma mudança real, as diferenças foram reavaliadas com estatísticas robustas (mediana, média aparada a 5\% e testes de Mann-Whitney e de permutação). No conjunto da série, o SUE mantém vantagem de 14,7 pontos de AF sobre os cotistas da Computação (IC 95\%: 11,6 a 17,9; $d = 0{,}26$), e a diferença em 2023–2025 ($-3{,}9$ pontos; IC 95\%: $-13{,}6$ a $6{,}0$) não é estatisticamente distinguível de zero. A decomposição por quantis mostra que essa vantagem se concentra na parte superior da distribuição: nos 10\% melhores, o SUE supera os cotistas em 46 pontos, enquanto na metade inferior as distribuições são equivalentes. Assim, as ultrapassagens observadas nas médias decorrem da grande dispersão do SUE na Computação, cuja mediana coincide com a média da coorte, apesar de a nota de corte superar 130 pontos. Uma simulação com gap constante reproduz o número de ultrapassagens observado nas Figuras 1 e 2 (47 em 243 comparações, contra 42 esperadas pelo acaso). Por fim, a aproximação de 2023–2025 em Ciência da Computação coincide com a redução do número de cotistas inscritos com AF abaixo da média da coorte (de 79 para 28), sem alteração no número de cotistas acima dela, o que indica uma mudança na composição da demanda, e não no desempenho dos cotistas.
