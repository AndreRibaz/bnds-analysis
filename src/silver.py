"""
Módulo: silver.py
Descrição: Pipeline de transformação e enriquecimento de dados da camada Silver.
Autor: Andre Ribas
Data: 2026-08-11
Versão: 1.3

Este módulo implementa o processo de transformação dos dados da camada Bronze 
para a camada Silver, incluindo:
- Conversão CSV para Parquet
- Tratamento de valores nulos
- Padronização de textos
- Feature Engineering
- Validação de integridade dos dados


Como utilizar:
DIRETO:
python src/silver.py

PROGRAMADO:
from src.silver import SilverDataPipeline

# Usando o nome padrão
pipeline = SilverDataPipeline()
df = pipeline.run_pipeline()

# Especificando um nome diferente
pipeline = SilverDataPipeline(output_filename=meu_arquivo.parquet)
df = pipeline.run_pipeline()


../data/
├── bronze/
│   ├── br_bd_diretorios_brasil_cnae_2.csv
│   ├── br_bd_diretorios_brasil_municipio.csv
│   └── br_bndes_operacoes_contratadas_operacoes_nao_automaticas.csv
└── silver/
    ├── br_bd_diretorios_brasil_cnae_2.parquet      # Conversão intermediária
    ├── br_bd_diretorios_brasil_municipio.parquet   # Conversão intermediária
    ├── br_bndes_operacoes_contratadas_operacoes_nao_automaticas.parquet  # Conversão intermediária
    └── bnds_silver.parquet                         # ✅ ARQUIVO FINAL PROCESSADO

"""

