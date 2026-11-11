# Investigação: os cotistas superaram o Sistema Universal na Computação?

**Pergunta da professora:** é improvável que a média das cotas (escola pública e Negros) supere a do Sistema Universal Estrito (SUE), já que a OCDE mostra a vantagem do ensino privado. Os dados do artigo estão errados?

**Resposta curta:**
- **Os dados estão corretos, e a professora também tem razão em parte.** Não há inversão real.
- O SUE continua à frente, como a OCDE prevê. Na Computação, porém, a vantagem dele fica concentrada no topo da distribuição, e a sua cauda inferior grande faz a média oscilar.
- As "ultrapassagens" dos gráficos são flutuação de amostras pequenas.
- O único ano com aproximação real (2023-25) é explicado por uma mudança em **quem se inscreveu**, não por uma melhora dos cotistas.

## Documentos

| Arquivo | Conteúdo |
|---|---|
| [`parte1_inversao.md`](parte1_inversao.md) | Teste de cada hipótese (auditoria, N pequeno, caudas, Negros, Licenciatura, Lei 14.723, flexibilização, pandemia, ruído × tendência, PcD) mais duas hipóteses novas |
| [`parte2_revisao_artigo.md`](parte2_revisao_artigo.md) | Checagem afirmação por afirmação do artigo, com sugestões de redação e uma subseção pronta para a Seção V-B |
| [`parte2_pandemia.md`](parte2_pandemia.md) | Teste do "mascaramento" da pandemia pela dificuldade das provas |
| `p1_*.csv`, `p2_*.csv` | Todas as tabelas citadas (cada número dos textos sai daqui) |

Scripts: `scripts/pas/investigacao/` (`comum.py`, `p1_descritivas_e_testes.py`, `p1_ruido_selecao_exogenos.py`, `p2_pandemia.py`).

Para reproduzir:

```bash
pip install pandas numpy scipy statsmodels
cd scripts/pas/investigacao
python3 p1_descritivas_e_testes.py   # cerca de 2,5 min (bootstrap e permutação)
python3 p1_ruido_selecao_exogenos.py
python3 p2_pandemia.py
```

Todos os sorteios usam semente fixa (42), então os resultados se repetem.

## Os sete resultados principais

1. **A base não tem erro que explique o fenômeno.**
   - Não há candidatos duplicados.
   - A cota está declarada para 100% dos candidatos.
   - A classificação é publicada para todos em todas as categorias, então ninguém é rotulado como SUE por engano.
   - O Argumento Final é recalculado a partir das notas brutas com R² > 0,999.
   - Os d de Cohen da investigação reproduzem os da F2.

2. **No Argumento Final, o SUE fica à frente em 8 dos 9 anos na Computação.**
   - Com todos os anos juntos, a vantagem é de **14,7 pontos** (IC 95%: 11,6 a 17,9; p < 0,001; d = 0,26).
   - O único ano invertido (2023-25: −3,9 pontos, p = 0,44) é um **empate estatístico**.

3. **A vantagem do SUE está toda no topo.**
   - Nos 10% melhores, o SUE supera os cotistas em **46 pontos**.
   - Na metade de baixo, os dois grupos são iguais.
   - 10% do SUE tem AF acima de 100, contra 0% a 4% dos grupos de cota.
   - O SUE ocupa 30% do quartil superior de cada curso, contra 8% a 17% de cada cota.

   É exatamente o padrão que a OCDE descreveria. O que muda é que, na Computação, a mediana do SUE é a média do ano (−3), apesar de o corte do SUE passar de 130. O curso atrai muitos candidatos do SUE sem chance real, e isso derruba a média do grupo.

4. **As ultrapassagens dos gráficos são ruído.**
   - Supondo que o SUE tivesse **sempre a mesma vantagem**, o acaso produziria cerca de 42 ultrapassagens em 243 comparações. Os gráficos mostram 47 (p = 0,22).
   - De 2015-17 a 2022-24, o gap da Computação é **constante** (cerca de 0,3 desvio-padrão; inclinação nula; I² = 0%).
   - Na UnB inteira, ao contrário, a queda da desigualdade é real e contínua.

