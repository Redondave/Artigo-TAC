# Relatório de validação dos dados

Gerado por `scripts/pas/validate.py` sobre as tabelas finais do artigo (`tabela1_alunos_sem_eng_soft.csv` e `tabela2_curso_cota_sem_eng_soft.csv`; subprogramas 15-17 a 23-25). Cada teste compara fontes diferentes; os critérios de aceitação estão declarados no resumo. Candidatos são identificados só pelo `id_aluno` anonimizado.

## Resumo

| Teste | Resultado | Critério | Situação |
|---|---|---|---|
| V1 cobertura do resultado final | mínimo 100.00% | 100% | OK |
| V2 reextração independente | 99.771% idênticos; 0 divergências sem explicação em 52397 campos | ≥ 99,9% idênticos ou explicados | OK |
| V3 notas iguais entre editais | mínimo 99.63% | ≥ 99% | OK |
| V4 médias e desvios oficiais (PAS 3) | maior diferença 0.005 | ≤ 0,005 | OK |
| V5 ordem classificação × AF | 0 pares fora de ordem, 0 repetidas | 0 | OK |
| V6 elegibilidade da cota de aprovação | 5 violações em 36685 convocações | ≤ 0,05% (sem explicação) | OK |
| V7 ninguém pulado | 24 candidatos | ≈ 0 (exceções explicáveis) | OK |
| V8 nota de corte coerente com a classificação | 99.90% das células | ≥ 99% | OK |
| V9 regime da cascata coerente com o edital | antes: > 0 em todos os anos; depois: 0 em 22-24 e 23-25 | > 0 antes e 0 depois da Lei 14.723 | OK |
| V10 quadro de vagas | ver tabela | totais iguais, CC idêntica, ordem usada ≥ 98% e alternativa < 50% | OK |
| V11 1ª chamada = mín(vagas, candidatos) | 15-17: 100%, 16-18: 100%, 17-19: 100%, 18-20: 100%, 19-21: 99%, 20-22: 98%, 21-23: 100%, 22-24: 100%, 23-25: 100% | ≥ 95% dos cursos com diferença ≤ 2 | OK |
| V12 homologados ⊆ convocados e sem duplicatas | 12 homologados sem convocação | ≤ 1% dos homologados | OK |
| V13 junção vagas × resultado | 4 células órfãs em 16954 | ≤ 0,1% | OK |

## V1. Cobertura da extração

Registros extraídos do resultado final do PAS 3 × inscrições de 8 dígitos seguidas de vírgula no texto da seção de resultados (contagem bruta, sem interpretar o registro).
| Subprograma | Inscrições no texto | Extraídos | Não interpretados | Cobertura |
|---|---|---|---|---|
| 15-17 | 9279 | 9279 | 0 | 100.00% |
| 16-18 | 9689 | 9689 | 0 | 100.00% |
| 17-19 | 9953 | 9953 | 0 | 100.00% |
| 18-20 | 5954 | 5954 | 0 | 100.00% |
| 19-21 | 8587 | 8587 | 0 | 100.00% |
| 20-22 | 7299 | 7299 | 0 | 100.00% |
| 21-23 | 8021 | 8021 | 0 | 100.00% |
| 22-24 | 8502 | 8502 | 0 | 100.00% |
| 23-25 | 8708 | 8708 | 0 | 100.00% |

## V2. Reextração independente (pdftotext/poppler × pypdf)

Amostra aleatória (semente fixa 42) de até 300 candidatos por subprograma. Para cada um, o registro é lido de novo do PDF com o `pdftotext` (poppler), com um analisador mínimo e independente do pipeline, e comparado campo a campo com a tabela: 9 notas, argumento final e todas as classificações.

As divergências são classificadas. **Sinal**: o poppler descarta o "-" que o PDF coloca sozinho no fim da linha (ex.: AF -55,760 lido como 55,760). O valor do pypdf é o correto, porque só ele é compatível com a classificação publicada (V5 tem 0 pares fora de ordem com os valores do pypdf). **Página**: o poppler cola o número da página no valor (ex.: 5,034 lido como 1155,034) ou insere esse número entre os campos quando o registro termina no pé da página (conferido no próprio PDF: é o número impresso naquela página). **Outra**: divergência sem explicação, que conta como erro.
| Subprograma | Amostra | Achados no poppler | Campos comparados | Idênticos | Div. sinal | Div. página | Div. sem explicação |
|---|---|---|---|---|---|---|---|
| 15-17 | 300 | 296 | 5840 | 99.777% | 7 | 6 | 0 |
| 16-18 | 300 | 298 | 5886 | 99.881% | 5 | 2 | 0 |
| 17-19 | 300 | 297 | 5811 | 99.707% | 14 | 3 | 0 |
| 18-20 | 300 | 297 | 5819 | 99.759% | 11 | 3 | 0 |
| 19-21 | 300 | 296 | 5809 | 99.690% | 12 | 6 | 0 |
| 20-22 | 300 | 295 | 5780 | 99.740% | 7 | 8 | 0 |
| 21-23 | 300 | 294 | 5787 | 99.827% | 10 | 0 | 0 |
| 22-24 | 300 | 299 | 5878 | 99.779% | 13 | 0 | 0 |
| 23-25 | 300 | 295 | 5787 | 99.775% | 13 | 0 | 0 |

