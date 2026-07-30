# run_csv_extraction.py
import os
from src.csv_processor.csv_extractor import CSVExtractor
from src.database.db_manager import DBManager
from src.utils.logger_config import setup_logger

# Configura o logger
logger = setup_logger()

def main():
    # Define o caminho base do projeto
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Caminho para o arquivo CSV
    csv_file_path = os.path.join(base_dir, 'data', 'raw_csvs', 'Lista_de_Alarmes_AGV.csv')

    # Caminho para o banco de dados SQLite
    db_path = os.path.join(base_dir, 'data', 'data_factory.db')

    logger.info(f"Iniciando extração de CSV do arquivo: {csv_file_path}")
    logger.info(f"Conectando ao banco de dados: {db_path}")

    db_manager = None
    try:
        db_manager = DBManager(db_path)
        db_manager.connect()
        db_manager.create_tables() # Garante que a tabela 'alarmes' existe

        extractor = CSVExtractor(db_manager)
        extractor.extract_and_load(csv_file_path)

        logger.info("Extração e carregamento do CSV concluídos com sucesso.")

    except FileNotFoundError:
        logger.error(f"Erro: Arquivo CSV não encontrado em {csv_file_path}. Verifique o caminho.")
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a extração ou carregamento do CSV: {e}", exc_info=True)
    finally:
        if db_manager:
            db_manager.close()
            logger.info("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()

