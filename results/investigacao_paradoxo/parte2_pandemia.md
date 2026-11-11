# Parte 2b — A pandemia foi "mascarada" por provas mais fáceis?

O artigo diz que as notas brutas se mantiveram estáveis durante o ensino remoto. A hipótese a testar: as provas da pandemia foram mais fáceis e escondem uma perda real de aprendizado.

**Anos letivos de ensino remoto no DF: 2020 e 2021.** A etapa *e* do subprograma AA-BB avalia o ano letivo 20AA + *e* − 1. As provas desses dois anos letivos são:
- PAS 3 de 18-20 (aplicado em 7/3/2021);
- PAS 2 e PAS 3 de 19-21 (o PAS 3 foi aplicado em 30/1/2022);
- PAS 1 e PAS 2 de 20-22;
- PAS 1 de 21-23.

## Antes de tudo: o que é e o que não é possível medir

1. **O Argumento Final não pode "mascarar" nada.** Ele é padronizado dentro de cada ano: a média do ano vira 0, seja a prova fácil ou difícil. Por construção, nenhuma análise baseada no AF (F2 a F6 do artigo) é afetada pela dificuldade da prova.
2. **As notas brutas misturam duas coisas.** Uma média bruta alta pode significar "prova fácil" ou "alunos mais preparados". Para separar as duas, seria preciso ter questões repetidas entre os anos ("itens âncora"), e o Cebraspe não as divulga. **Com estes dados, o nível absoluto de aprendizado não é mensurável**, e qualquer afirmação sobre "resiliência" das notas brutas precisa dessa ressalva.

Dentro desse limite, há quatro testes possíveis.

## Teste 1: as provas da pandemia tiveram médias brutas fora do padrão?

Cada prova da pandemia foi comparada às provas da mesma etapa e do mesmo tipo nos outros anos. O escore z mede quantos desvios-padrão a média da prova pandêmica ficou da média histórica; acima de +2 ou abaixo de −2 seria anormal (`p2_dificuldade_pandemia.csv`).

| Prova | Ano letivo | Média na pandemia | Média dos outros anos | z |
|---|---|---|---|---|
| EB2 PAS 1 | 2020 | 22,4 | 22,0 | +0,19 |
| EB2 PAS 1 | 2021 | 21,0 | 22,0 | −0,53 |
| EB2 PAS 2 | 2020 | 24,7 | 21,6 | +1,05 |
| EB2 PAS 2 | 2021 | 20,8 | 21,6 | −0,27 |
| EB2 PAS 3 | 2020 | 27,8 | 28,0 | −0,06 |
| EB2 PAS 3 | 2021 | 23,4 | 28,0 | −1,77 |
| Redação PAS 1 | 2020 | 5,54 | 5,98 | −1,84 |
| Redação PAS 3 | 2021 | 6,99 | 7,15 | −0,55 |

- **Nenhuma prova da pandemia está fora da faixa normal**: todos os |z| são menores que 2.
- Os sinais se dividem: algumas médias ficaram um pouco acima do histórico, outras abaixo. O EB2 do PAS 3 de 2021 foi um dos **mais baixos** da série.
- A assimetria das notas, que ficaria muito negativa numa prova fácil (todo mundo perto do teto), também ficou no padrão.
- **Não há sinal de provas sistematicamente mais fáceis.** A hipótese de mascaramento não tem sustentação nos dados.

## Teste 2: quem fez o PAS 3 durante a pandemia? (o verdadeiro "mascaramento")

| Subprograma | % dos presentes no PAS 2 que fizeram o PAS 3 | EB2 do PAS 2 de quem ficou | de quem saiu |
|---|---|---|---|
| 17-19 | 51,4% | 24,1 | 15,8 |
| **18-20 (PAS 3 em mar/2021)** | **27,9%** | 25,0 | 18,2 |
| 19-21 | 53,3% | 28,7 | 20,1 |
| 20-22 | 51,1% | 25,1 | 16,3 |
| 21-23 | 52,1% | 21,9 | 14,6 |

