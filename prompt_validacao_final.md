# Instruções para Validação e Ajuste do Pipeline de Dados PAS/UnB

Eu verifiquei o pipeline de parsing e as mudanças no repositório. Ficou bem estruturado, mas eu queria garantir maior segurança de que esses dados estão de fato seguros para uso em um artigo científico, e seria bom ter métricas de validação que conseguissem justificar no artigo que temos dados de boa qualidade. 

Assim, foram feitas algumas modificações na branch do repositório em que você estava mexendo, com dois novos scripts que removem, respectivamente: dados a respeito do subprograma 14-16 (que apresentavam maiores irregularidades e inconsistências) e tags sobre engenharia de software (porque o PAS não separa software de outras engenharias, então optamos por largar esse curso do escopo do artigo e avaliar só 3 cursos mesmo). 

Entretanto, ainda há alguns pontos que merecem uma checagem mais aprofundada sua, os quais vou listar a seguir:

## 1. Investigar pares fora de ordem
* Pegue os pares fora de ordem propriamente ditos (não só a quantidade, mas quais são eles) e tente achar uma razão para a ordem estar errada. Compare com o que deveria ser e veja se a ordem não está diferente porque você esqueceu dos critérios de desempate (pode ler os editais de regras para ver o desempate).
* Talvez seja erro de leitura e, por isso, pode ser necessário modificar o pipeline para gerar novas tabelas (utilize também as partes do pipeline que foram criadas no commit novo, que alteram as tabelas do `build_tables`, para manter a ideia de que vamos excluir 14-16 e eng. software).
* Encontre a razão, detalhe o que causava e qual a solução definitiva oferecida por você no `metodologia.md`, com alguma validação que mostre que de fato surtiu efeito.

## 2. Fazer um glossário
* Crie em algum lugar no repositório um arquivo `.md` (glossário) que descreva de forma clara e detalhada o que cada coluna de cada tabela de fato considera, de qual documento e de qual elemento do documento a informação é retirada.

## 3. Propor validações mais rigorosas para o artigo
* Quero métricas que mostrem que os dados são seguros. Quero ver se, na tabela de estudantes, as informações em cada linha estão mesmo corretas (principalmente sobre aprovação e cotas).
* Na tabela de cursos, quero garantia de que a nota de corte está correta para cada coluna que a mede (considere as mudanças das categorias de cotas, que em um momento foram da mais restritiva até a menos restritiva, e em outro foi o contrário). 
* Você deve garantir que os dados estão de fato prontos para um artigo científico que pretende ser levado minimamente a sério. Aprimore o já existente `validate.py` (pode aprimorá-lo completamente se necessário), evitando análises circulares.

## 4. Avaliar se a ordem das colunas dos quadros de vaga dos 9 subprogramas bate com os dados da tabela 2
* **O que acontece no PDF:** O Quadro de Vagas do Cebraspe tem o nome do curso e, logo depois, uma fileira de números (Exemplo: Ciência da Computação | 20 | 2 | 1 | 4 | 0 ...). O problema é que o cabeçalho que diz o que é cada número muda ao longo dos anos. Às vezes a 2ª coluna é "Cota para Negros", às vezes é "Cota PPI de Baixa Renda". 
* **O que o script faz hoje:** Como o cabeçalho muda, o script `vagas.py` tenta "ler" o cabeçalho usando palavras-chave e deduz qual é a ordem das colunas para aquele ano.
* **O perigo (e o que você deve fazer):** Se a dedução do script falhar em algum subprograma, ele pode trocar as colunas. Ele pode dizer que Computação teve 4 vagas para PPI e 1 para Não-PPI, quando na verdade era o contrário. Se isso acontecer, toda a nossa análise de concorrência e nota de corte por cota vai para o ralo.
* **Ação:** Abra o PDF original do Edital de Abertura. Olhe a linha de Ciência da Computação e anote as vagas. Depois, abra o seu `tabela2_curso_cota.csv` e veja se os números estão idênticos. Se baterem, a dedução do script funcionou perfeitamente. *(Nota: Eu chequei manualmente para o 23-25 e está correto).*

## 5. Avaliar o caso estranho do subprograma 16-18 e ver se está de fato tudo certo
* **Duplicatas no 16-18 (Caso SISUnB):** Até 2019, o candidato do PAS fazia uma "pré-opção" de curso. Depois que a nota saía, ele usava o SISUnB (um sistema interno da UnB) para confirmar ou trocar de curso. O Cebraspe publicava os editais de convocação dessa galera na própria página do PAS.
* Se o seu extrator leu o PDF de "Resultado Provisório", depois o de "1ª Chamada" e depois o de "Retificação de Chamada", um mesmo aluno pode ter sido contado duas ou três vezes como "convocado" em cursos diferentes se ele trocou de ideia no SISUnB. Verifique isso.

## 6. Atualizar a documentação
* Ao final, atualize o `metodologia.md` com as alterações feitas por mim (os dois scripts novos de remoção de dados) e por você (etapas extras de validação e correções citadas acima).