## V3. Consistência entre editais de etapas diferentes

As notas das etapas 1 e 2 aparecem de novo no resultado do PAS 3. Elas são comparadas com os resultados finais do PAS 1 e do PAS 2 (outros editais, publicados um e dois anos antes). Diferenças residuais vêm de retificações publicadas depois.
| Subprograma | Etapa | Comparados | Idênticos | % |
|---|---|---|---|---|
| 15-17 | 2 | 9101 | 9101 | 100.00% |
| 16-18 | 1 | 8848 | 8847 | 99.99% |
| 16-18 | 2 | 9548 | 9548 | 100.00% |
| 17-19 | 1 | 8927 | 8926 | 99.99% |
| 17-19 | 2 | 9821 | 9821 | 100.00% |
| 18-20 | 1 | 5442 | 5441 | 99.98% |
| 18-20 | 2 | 5875 | 5875 | 100.00% |
| 19-21 | 1 | 7979 | 7979 | 100.00% |
| 19-21 | 2 | 8458 | 8458 | 100.00% |
| 20-22 | 1 | 6626 | 6625 | 99.98% |
| 20-22 | 2 | 7210 | 7210 | 100.00% |
| 21-23 | 1 | 7046 | 7046 | 100.00% |
| 21-23 | 2 | 7942 | 7942 | 100.00% |
| 22-24 | 1 | 7490 | 7462 | 99.63% |
| 22-24 | 2 | 8392 | 8390 | 99.98% |
| 23-25 | 1 | 7712 | 7707 | 99.94% |
| 23-25 | 2 | 8615 | 8614 | 99.99% |

## V4. Médias e desvios × números oficiais do Cebraspe

Média e desvio padrão (populacional) da Parte II e da redação do PAS 3, calculados a partir da tabela, comparados com os publicados pelo Cebraspe (edital de média e desvio ou fim do resultado final). A Parte I não entra porque a média oficial é por língua estrangeira, que não é publicada por candidato. As etapas 1 e 2 não entram porque os PDFs dessas etapas incluem ausentes com nota zero, excluídos do cálculo oficial.
| Subprograma | Prova | n | Média calc. | Média oficial | DP calc. | DP oficial |
|---|---|---|---|---|---|---|
| 15-17 | Parte II | 9279 | 28.447 | 28.449 | 12.607 | 12.608 |
| 15-17 | Redação | 9279 | 7.267 | 7.267 | 1.780 | 1.780 |
| 16-18 | Parte II | 9689 | 27.724 | 27.722 | 14.032 | 14.027 |
| 16-18 | Redação | 9689 | 6.782 | 6.782 | 1.739 | 1.738 |
| 17-19 | Parte II | 9953 | 24.315 | 24.313 | 11.512 | 11.511 |
| 17-19 | Redação | 9953 | 6.984 | 6.984 | 1.776 | 1.775 |
| 18-20 | Parte II | 5954 | 27.816 | 27.816 | 12.815 | 12.814 |
| 18-20 | Redação | 5954 | 6.928 | 6.928 | 1.786 | 1.786 |
| 21-23 | Parte II | 8021 | 26.899 | 26.898 | 12.861 | 12.861 |
| 21-23 | Redação | 8021 | 6.863 | 6.864 | 1.989 | 1.989 |
| 22-24 | Parte II | 8502 | 31.739 | 31.740 | 14.066 | 14.063 |
| 22-24 | Redação | 8502 | 7.548 | 7.548 | 1.739 | 1.739 |
| 23-25 | Parte II | 8708 | 30.671 | 30.675 | 13.751 | 13.752 |
| 23-25 | Redação | 8708 | 7.130 | 7.130 | 1.789 | 1.789 |

