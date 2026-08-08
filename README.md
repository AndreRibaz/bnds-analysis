# Contexto da base de dados
Esta base reúne o histórico de financiamentos concedidos pelo BNDES para empresas e órgãos públicos no Brasil. Ela mostra quem pediu o recurso (nome_cliente), onde o projeto será feito (sigla_uf) e para qual setor ele se destina (setor_bndes). Além disso, compara o total aprovado no papel (valor_operacao) com o dinheiro que já foi de fato entregue (valor_desembolsado). Na prática, funciona como um extrato transparente para acompanhar onde o dinheiro do banco está sendo investido.

- Base de Operações Não Automática: Concentra grandes projetos de infraestrutura, expansões industriais, financiamentos estruturados e operações estratégicas.
- devido ao valor elevado, à complexidade técnica ou às exigências do programa, passa por análise e aprovação específica da equipe do BNDES.


# 1. Problema de negócio e objetivo do projeto

## 1.1 Qual é o problema de negócio?

- Um gestor financeiro do BNDES precisa melhorar o planejamento da demanda de crédito e a alocação de capital para operações não automáticas. Ele se beneficiaria muito se pudesse prever o valor total contratado (`valor_contratado`) de novos projetos com base no perfil do cliente, localização geográfica e termos do contrato, permitindo otimizar a gestão de liquidez, avaliar riscos e identificar antecipadamente solicitações de crédito fora do padrão.
    

## 1.2 Qual é o contexto?

- Quando um banco de desenvolvimento como o BNDES aloca capital para operações financeiras não automáticas, três Indicadores-Chave de Desempenho (KPIs) essenciais devem ser considerados:
    
    - **i. Eficiência na Alocação de Capital:** Mede o quão efetivamente os recursos financeiros são distribuídos entre setores e regiões para impulsionar o desenvolvimento econômico sem gerar gargalos de liquidez.
        
    - **ii. Valor Médio Contratado por Segmento:** Acompanha o porte típico dos financiamentos concedidos por tamanho de empresa (PMEs vs. Grandes Empresas) e setores econômicos, garantindo uma distribuição equilibrada de crédito.
        
    - **iii. Proporção entre Carência e Amortização:** Avalia a estrutura de pagamento (prazo de carência em relação ao tempo total de amortização) para alinhar os fluxos de caixa de longo prazo com a exposição geral da carteira.
        
- Esses KPIs ajudam o banco a avaliar a eficácia de suas estratégias de concessão de crédito e a mensurar o impacto financeiro de longo prazo desses investimentos no país.
    

# 2. Escopo do projeto e metadados

## 2.1 Quais são os objetivos específicos do projeto?

- **i. Construir um Pipeline Robusto de Engenharia de Recursos (_Feature Engineering_):** Transformar dados brutos tratando a assimetria financeira (transformação logarítmica), codificando variáveis categóricas de alta cardinalidade (CNAE/localizações) e criando variáveis derivadas do domínio (ex: razão entre carência e amortização).
    
- **ii. Treinar e Comparar Modelos de Regressão:** Construir e avaliar modelos lineares baseline (Ridge/Lasso) contra algoritmos baseados em árvores (Random Forest/LightGBM) utilizando métricas de avaliação como $MAE$, $RMSE$ e $R^2$.
    
- **iii. Interpretar Previsões e Importância das Variáveis:** Aplicar técnicas de explicabilidade para identificar quais atributos (porte da empresa, setor ou localização) exercem maior influência no valor contratado estimado.
    

## 2.2 Metadados e Fontes de Dados

- **Autor:** André Cicco Ribas
    
- **Data:** Agosto de 2026
    
- **Fonte dos Dados:** [Base dos Dados](https://basedosdados.org/) (Hospedado no Google Cloud BigQuery)
    
- **Conjunto de Dados / Tabela:** `basedosdados.br_bndes_operacoes_contratadas.operacoes_nao_automaticas`
    
- **Provedor dos Dados:** Banco Nacional de Desenvolvimento Econômico e Social (BNDES)
    
- **Cobertura Temporal:** Janeiro de 2002 – Junho de 2026
    
- **Licença dos Dados:** Dados Abertos / Domínio Público (Lei de Acesso à Informação)


  
    
    
| Entrada                      | Feature Engineering                        | Saída                      |
| ---------------------------- | ------------------------------------------ | -------------------------- |
| valor_contratado             | Transformação Logarítmica (log1p)          | y_log                      |
| prazo_carencia, prazo_amort  | Razão de Carência (carencia / prazo_total) | feature_proporcao_carencia |
| subclasse_cnae, id_municipio | Target Encoding / Aggregation por Setor    | feature_setor_media_valor  |
| data_contratacao             | Extração Temporal (Ano, Mês, Ciclo)        | features_temporais         |



1. **Modelagem de Regressão:** Treinar e comparar um modelo baseline (Regressão Ridge/Lasso) contra um modelo de árvores (Random Forest/LightGBM), avaliando por $MAE$, $RMSE$ e $R^2$.
    
2. **Explicabilidade:** Mapear e interpretar a importância de cada variável na estimativa do crédito.