import os
from src.database.db_manager import DBManager
from src.csv_processor.csv_extractor import CSVExtractor
from src.utils.logger_config import setup_logger

logger = setup_logger()

def main():
    # Caminho para o arquivo CSV de exemplo
    # Certifique-se de que o arquivo 'Lista_de_Alarmes_AGV.csv' está na pasta 'data/raw/'
    csv_file_path = os.path.join('data', 'raw', 'Lista_de_Alarmes_AGV.csv')

    # Inicializa o DBManager
    db_manager = DBManager(db_path=os.path.join('data', 'data_factory.db'))

    # Conecta e cria as tabelas se não existirem
    try:
        db_manager.connect()
        db_manager.create_tables()
        logger.info("Tabelas do banco de dados verificadas/criadas.")
    except Exception as e:
        logger.error(f"Erro ao conectar ou criar tabelas no banco de dados: {e}")
        return
    finally:
        db_manager.close() # Fecha a conexão após criar as tabelas

    # Inicializa o CSVExtractor
    csv_extractor = CSVExtractor(db_manager)

    # Executa a extração e carregamento
    logger.info(f"Iniciando extração do CSV: {csv_file_path}")
    csv_extractor.extract_and_load(csv_file_path)
    logger.info("Extração do CSV concluída.")

if __name__ == "__main__":
    main()