## V5. Classificação × argumento final

Dentro de cada curso e categoria, a classificação publicada deve seguir o argumento final em ordem decrescente. Antes da correção do cabeçalho de curso (ver `metodologia.md`, seção 4) havia 136, 82, 62, 212, 18, 38, 32, 36, 28 e 0 pares fora de ordem no Universal (14-16 a 23-25). Empates exatos de AF são listados à parte: o desempate segue o Edital nº 1 de cada subprograma.
| Subprograma | Grupos curso×categoria | Pares comparados | Fora de ordem | Classificação repetida | Empates de AF |
|---|---|---|---|---|---|
| 15-17 | 537 | 13990 | 0 | 0 | 10 |
| 16-18 | 546 | 15344 | 0 | 0 | 3 |
| 17-19 | 533 | 16287 | 0 | 0 | 6 |
| 18-20 | 481 | 9220 | 0 | 0 | 5 |
| 19-21 | 525 | 13182 | 0 | 0 | 15 |
| 20-22 | 487 | 10616 | 0 | 0 | 3 |
| 21-23 | 481 | 11191 | 0 | 0 | 1 |
| 22-24 | 433 | 11549 | 0 | 0 | 14 |
| 23-25 | 416 | 11429 | 0 | 0 | 11 |

## V6. Elegibilidade da aprovação (convocação × resultado)

A categoria de cada convocação vem da legenda (1)–(10) do edital de convocação; a classificação por categoria vem do resultado final. Todo convocado numa categoria precisa ter classificação nela (ou seja, concorria naquela vaga).
| Subprograma | Convocações verificáveis | Sem classificação na categoria | Idem, sub judice | Convocado fora do resultado do PAS 3 | Convocação SJ sem categoria |
|---|---|---|---|---|---|
| 15-17 | 4673 | 1 | 0 | 1 | 9 |
| 16-18 | 5118 | 0 | 1 | 5 | 0 |
| 17-19 | 4316 | 0 | 0 | 6 | 0 |
| 18-20 | 2899 | 1 | 2 | 1 | 3 |
| 19-21 | 3956 | 0 | 1 | 1 | 0 |
| 20-22 | 3752 | 3 | 1 | 0 | 0 |
| 21-23 | 3899 | 0 | 1 | 2 | 3 |
| 22-24 | 4019 | 0 | 1 | 1 | 4 |
| 23-25 | 4053 | 0 | 0 | 8 | 1 |

"Convocado fora do resultado do PAS 3": a inscrição não aparece em nenhum resultado final do repositório, nem pelo nome. São candidatos incluídos depois por editais de retificação ou sub judice que não estão no repositório. Eles não têm argumento final e por isso não entram nas notas de corte. "Idem, sub judice": a convocação ou o candidato é sub judice (decisão judicial que garante a vaga independentemente da classificação).

## V7. Ninguém pulado na ordem de classificação

Para cada curso e categoria, encontra a pior classificação entre os convocados naquela categoria e conta os candidatos do mesmo curso com classificação melhor na categoria que nunca foram convocados. Pelas regras do edital esse número deve ser zero, exceto quando o candidato perde a vaga reservada na validação da autodeclaração (heteroidentificação, a partir de 21-23) ou na avaliação biopsicossocial. Em 15-17 e 16-18 (SISUnB) a classificação publicada é da pré-opção de curso, então o teste é feito só para quem não mudou de curso.
| Subprograma | Células curso×categoria com convocados | Não convocados acima do último convocado |
|---|---|---|
| 15-17 | 514 | 9 |
| 16-18 | 516 | 1 |
| 17-19 | 512 | 0 |
| 18-20 | 436 | 0 |
| 19-21 | 487 | 4 |
| 20-22 | 449 | 0 |
| 21-23 | 449 | 2 |
| 22-24 | 366 | 6 |
| 23-25 | 352 | 2 |

## V8. Nota de corte da tabela 2

Para cada célula (curso, semestre, categoria), toma o convocado com a **pior classificação na categoria** (informação do resultado final, independente do AF) e compara o AF dele com a `nota_corte_ultima_chamada` da tabela 2 (o menor AF entre os convocados da célula). Se a classificação e o AF forem coerentes e a célula estiver bem montada, os dois coincidem. O teste vale para as duas regras de preenchimento (cotas antes do Universal até 21-23; Universal antes das cotas a partir de 22-24), porque compara posição e nota dentro da mesma categoria.
| Subprograma | Células com nota de corte | Corte = AF do pior classificado | % |
|---|---|---|---|
| 15-17 | 865 | 865 | 100.00% |
| 16-18 | 871 | 870 | 99.89% |
| 17-19 | 830 | 830 | 100.00% |
| 18-20 | 436 | 435 | 99.77% |
| 19-21 | 712 | 712 | 100.00% |
| 20-22 | 628 | 627 | 99.84% |
| 21-23 | 632 | 632 | 100.00% |
| 22-24 | 529 | 528 | 99.81% |
| 23-25 | 506 | 504 | 99.60% |