5. **2023-25 é um ano atípico, explicado por composição.**
   - Em Ciência da Computação, os cotistas com nota abaixo da média do ano **caíram de 79 para 28**.
   - Os cotistas acima da média continuaram os mesmos (44 → 45), e o SUE não mudou.
   - A média das cotas subiu porque os mais fracos deixaram de escolher o curso, não porque os cotistas melhoraram.
   - O empate já existia no PAS 1 dessa coorte (2023), antes da Lei 14.723. A lei, além disso, não muda o grupo em que o candidato se inscreveu. **A lei não é a causa.**

6. **Hipóteses descartadas:**
   - "a cota para Negros reúne uma elite parecida com o SUE": a distribuição de Negros é estatisticamente igual à de escola pública (p = 0,46);
   - "a Licenciatura gera a inversão": lá o SUE também lidera, com todos os anos juntos;
   - "candidatos PcD inflam as médias": só 5 casos, sem efeito;
   - "flexibilização de 2022": 2022-24 tem gap normal.

7. **Pandemia:**
   - Não há evidência de provas mais fáceis: as médias brutas ficaram dentro da faixa normal, com sinais mistos.
   - O "mascaramento" que os dados mostram é de **seleção**: no PAS 3 de 2018-20, só 28% dos candidatos do PAS 2 compareceram (contra cerca de 52% nos outros anos), e quem desistiu tinha notas menores.
   - O Argumento Final é padronizado por ano e, portanto, imune à dificuldade da prova.
   - O nível absoluto de aprendizado não pode ser medido com dados públicos.

## Conclusão para apresentar à professora

> A observação da professora está correta quanto ao fenômeno de fundo: **não há inversão real de desempenho**. Em todos os testes robustos (média aparada, mediana, testes não paramétricos, permutação e bootstrap), o Sistema Universal mantém vantagem estatisticamente significativa sobre os cotistas da Computação no conjunto da série (d = 0,26) e, na UnB como um todo, em todos os nove subprogramas (d de 0,69 a 0,21). Esse resultado é coerente com a literatura e com os relatórios da OCDE.
>
> Os dados do artigo, porém, também estão corretos. As "ultrapassagens" observadas nos gráficos de médias são o que a estatística prevê para grupos de 17 a 130 candidatos comparados ano a ano: uma simulação com vantagem constante do SUE produz, só pelo acaso, o mesmo número de ultrapassagens observado. Elas aparecem com mais frequência na Computação por uma particularidade da demanda do curso: o Sistema Universal de Ciência da Computação reúne, além dos melhores candidatos do certame (10% com AF acima de 100), uma grande parcela de candidatos com nota na média da coorte, sem chance real de aprovação. Essa cauda inferior tem o mesmo tamanho da dos cotistas e encolhe a média do grupo, embora a vantagem no topo, onde as vagas são decididas, permaneça intacta (46 pontos no 90º percentil; nota de corte do SUE de 100 a 140 pontos acima das cotas).
>
> O único subprograma com aproximação estatisticamente atípica (2023–2025) é explicado por uma mudança na composição dos inscritos: o número de cotistas com desempenho abaixo da média que escolheram Ciência da Computação caiu de 79 para 28, sem alteração no número de cotistas acima dela nem no perfil do SUE. A aproximação já estava presente no PAS 1 dessa coorte, antes da vigência da Lei nº 14.723/2023, que de todo modo não altera o grupo de inscrição dos candidatos.
>
> Portanto, a comparação com a OCDE não é contrariada: ela descreve populações inteiras, enquanto o artigo compara candidatos autosselecionados para um curso específico, e nessa comparação a vantagem do ensino privado aparece onde importa, no topo da distribuição, mas se dilui na média por causa da heterogeneidade da demanda pelo curso. O texto do artigo deve trocar termos como "superou", "inversão" e "expressiva elevação" por "aproximação" ou "equiparação estatística", e incluir as ressalvas listadas em `parte2_revisao_artigo.md`.
