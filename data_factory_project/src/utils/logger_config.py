import logging
import os
from datetime import datetime

def setup_logger(name="data_factory_logger", log_dir="logs"):
    """
    Configura um logger para o projeto, com saída para console e arquivo.

    Args:
        name (str): Nome do logger.
        log_dir (str): Diretório onde os arquivos de log serão salvos.
    """
    # Garante que o diretório de logs exista
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False # Evita que logs sejam enviados para loggers pai

    # Formato do log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler para console
    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    # Handler para arquivo (um novo arquivo por dia)
    log_file_name = datetime.now().strftime("app_%Y-%m-%d.log")
    log_file_path = os.path.join(log_dir, log_file_name)

    # Verifica se já existe um FileHandler para evitar duplicidade
    if not any(isinstance(handler, logging.FileHandler) and handler.baseFilename == os.path.abspath(log_file_path) for handler in logger.handlers):
        fh = logging.FileHandler(log_file_path, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

# Exemplo de uso (opcional, para testar o logger)
if __name__ == "__main__":
    logger = setup_logger()
    logger.info("Este é um log de informação.")
    logger.warning("Este é um log de aviso.")
    logger.error("Este é um log de erro.")