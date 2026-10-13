# Raw data: o que cada edital contém

## Escopo

Estamos avaliando **principalmente quem chegou ao PAS 3**, uma vez que os editais mais importantes para a pesquisa estão nessa etapa.

O PAS 1 e o PAS 2 podem ser úteis para medir **desistências** ou **notas de quem não fez o PAS 3**.

## Estrutura de pastas

```
raw_data/
└── <subprograma>/
    ├── explicacao.md               # explica o que cada edital tem
    ├── PAS1/
    │   └── <tipo do edital>/       # PDFs desse tipo de edital na etapa 1 são agrupados aqui
    │       └── <nome do edital>/   # arquivo PDF com o nome do edital
    ├── PAS2/
    │   └── <tipo do edital>/   
    └── PAS3/
        └── <tipo do edital>/  
```

Futuramente, o *parsed_data* deve conter informações que tratam sobre:

```
parsed_data/
├── alunos com notas e classificações (universal ou por cota)
└── alunos com os cursos em que foram convocados/inscritos
```

Cada pasta de edital tem o nome do tipo de edital e contém os PDFs referentes a ele. Caso um PDF seja um *edital sub_júdice*, será nomeado ao final com a terminação *_SJ*.

## Tipos de editais importantes para o PAS 3

### Sub judice

É preciso fazer **join com os outros editais**, dependendo do edital. Os arquivos ficam no repositório agrupados na pasta correta e **claramente classificados como sub judice**, para o caso de decidirmos excluí-los depois.

### Relação final (ou provisória-RP/sub judice) das pessoas candidatas selecionadas, em X.ª chamada, dentro do quantitativo de vagas para o Y.º semestre

- Fornece a relação de quem **teve o registro acadêmico homologado**, ou seja, quem efetivou a inscrição de fato, com documentação.
- **Dados fornecidos:** nome, número de inscrição, campus/curso/turno.

### Convocação, em X.ª chamada, para o registro acadêmico on-line das pessoas candidatas selecionadas dentro do quantitativo de vagas para o Y.º semestre

- Fornece a relação de quem **foi chamado** para as vagas, mas não necessariamente efetivou a inscrição de fato.
- **Dados fornecidos:** nome, número de inscrição, campus/curso/turno e sistema de cotas da convocação.

### Resultado final das pessoas candidatas não eliminadas na terceira etapa

- Fornece o resultado final de todas as pessoas que **não foram eliminadas**.
- **Dados fornecidos:** campus/curso/turno, número de inscrição, nome da pessoa, escore bruto (EB) das partes 1 e 2 e nota da redação das etapas 1, 2 e 3 (o tipo D já está incluído no EB), argumento final e classificação nos sistemas de cotas.
- Na classificação por cota, `-` significa que a pessoa não participou daquela cota, e um número é a classificação dela nessa cota. As colunas de cota se sobrepõem: a mesma pessoa pode ter classificação em mais de uma.

### Edital de abertura da terceira etapa

- Contém as regras da etapa: sistemas de cotas e subsistemas, critérios de elegibilidade, validação de autodeclaração, ordem de seleção e remanejamento de vagas, além do **quadro de vagas** por curso e cota.
- Fica em `PAS3/Edital_de_abertura/edital_de_abertura.pdf`.
- O resumo comparativo da década está em [`regulamentos.md`](regulamentos.md).

##  Tipos de editais importantes para o PAS 1 e o PAS 2

### Resultado final de PAS 1 e PAS 2, mais as retificações dele

- Serve para saber as notas de quem **não foi até o PAS 3**.

## Próximos passos

Entender como funcionam a nota do PAS e o sistema de cotas, para saber o que analisar.