import os
import re
import unicodedata
import sys
import pandas as pd
import numpy as np
from typing import List, Optional, Union, Dict, Any
import logging
from pathlib import Path
from datetime import datetime

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class SilverDataPipeline:
    """
    Classe responsável pelo pipeline de transformação de dados da camada Silver.
    
    Esta classe encapsula todas as etapas de processamento necessárias para
    transformar dados brutos (camada Bronze) em dados enriquecidos e tratados
    (camada Silver), seguindo as melhores práticas de engenharia de dados.
    
    Attributes:
        bronze_dir (str): Caminho para o diretório de dados Bronze
        silver_dir (str): Caminho para o diretório de dados Silver
        output_filename (str): Nome do arquivo de saída
        df (pd.DataFrame): DataFrame principal das operações
    """
    
    def __init__(self, bronze_dir: Optional[str] = None, 
                 silver_dir: Optional[str] = None,
                 output_filename: str = "bnds_silver.parquet"):
        """
        Inicializa o pipeline com os diretórios de dados.
        
        Args:
            bronze_dir (str): Diretório de dados Bronze
            silver_dir (str): Diretório de dados Silver
            output_filename (str): Nome do arquivo Parquet de saída
        """
        # Determina o diretório base do projeto
        self.base_dir = self._get_project_root()
        
        # Define os diretórios de dados
        if bronze_dir is None:
            self.bronze_dir = os.path.join(self.base_dir, "data", "bronze")
        else:
            self.bronze_dir = bronze_dir
            
        if silver_dir is None:
            self.silver_dir = os.path.join(self.base_dir, "data", "silver")
        else:
            self.silver_dir = silver_dir
            
        self.output_filename = output_filename
        self.df = None
        
        self._validate_directories()
        logger.info(f"Pipeline inicializado - Bronze: {self.bronze_dir}, Silver: {self.silver_dir}")
        logger.info(f"Arquivo de saída: {output_filename}")
    
    def _get_project_root(self) -> str:
        """
        Determina o diretório raiz do projeto.
        
        Returns:
            str: Caminho absoluto para o diretório raiz
        """
        # Obtém o diretório do script atual
        script_path = Path(__file__).resolve()
        
        # Se estiver em src/, sobe um nível
        if script_path.parent.name == "src":
            root = script_path.parent.parent
        else:
            # Caso contrário, tenta encontrar pela estrutura comum
            root = script_path.parent
        
        # Verifica se existe o diretório data
        if not (root / "data").exists():
            # Tenta subir mais um nível
            parent = root.parent
            if (parent / "data").exists():
                root = parent
        
        logger.info(f"Diretório raiz do projeto: {root}")
        return str(root)
    
    def _validate_directories(self) -> None:
        """Valida se os diretórios de dados existem."""
        for directory in [self.bronze_dir, self.silver_dir]:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.warning(f"Diretório criado: {directory}")
                except Exception as e:
                    logger.error(f"Erro ao criar diretório {directory}: {str(e)}")
                    raise
    
    def list_bronze_files(self) -> List[str]:
        """
        Lista todos os arquivos disponíveis no diretório Bronze.
        
        Returns:
            List[str]: Lista de nomes de arquivos no diretório Bronze
        """
        try:
            files = [f for f in os.listdir(self.bronze_dir) 
                    if os.path.isfile(os.path.join(self.bronze_dir, f))]
            
            # Filtra apenas arquivos CSV
            csv_files = [f for f in files if f.endswith('.csv')]
            
            if csv_files:
                logger.info(f"Encontrados {len(csv_files)} arquivos CSV no diretório Bronze")
            else:
                logger.warning(f"Nenhum arquivo CSV encontrado em {self.bronze_dir}")
                logger.info(f"Arquivos encontrados: {files}")
                
            return csv_files
            
        except FileNotFoundError:
            logger.error(f"Diretório Bronze não encontrado: {self.bronze_dir}")
            return []
        except Exception as e:
            logger.error(f"Erro ao listar arquivos Bronze: {str(e)}")
            return []
    
    def convert_csv_to_parquet(self, file_list: List[str]) -> None:
        """
        Converte uma lista de arquivos CSV para formato Parquet.
        
        Args:
            file_list (List[str]): Lista de nomes de arquivos CSV para converter
        """
        if not file_list:
            logger.warning("Nenhum arquivo CSV para converter")
            return
            
        for arquivo in file_list:
            try:
                input_path = os.path.join(self.bronze_dir, arquivo)
                output_filename = os.path.splitext(arquivo)[0] + '.parquet'
                output_path = os.path.join(self.silver_dir, output_filename)
                
                # Verifica se o arquivo já foi convertido
                if os.path.exists(output_path):
                    logger.info(f"Arquivo {output_filename} já existe, pulando conversão")
                    continue
                
                # Leitura do CSV
                logger.info(f"Lendo arquivo: {arquivo}")
                df = pd.read_csv(input_path, low_memory=False)
                logger.info(f"Arquivo {arquivo} lido - {len(df)} linhas, {len(df.columns)} colunas")
                
                # Salvamento como Parquet
                df.to_parquet(output_path, index=False)
                logger.info(f"Arquivo convertido: {arquivo} -> {output_filename}")
                
            except Exception as e:
                logger.error(f"Erro ao converter {arquivo}: {str(e)}")
                raise
    
    def load_silver_data(self, filename: str) -> pd.DataFrame:
        """
        Carrega um arquivo Parquet da camada Silver.
        
        Args:
            filename (str): Nome do arquivo Parquet
            
        Returns:
            pd.DataFrame: DataFrame carregado
        """
        filepath = os.path.join(self.silver_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
        self.df = pd.read_parquet(filepath)
        logger.info(f"Dados carregados: {filename} - {len(self.df)} linhas, {len(self.df.columns)} colunas")
        return self.df
    
    def check_null_values(self, df: pd.DataFrame) -> Union[bool, pd.DataFrame]:
        """
        Verifica valores nulos no DataFrame e retorna análise detalhada.
        
        Args:
            df (pd.DataFrame): DataFrame a ser verificado
            
        Returns:
            Union[bool, pd.DataFrame]: False se não houver nulos, 
                                      DataFrame com análise se houver
        """
        total_nulos = df.isnull().sum().sort_values(ascending=False)
        total_nulos = total_nulos[total_nulos > 0]
        
        if total_nulos.empty:
            logger.info("Nenhum valor nulo encontrado")
            return False
        
        nulos_percent = ((total_nulos / df.shape[0]) * 100).round(2)
        resultado = pd.DataFrame({
            'Total_Nulos': total_nulos, 
            'Percentual_%': nulos_percent
        })
        
        logger.info(f"Valores nulos encontrados em {len(resultado)} colunas")
        return resultado
    
    def treat_null_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica tratamento de valores nulos conforme regras de negócio.
        
        Regras de negócio implementadas:
        1. tipo_excepcionalidade: Valores nulos indicam operação padrão (0)
        2. Instituição financeira: Nulo indica operação direta com BNDES
        3. id_municipio: Nulo preenchido como "NÃO INFORMADO"
        4. cnpj_cliente: Nulo preenchido com zeros
        5. situacao_contrato: Nulo preenchido como "OUTROS"
        6. tipo_fonte_recursos: Nulo preenchido como "OUTROS"
        
        Args:
            df (pd.DataFrame): DataFrame para tratamento
            
        Returns:
            pd.DataFrame: DataFrame com valores nulos tratados
        """
        df_copy = df.copy()
        
        # 1. Tratamento de excepcionalidade
        if 'tipo_excepcionalidade' in df_copy.columns:
            df_copy["tem_excepcionalidade"] = df_copy["tipo_excepcionalidade"].notna().astype(int)
            df_copy = df_copy.drop(columns=["tipo_excepcionalidade"])
            logger.info("Coluna 'tem_excepcionalidade' criada")
        
        # 2. Tratamento de instituição financeira
        if 'cnpj_instituicao_financeira_credenciada' in df_copy.columns:
            df_copy["cnpj_instituicao_financeira_credenciada"] = \
                df_copy["cnpj_instituicao_financeira_credenciada"].fillna("0000000000000.0")
        if 'nome_instituicao_financeira_credenciada' in df_copy.columns:
            df_copy["nome_instituicao_financeira_credenciada"] = \
                df_copy["nome_instituicao_financeira_credenciada"].fillna("OPERAÇÃO DIRETA")
        logger.info("Instituições financeiras preenchidas para operações diretas")
        
        # 3. Tratamento de campos de localização
        if 'id_municipio' in df_copy.columns:
            df_copy["id_municipio"] = df_copy["id_municipio"].fillna("NÃO INFORMADO")
        
        # 4. Tratamento de CNPJ do cliente
        if 'cnpj_cliente' in df_copy.columns:
            df_copy["cnpj_cliente"] = df_copy["cnpj_cliente"].fillna("000000000000.0")
        
        # 5. Tratamento de situação e fonte de recursos
        if 'situacao_contrato' in df_copy.columns:
            df_copy["situacao_contrato"] = df_copy["situacao_contrato"].fillna("OUTROS")
        if 'tipo_fonte_recursos' in df_copy.columns:
            df_copy["tipo_fonte_recursos"] = df_copy["tipo_fonte_recursos"].fillna("OUTROS")
        
        # 6. Remoção de colunas CNAE desnecessárias
        cnae_cols = ["classe_cnae", "subclasse_cnae", "grupo_cnae", 
                    "divisao_cnae", "secao_cnae"]
        cnae_cols_existentes = [col for col in cnae_cols if col in df_copy.columns]
        if cnae_cols_existentes:
            df_copy = df_copy.drop(columns=cnae_cols_existentes)
            logger.info(f"Colunas CNAE removidas: {cnae_cols_existentes}")
        
        logger.info("Tratamento de valores nulos concluído")
        return df_copy
    
    @staticmethod
    def normalize_text(value: Union[str, float, None]) -> Optional[str]:
        """
        Normaliza texto removendo acentos e convertendo para maiúsculas.
        
        Args:
            value: Valor a ser normalizado
            
        Returns:
            Optional[str]: Texto normalizado ou None se entrada for nula
        """
        if pd.isna(value):
            return value
        
        text = str(value).strip().upper()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = re.sub(r"\s+", " ", text)
        return text
    
    def standardize_text(self, df: pd.DataFrame, 
                        cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Padroniza colunas de texto com normalização.
        
        Args:
            df (pd.DataFrame): DataFrame a ser processado
            cols (Optional[List[str]]): Colunas a processar
            
        Returns:
            pd.DataFrame: DataFrame com texto padronizado
        """
        df_copy = df.copy()
        
        if cols is None:
            cols = df_copy.select_dtypes(include=["object", "string"]).columns.tolist()
        
        for col in cols:
            df_copy[col] = df_copy[col].map(self.normalize_text)
        
        logger.info(f"Textos padronizados em {len(cols)} colunas")
        return df_copy
    
    def convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte colunas de data para tipo datetime.
        
        Args:
            df (pd.DataFrame): DataFrame para conversão
            
        Returns:
            pd.DataFrame: DataFrame com datas convertidas
        """
        df_copy = df.copy()
        date_pattern = "data"
        date_cols = [col for col in df_copy.columns if date_pattern in col.lower()]
        
        for col in date_cols:
            df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
        
        if date_cols:
            logger.info(f"Colunas de data convertidas: {date_cols}")
        return df_copy
    
    def apply_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica feature engineering para enriquecimento dos dados.
        
        Features criadas:
        1. ano_contratacao: Ano da contratação
        2. mes_contratacao: Mês da contratação
        3. prazo_total_meses: Soma do prazo de carência e amortização
        4. grupo_taxa_juros: Categorização da taxa (BAIXA, MEDIA, ALTA)
        5. grupo_taxa_juros_ordinal: Codificação ordinal da taxa
        6. flag_apoio_direto: Indicador de apoio direto (1/0)
        7. flag_reembolsavel: Indicador de modalidade reembolsável (1/0)
        8. flag_cliente_publico: Indicador de cliente público (1/0)
        9. qtd_palavras_descricao: Quantidade de palavras na descrição
        10. porte_cliente_ordinal: Codificação ordinal do porte
        
        Args:
            df (pd.DataFrame): DataFrame para enriquecimento
            
        Returns:
            pd.DataFrame: DataFrame com features enriquecidas
        """
        df_copy = df.copy()
        
        # 1. Extração temporal
        if 'data_contratacao' in df_copy.columns:
            df_copy["ano_contratacao"] = df_copy["data_contratacao"].dt.year
            df_copy["mes_contratacao"] = df_copy["data_contratacao"].dt.month
        
        # 2. Cálculo de prazo
        if 'prazo_carencia' in df_copy.columns and 'prazo_amortizacao' in df_copy.columns:
            df_copy["prazo_total_meses"] = (df_copy["prazo_carencia"].fillna(0) + 
                                           df_copy["prazo_amortizacao"].fillna(0))
        
        # 3. Categorização de taxa de juros
        if 'taxa_juros' in df_copy.columns:
            conditions = [
                df_copy["taxa_juros"] < 5,
                (df_copy["taxa_juros"] >= 5) & (df_copy["taxa_juros"] <= 10),
                df_copy["taxa_juros"] > 10,
            ]
            categories = ["BAIXA", "MEDIA", "ALTA"]
            df_copy["grupo_taxa_juros"] = np.select(
                conditions, categories, default="SEM TAXA"
            )
            
            # 4. Codificação ordinal da taxa
            taxa_mapping = {"SEM TAXA": 0, "BAIXA": 1, "MEDIA": 2, "ALTA": 3}
            df_copy["grupo_taxa_juros_ordinal"] = df_copy["grupo_taxa_juros"].map(taxa_mapping)
        
        # 5. Flags binárias
        if 'forma_apoio' in df_copy.columns:
            df_copy["flag_apoio_direto"] = (df_copy["forma_apoio"] == "DIRETA").astype(int)
        if 'modalidade_apoio' in df_copy.columns:
            df_copy["flag_reembolsavel"] = (df_copy["modalidade_apoio"] == "REEMBOLSAVEL").astype(int)
        
        # 6. Flag cliente público
        if 'natureza_cliente' in df_copy.columns:
            public_pattern = "PUBLICA|PUBLICO"
            df_copy["flag_cliente_publico"] = (
                df_copy["natureza_cliente"]
                .fillna("")
                .str.contains(public_pattern, regex=True)
                .astype(int)
            )
        
        # 7. Quantidade de palavras
        if 'descricao_projeto' in df_copy.columns:
            df_copy["qtd_palavras_descricao"] = (
                df_copy["descricao_projeto"]
                .fillna("")
                .str.split()
                .str.len()
            )
        
        # 8. Codificação ordinal do porte
        if 'porte_cliente' in df_copy.columns:
            porte_mapping = {
                "SEM PORTE": 0, "MICRO": 1, "PEQUENA": 2, 
                "MEDIA": 3, "GRANDE": 4
            }
            df_copy["porte_cliente_ordinal"] = df_copy["porte_cliente"].map(porte_mapping)
        
        logger.info("Feature Engineering concluído")
        return df_copy
    
    def validate_data_integrity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida a integridade dos dados processados.
        
        Args:
            df (pd.DataFrame): DataFrame a validar
            
        Returns:
            Dict[str, Any]: Dicionário com métricas de validação
        """
        validation_results = {
            "total_linhas": len(df),
            "total_colunas": len(df.columns),
            "valores_ausentes": df.isnull().sum().sum(),
            "linhas_duplicadas": df.duplicated().sum(),
        }
        
        # Validação de integridade financeira
        if 'valor_contratado' in df.columns and 'valor_desembolsado' in df.columns:
            valor_total_contratado = df["valor_contratado"].sum()
            valor_total_desembolsado = df["valor_desembolsado"].sum()
            
            validation_results.update({
                "valor_total_contratado": f"R$ {valor_total_contratado:,.2f}",
                "valor_total_desembolsado": f"R$ {valor_total_desembolsado:,.2f}",
                "taxa_execucao": f"{(valor_total_desembolsado/valor_total_contratado*100):.2f}%"
            })
        
        logger.info(f"Validação de integridade concluída - {len(df)} registros")
        return validation_results
    
    def save_final_dataframe(self, df: pd.DataFrame) -> str:
        """
        Salva o DataFrame processado no formato Parquet.
        
        Args:
            df (pd.DataFrame): DataFrame a ser salvo
            
        Returns:
            str: Caminho do arquivo salvo
        """
        output_path = os.path.join(self.silver_dir, self.output_filename)
        df.to_parquet(output_path, index=False)
        logger.info(f"Dados processados salvos em: {output_path}")
        return output_path
    
    def run_pipeline(self, filename: Optional[str] = None) -> pd.DataFrame:
        """
        Executa o pipeline completo de transformação de dados.
        
        Args:
            filename (Optional[str]): Nome específico do arquivo a processar
            
        Returns:
            pd.DataFrame: DataFrame processado da camada Silver
        """
        try:
            # 1. Listar e converter arquivos
            bronze_files = self.list_bronze_files()
            
            if not bronze_files:
                logger.error("Nenhum arquivo CSV encontrado no diretório Bronze")
                logger.info(f"Verifique se os arquivos estão em: {self.bronze_dir}")
                return pd.DataFrame()
            
            # Converte arquivos CSV para Parquet
            self.convert_csv_to_parquet(bronze_files)
            
            # 2. Encontrar o arquivo de operações
            if filename is None:
                # Padrões para encontrar o arquivo de operações
                patterns = ["operacoes_contratadas", "bndes_operacoes"]
                silver_files = [f for f in os.listdir(self.silver_dir) 
                               if f.endswith('.parquet')]
                
                filename = None
                for pattern in patterns:
                    matching = [f for f in silver_files if pattern in f]
                    if matching:
                        filename = matching[0]
                        break
                
                if filename is None and silver_files:
                    # Usar o primeiro arquivo disponível
                    filename = silver_files[0]
                
                if filename is None:
                    # Tentar usar o nome original do CSV
                    csv_files = [f for f in bronze_files if "operacoes" in f]
                    if csv_files:
                        filename = csv_files[0].replace('.csv', '.parquet')
            
            if filename is None:
                logger.error("Não foi possível encontrar o arquivo de operações")
                return pd.DataFrame()
            
            # 3. Processar dados
            logger.info(f"Processando arquivo: {filename}")
            self.df = self.load_silver_data(filename)
            
            # 4. Verificar e tratar nulos
            null_analysis = self.check_null_values(self.df)
            if null_analysis is not False:
                logger.info(f"Análise de nulos:\n{null_analysis}")
                self.df = self.treat_null_values(self.df)
            
            # 5. Conversão de datas
            self.df = self.convert_date_columns(self.df)
            
            # 6. Padronização de textos
            self.df = self.standardize_text(self.df)
            
            # 7. Feature Engineering
            self.df = self.apply_feature_engineering(self.df)
            
            # 8. Validação final
            validation = self.validate_data_integrity(self.df)
            logger.info(f"Métricas finais:\n{validation}")
            
            # 9. Salvar dados processados
            output_path = self.save_final_dataframe(self.df)
            
            logger.info(f"Pipeline concluído com sucesso - Arquivo salvo em: {output_path}")
            return self.df
            
        except Exception as e:
            logger.error(f"Erro durante execução do pipeline: {str(e)}")
            raise


def main():
    """
    Função principal para execução do pipeline.
    """
    # Inicializa o pipeline com o nome do arquivo de saída desejado
    pipeline = SilverDataPipeline(output_filename="bnds_silver.parquet")
    
    logger.info("Iniciando pipeline de transformação Silver...")
    
    try:
        result_df = pipeline.run_pipeline()
        
        if result_df.empty:
            print("\n❌ Nenhum dado foi processado. Verifique os arquivos na pasta data/bronze/")
            return
        
        # Sumário final
        print("\n" + "="*60)
        print("RESUMO DA TRANSFORMAÇÃO SILVER")
        print("="*60)
        print(f"Arquivo gerado: bnds_silver.parquet")
        print(f"Localização: {pipeline.silver_dir}/bnds_silver.parquet")
        print(f"Total de registros: {len(result_df):,}")
        print(f"Total de colunas: {len(result_df.columns)}")
        
        if 'valor_contratado' in result_df.columns:
            total = result_df['valor_contratado'].sum()
            print(f"Valor total contratado: R$ {total:,.2f}")
        
        if 'valor_desembolsado' in result_df.columns:
            total_desemb = result_df['valor_desembolsado'].sum()
            print(f"Valor total desembolsado: R$ {total_desemb:,.2f}")
        
        if 'data_contratacao' in result_df.columns:
            min_date = result_df['data_contratacao'].min()
            max_date = result_df['data_contratacao'].max()
            if pd.notna(min_date) and pd.notna(max_date):
                print(f"Período: {min_date.date()} a {max_date.date()}")
        
        # Verificar colunas criadas pelo feature engineering
        feature_cols = ['ano_contratacao', 'mes_contratacao', 'prazo_total_meses', 
                       'grupo_taxa_juros', 'flag_apoio_direto', 'flag_reembolsavel',
                       'flag_cliente_publico', 'qtd_palavras_descricao', 
                       'porte_cliente_ordinal']
        features_criadas = [col for col in feature_cols if col in result_df.columns]
        print(f"Features criadas: {len(features_criadas)}")
        
        
    except Exception as e:
        logger.error(f"Falha no pipeline: {str(e)}")
        print(f"\n❌ Erro durante execução: {str(e)}")
        raise


if __name__ == "__main__":
    main()