- No PAS 3 de 18-20, **só 28% dos que fizeram o PAS 2 compareceram**, contra cerca de 52% nos outros anos. Foram 5.954 presentes, contra 8.000 a 10.000 nos demais.
- Quem desiste tem nota menor. Portanto, o grupo que fez essa prova era **mais selecionado** que o normal.
- **Esse é o mecanismo de "mascaramento" que os dados sustentam:** não uma prova mais fácil, e sim uma população de candidatos mais filtrada. Mesmo assim, o EB2 desse PAS 3 ficou na média histórica (z = −0,06). Um grupo mais forte com média normal é compatível com uma perda de aprendizado ou com uma prova mais difícil, mas os dados não permitem dizer qual das duas.

**Sugestão para o artigo:** em vez de "resiliência das notas", dizer que as médias brutas ficaram na faixa histórica, que no PAS 3 de 2018-2020 só compareceu cerca de um quarto dos candidatos do PAS 2, e que essa seleção pode ter compensado eventuais perdas.

## Teste 3: a pandemia aumentou a desigualdade entre SUE e cotas?

Ao contrário do nível absoluto, a **diferença entre grupos** pode ser medida, porque os dois grupos fazem a mesma prova. O modelo compara o d de cada etapa de cada coorte e controla a coorte e a etapa (`p2_modelo_pandemia.csv`):

| Grupo | Prova | Efeito de a prova ser da pandemia sobre o d | IC 95% | p |
|---|---|---|---|---|
| EP | EB2 | **−0,10** | −0,16 a −0,05 | <0,001 |
| EP | Redação | +0,04 | −0,01 a +0,09 | 0,08 |
| Negros | EB2 | −0,04 | −0,08 a −0,01 | 0,02 |
| Negros | Redação | +0,03 | −0,03 a +0,08 | 0,32 |

- Nas provas de conhecimentos (EB2) aplicadas na pandemia, a distância entre SUE e cotistas foi **menor**, e não maior: cerca de 0,1 desvio-padrão.
- Os dados não dizem por quê. Há duas explicações compatíveis:
  - provas mais difíceis "comprimem" as notas perto do mínimo e reduzem todas as diferenças;
  - a desistência foi diferente entre os grupos.
- O que os dados **descartam** é a ideia de que a pandemia ampliou a desvantagem dos cotistas *entre os candidatos que chegaram ao PAS 3*.

## Teste 4: as provas da pandemia ordenaram os alunos de forma menos confiável?

Correlação entre o EB2 do PAS 1 (ou PAS 2) e o EB2 do PAS 3 dos mesmos alunos (`p2_correlacao_etapas.csv`):

| Coorte | Provas na pandemia | r PAS 1 × PAS 3 | r PAS 2 × PAS 3 |
|---|---|---|---|
| 16-18 | nenhuma | 0,71 | 0,78 |
| 18-20 | PAS 3 | 0,66 | 0,75 |
| 19-21 | PAS 2 e 3 | 0,66 | 0,79 |
| 20-22 | PAS 1 e 2 | 0,69 | 0,77 |
| 22-24 | nenhuma | 0,69 | 0,82 |

As correlações ficaram iguais: as provas da pandemia classificaram os alunos com a mesma consistência das demais.

## Conclusão da Parte 2b

1. Não há evidência de provas mais fáceis na pandemia: as médias brutas ficaram na faixa normal, com sinais mistos.
2. O "mascaramento" que os dados mostram é de **seleção**: no PAS 3 de 18-20 só compareceu um quarto dos candidatos, os mais preparados.
3. O AF, base de quase todas as análises do artigo, é imune à dificuldade da prova.
4. O nível absoluto de aprendizado não pode ser medido com dados públicos sem itens âncora. O artigo deve dizer isso explicitamente.
