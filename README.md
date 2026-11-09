Esta base reúne o histórico de financiamentos concedidos pelo BNDES para empresas e órgãos públicos no Brasil. Ela mostra quem pediu o recurso (nome_cliente), onde o projeto será feito (sigla_uf) e para qual setor ele se destina (setor_bndes). Além disso, compara o total aprovado no papel (valor_operacao) que renomeamos para (valor_contratado) com o dinheiro que já foi de fato entregue (valor_desembolsado). Na prática, funciona como um extrato transparente para acompanhar onde o dinheiro do banco está sendo investido.

- Base de Operações Não Automática: Concentra grandes projetos de infraestrutura, expansões industriais, financiamentos estruturados e operações estratégicas.
- devido ao valor elevado, à complexidade técnica ou às exigências do programa, passa por análise e aprovação específica da equipe do BNDES.


# 1. Problema de negócio e objetivo do projeto

## 1.1 Qual é o problema de negócio?

- Um gestor financeiro do BNDES precisa melhorar o planejamento da demanda de crédito e a alocação de capital para operações não automáticas. Ele se beneficiaria muito se pudesse prever o valor total contratado (`valor_contratado`) de novos projetos com base no perfil do cliente, localização geográfica, permitindo otimizar a gestão de liquidez, avaliar riscos e identificar antecipadamente solicitações de crédito fora do padrão.

# 2. Escopo do projeto e metadados

## 2.1 Quais são os objetivos específicos do projeto?

- **i. Entender e preparar os dados:**  consolidar as camadas raw e silver, validar o dicionário de dados, tratar duplicidades por id_contrato, valores ausentes, inconsistências, outliers e categorias com baixa frequência. Realizar análise descritiva: aplicar frequências, histogramas, tabelas de frequência, média, mediana, quartis, percentis e desvio padrão para caracterizar valor_contratado, prazos, taxas, portes, setores e UFs.
    
- **ii. Aplicar regressão:** estimar modelos de regressão linear simples, múltipla e polinomial, com avaliação de R², resíduos e coeficientes. Construir e avaliar o modelo preditivo. Avaliar desempenho e riscos: medir MAE, RMSE, R² e erro por segmento; analisar resíduos.
    
- **iii. Interpretar Previsões e Importância das Variáveis:** Aplicar técnicas de explicabilidade para identificar quais atributos (porte da empresa, setor ou localização) exercem maior influência no valor contratado estimado.
    

## 2.2 Metadados e Fontes de Dados

- **Autor:** André Felipe Cicco Ribas
    
- **Data:** Agosto de 2026
    
- **Fonte dos Dados:** [Base dos Dados](https://basedosdados.org/) (Hospedado no Google Cloud BigQuery)
    
- **Conjunto de Dados / Tabela:** `basedosdados.br_bndes_operacoes_contratadas.operacoes_nao_automaticas`
    
- **Provedor dos Dados:** Banco Nacional de Desenvolvimento Econômico e Social (BNDES)
    
- **Cobertura Temporal:** Janeiro de 2002 – Junho de 2026
    
- **Licença dos Dados:** Dados Abertos / Domínio Público (Lei de Acesso à Informação)