## V9. Regime da cascata de preenchimento

Até 21-23 as vagas de cota eram preenchidas antes do Universal; a partir de 22-24 (Lei 14.723/2023) o Universal é preenchido primeiro e o cotista só ocupa vaga reservada se não alcançar a ampla concorrência. Consequência observável, no 1º semestre e na 1ª chamada: convocados **por cota** cuja classificação no Universal está dentro do número de vagas do Universal do curso (ou seja, que teriam entrado pela ampla concorrência). Antes da lei esse número deve ser positivo; depois, zero. A comparação usa a posição e não o AF, porque vagas de cota não preenchidas migram para o Universal e baixam o corte dele. Os dados não usam a regra na construção das tabelas, então o teste confronta os dados com a regra de cada edital.
| Subprograma | Regra do edital | Convocados por cota (1º sem., 1ª chamada) | Dentro das vagas do Universal pela classificação | % | Esperado |
|---|---|---|---|---|---|
| 15-17 | cotas primeiro | 1066 | 79 | 7.4% | > 0 |
| 16-18 | cotas primeiro | 1065 | 83 | 7.8% | > 0 |
| 17-19 | cotas primeiro | 1025 | 150 | 14.6% | > 0 |
| 18-20 | cotas primeiro | 1169 | 420 | 35.9% | > 0 |
| 19-21 | cotas primeiro | 914 | 190 | 20.8% | > 0 |
| 20-22 | cotas primeiro | 804 | 157 | 19.5% | > 0 |
| 21-23 | cotas primeiro | 828 | 141 | 17.0% | > 0 |
| 22-24 | Universal primeiro | 725 | 0 | 0.0% | 0 |
| 23-25 | Universal primeiro | 730 | 0 | 0.0% | 0 |

## V10. Quadro de vagas

(a) Soma das vagas extraídas × "TOTAL GERAL" impresso no edital (quando existe). (b) Linha de Ciência da Computação do PDF × CSV. (c) Regras da Lei 12.711, que não dependem da ordem das colunas: metade das vagas de escola pública vai para a renda mais baixa (|R1 − R2| ≤ 1 por curso) e a parcela PPI é ≥ não PPI. O teste (c) também é aplicado à ordem alternativa das colunas, para mostrar que ele distingue as duas leituras.
| Subprograma | Vagas extraídas | TOTAL GERAL do edital | Linha de CC idêntica | Lei 12.711 (renda / PPI), ordem usada | Idem, ordem alternativa |
|---|---|---|---|---|---|
| 15-17 | 4222 | — | sim | 100% / 100% | 0% / 100% |
| 16-18 | 4222 | — | sim | 100% / 100% | 0% / 100% |
| 17-19 | 4232 | — | sim | 100% / 100% | 0% / 100% |
| 18-20 | 4232 | 4232 | sim | 100% / 100% | 0% / 100% |
| 19-21 | 4232 | 4232 | sim | 100% / 100% | 0% / 100% |
| 20-22 | 4238 | 4238 | sim | 100% / 100% | 0% / 100% |
| 21-23 | 4233 | 4233 | sim | 100% / 100% | 0% / 100% |
| 22-24 | 4233 | 4233 | sim | 99% / 100% | 0% / 100% |
| 23-25 | 4212 | 4212 | sim | 100% / 100% | 1% / 100% |

## V11. Convocados na 1ª chamada × vagas e candidatos

