## Resumo dos principais insights da estatística descritiva

### 1. Variáveis inteiras e indicadores

- Os prazos apresentam dispersão relevante: a carência tem mediana de **18 meses**, a amortização de **72 meses** e o prazo total de **96 meses**. Os máximos de **259**, **399** e **408 meses**, respectivamente, indicam contratos muito longos ou possíveis valores extremos que precisam ser investigados.
- `indicador_inovacao` vale 1 em aproximadamente **6,8%** das operações. A inovação é, portanto, uma característica minoritária e deve ser analisada com contagens e intervalos de confiança, não apenas pela média.
- `tem_excepcionalidade` vale 1 em aproximadamente **0,9%** dos casos. É uma variável extremamente desbalanceada; antes de usá-la em testes ou modelos, devemos verificar a definição do indicador e o número absoluto de ocorrências.
- O apoio é predominantemente **direto** (**82,7%**) e **reembolsável** (**93,3%**). `flag_cliente_publico` representa aproximadamente **8,5%** da base.
- `porte_cliente_ordinal` está concentrado no maior porte: a mediana e o terceiro quartil são 4. O ordinal não deve ser interpretado automaticamente como uma escala linear; é necessário conferir sua distribuição por categoria.
- `grupo_taxa_juros_ordinal` também está concentrado no grupo 1, sugerindo baixa variabilidade entre as operações.
- `qtd_palavras_descricao` tem mediana de 28 palavras e máximo de 148. Valores muito altos podem ser avaliados como possíveis outliers textuais, mas a variável pode ser útil como medida de complexidade ou detalhamento do projeto.

### 2. Variáveis categóricas

- Há concentração regional em **SP**, que representa aproximadamente **23,3%** das operações. A distribuição por UF deve ser apresentada antes de qualquer conclusão sobre representatividade nacional.
- `nome_municipio` e `id_municipio` possuem muitos registros como **"SEM MUNICIPIO"** ou **"NAO INFORMADO"**. Esses valores devem ser tratados como categoria de ausência, e não como municípios reais. Também é necessário conferir se o preenchimento é estruturalmente associado a operações diretas ou a determinados tipos de cliente.
- `porte_cliente` é dominado por **GRANDE** (aproximadamente **80,5%**) e `natureza_cliente` por **PRIVADA** (aproximadamente **91,5%**). A base representa principalmente grandes empresas privadas, portanto conclusões sobre pequenas empresas ou clientes públicos terão pouca sustentação amostral.
- `modalidade_apoio` é majoritariamente **REEMBOLSÁVEL** (aproximadamente **93,3%**) e `forma_apoio` majoritariamente **DIRETA** (aproximadamente **82,7%**). Essas concentrações podem reduzir o poder de comparação entre grupos.
- `setor_cnae_bndes` e `setor_bndes` têm apenas quatro categorias, enquanto `tipo_instrumento_financeiro`, `descricao_subclasse` e alguns campos de localização têm alta cardinalidade. Para a análise, convém começar pelos agrupamentos mais estáveis e deixar categorias raras explícitas ou agregadas em "OUTROS".
- `situacao_contrato` tem **LIQUIDADO** como categoria mais frequente (aproximadamente **59,7%**), o que permite comparar valor contratado e valor desembolsado por situação.
- `grupo_taxa_juros` é dominado por **BAIXA** (aproximadamente **89,0%**), reforçando o desbalanceamento já observado no ordinal.

### 3. Variáveis contínuas

- `valor_contratado` tem mediana de aproximadamente **R$ 9,46 milhões**, média de **R$ 52,34 milhões** e máximo de **R$ 9,89 bilhões**. A média muito acima da mediana evidencia forte assimetria à direita e influência de operações de grande valor.
- `valor_desembolsado` tem mediana de aproximadamente **R$ 6,65 milhões**, inferior à mediana contratada de **R$ 9,46 milhões**. A diferença deve ser analisada por situação do contrato, ano e setor; não é suficiente concluir que representa apenas saldo a desembolsar.
- `taxa_juros` tem mediana de **2,5** e máximo de **16,53**, indicando possível concentração em poucos níveis e eventuais observações extremas. É importante verificar a unidade e o significado econômico da taxa antes de aplicar transformações.
- Para `valor_contratado` e `valor_desembolsado`, médias e desvios-padrão não descrevem bem o centro da distribuição. As próximas tabelas e gráficos devem priorizar mediana, quartis, IQR e escala logarítmica (`log1p`).

### Decisões para os próximos passos da EDA

1. Validar qualidade e semântica dos dados: identificar placeholders, duplicidades, contratos com valor zero e possíveis inconsistências entre contratado e desembolsado.
2. Visualizar as distribuições de `valor_contratado`, `valor_desembolsado`, `taxa_juros` e prazos com histogramas, boxplots e versões em escala logarítmica.
3. Comparar o valor contratado por `porte_cliente`, `natureza_cliente`, UF, setor e situação do contrato, sempre mostrando número de operações por grupo.
4. Medir correlações entre variáveis numéricas com Pearson e Spearman, sem incluir identificadores como `id_contrato`.
5. Quantificar a qualidade dos grupos raros e dos indicadores desbalanceados antes de testes de hipótese ou modelagem.
6. Definir `valor_contratado` como variável-alvo e separar a análise descritiva da análise de associação, evitando interpretar correlação como causalidade.