# data_factory_project/main.py

import os
from src.database.db_manager import DBManager
from src.csv_processor.csv_extractor import CSVExtractor
from src.utils.logger_config import setup_logger

# Configura o logger
logger = setup_logger()

def run_csv_extraction():
    """
    Executa o processo de extração e carregamento de dados CSV.
    """
    logger.info("Iniciando o processo de extração de CSV.")

    # Define o caminho para o banco de dados
    db_path = os.path.join('data', 'data_factory.db')
    csv_file_path = os.path.join('data', 'Lista_de_Alarmes_AGV.csv')

    # Garante que o diretório 'data' existe
    os.makedirs('data', exist_ok=True)

    try:
        # Inicializa o DBManager e cria as tabelas se não existirem
        db_manager = DBManager(db_path)
        db_manager.create_tables()
        logger.info("Tabelas do banco de dados verificadas/criadas.")

        # Inicializa o CSVExtractor
        csv_extractor = CSVExtractor(db_manager)

        # Executa a extração e carregamento
        csv_extractor.extract_and_load(csv_file_path)
        logger.info("Extração e carregamento de CSV concluídos com sucesso.")

    except Exception as e:
        logger.error(f"Erro durante a execução do extrator CSV: {e}", exc_info=True)

if __name__ == "__main__":
    run_csv_extraction()