Por curso, o número de convocados na 1ª chamada (editais de convocação) é comparado com o esperado pelas regras: no 1º semestre, o menor valor entre as vagas (edital de abertura) e os candidatos não eliminados do curso (resultado final); no 2º semestre, o menor valor entre as vagas e os candidatos que sobraram depois de todas as chamadas do 1º semestre. As vagas que sobram numa categoria migram para outra do mesmo curso. Três documentos independentes. Diferença de 1 a 2 é esperada quando há candidato sub judice ou convocação posterior por decisão judicial.
| Subprograma | Cursos | Igual | Diferença ≤ 2 | Diferença > 2 | Exemplos |
|---|---|---|---|---|---|
| 15-17 | 98 | 97 | 1 | 0 |  |
| 16-18 | 97 | 95 | 2 | 0 |  |
| 17-19 | 99 | 98 | 1 | 0 |  |
| 18-20 | 100 | 100 | 0 | 0 |  |
| 19-21 | 100 | 99 | 0 | 1 | FISICA (BACHARELADO) (18 conv., esperado 28) |
| 20-22 | 99 | 97 | 0 | 2 | ARTES VISUAIS (LICENCIATURA) (11 conv., esperado 0); ARTES VISUAIS (BACHARELADO) (12 conv., esperado 21) |
| 21-23 | 99 | 98 | 1 | 0 |  |
| 22-24 | 98 | 97 | 1 | 0 |  |
| 23-25 | 98 | 97 | 1 | 0 |  |

Em 18-20 as convocações são para o total de vagas, sem separar semestres (semestre 0 na tabela 2); o esperado usa a soma das vagas dos dois semestres.

## V12. Homologação, duplicatas e SISUnB

Homologados (relação de selecionados) devem ter sido convocados (editais de convocação). Convocações repetidas foram removidas no pipeline (o edital da 1ª chamada do 2º semestre de 21-23 publica duas vezes o bloco de Enfermagem). Em 15-17 e 16-18 o SISUnB permitia trocar de curso depois do resultado: conta quantos aprovados mudaram de curso.
| Subprograma | Homologados | Homologados sem convocação | Convocações duplicadas | Aprovados | Aprovados que mudaram de curso |
|---|---|---|---|---|---|
| 15-17 | 3918 | 0 | 0 | 4682 | 0 |
| 16-18 | — | — | 0 | 5123 | 1 |
| 17-19 | 2240 | 0 | 0 | 4322 | 0 (sem SISUnB) |
| 18-20 | 2451 | 0 | 1 | 2902 | 0 (sem SISUnB) |
| 19-21 | 2689 | 7 | 0 | 3957 | 0 (sem SISUnB) |
| 20-22 | 2597 | 0 | 0 | 3752 | 0 (sem SISUnB) |
| 21-23 | 2565 | 0 | 0 | 3902 | 0 (sem SISUnB) |
| 22-24 | 2629 | 5 | 0 | 4023 | 0 (sem SISUnB) |
| 23-25 | 2637 | 0 | 0 | 4061 | 0 (sem SISUnB) |

## V13. Junção entre edital de abertura e resultado final

O nome do curso é escrito de formas diferentes nos editais; o pipeline casa cada nome com o do quadro de vagas (ver `intermediarios/correspondencia_cursos.csv`). Conta as células da tabela 2 que ficaram órfãs: com candidatos ou convocados e sem vagas (junção falhou), e cursos com vagas e nenhum candidato no resultado (pode ser real: cursos noturnos pequenos ou que exigem certificação de habilidade específica).
| Subprograma | Células | Com candidatos e sem vagas | Cursos com vagas e sem candidatos | Exemplos |
|---|---|---|---|---|
| 15-17 | 1961 | 1 | 1 | LICENCIATURA EM ARTES VISUAIS |
| 16-18 | 1960 | 0 | 2 | LICENCIATURA EM ARTES CENICAS; LICENCIATURA EM ARTES VISUAIS |
| 17-19 | 1970 | 0 | 1 | LICENCIATURA EM MUSICA |
| 18-20 | 1020 | 0 | 2 | CIENCIAS NATURAIS (LICENCIATURA); LICENCIATURA EM MUSICA |
| 19-21 | 2010 | 0 | 2 | ARTES VISUAIS (LICENCIATURA); MUSICA (BACHARELADO) |
| 20-22 | 2013 | 3 | 3 | ARTES VISUAIS (LICENCIATURA); LICENCIATURA EM ARTES CENICAS; LICENCIATURA EM MUSICA |
| 21-23 | 2010 | 0 | 3 | ARTES VISUAIS (LICENCIATURA); GESTAO AMBIENTAL (BACHARELADO); LICENCIATURA EM MUSICA |
| 22-24 | 1990 | 0 | 3 | ARTES VISUAIS (LICENCIATURA); CIENCIAS NATURAIS (LICENCIATURA); LICENCIATURA EM MUSICA |
| 23-25 | 2020 | 0 | 3 | CIENCIAS NATURAIS (LICENCIATURA); GESTAO AMBIENTAL (BACHARELADO); MUSICA (LICENCIATURA) |
