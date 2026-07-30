import sqlite3
from src.utils.logger_config import setup_logger

logger = setup_logger()

class DBManager:
    def __init__(self, db_path="data/data_factory.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        logger.info(f"DBManager inicializado com banco de dados: {self.db_path}")

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Conectado ao banco de dados: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Conexão com o banco de dados fechada.")

    def create_tables(self):
        """Cria as tabelas necessárias se não existirem."""
        if not self.conn:
            logger.error("Não há conexão com o banco de dados. Chame connect() primeiro.")
            raise ConnectionError("Não há conexão com o banco de dados. Chame connect() primeiro.")

        try:
            # Tabela para sistemas afetados (ex: Powertrain, Lift, Navigation)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sistemas_afetados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL
                );
            """)
            logger.info("Tabela 'sistemas_afetados' verificada/criada.")

            # Tabela para dispositivos (ex: TL1, FC1, BS1, Scanner Front)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS dispositivos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag TEXT UNIQUE NOT NULL,
                    descricao TEXT
                );
            """)
            logger.info("Tabela 'dispositivos' verificada/criada.")

            # Tabela principal de alarmes
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS alarmes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topico_limpo TEXT,
                    codigo TEXT NOT NULL,
                    tipo TEXT,
                    descricao TEXT NOT NULL,
                    causa_provavel TEXT,
                    solucao_sugerida TEXT,
                    tag_dispositivo_associada TEXT, -- Pode ser FK para 'dispositivos' ou apenas texto
                    origem_documento TEXT,
                    FOREIGN KEY (tag_dispositivo_associada) REFERENCES dispositivos(tag)
                );
            """)
            logger.info("Tabela 'alarmes' verificada/criada.")

            self.conn.commit()
            logger.info("Todas as tabelas foram verificadas/criadas com sucesso.")
        except sqlite3.Error as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise

    def insert_alarmes(self, alarmes_data: list[dict]):
        """
        Insere uma lista de alarmes no banco de dados.
        Espera uma lista de dicionários, onde cada dicionário representa um alarme.
        """
        if not self.conn:
            logger.error("Não há conexão com o banco de dados. Chame connect() primeiro.")
            raise ConnectionError("Não há conexão com o banco de dados. Chame connect() primeiro.")

        try:
            for alarme in alarmes_data:
                # Inserir ou obter ID do dispositivo
                tag_dispositivo = alarme.get('tag_dispositivo_associada')
                if tag_dispositivo:
                    self.cursor.execute("INSERT OR IGNORE INTO dispositivos (tag) VALUES (?)", (tag_dispositivo,))
                    # Não precisamos do ID do dispositivo para a tabela alarmes, pois a FK é por TAG (texto)

                self.cursor.execute("""
                    INSERT INTO alarmes (
                        topico_limpo, codigo, tipo, descricao,
                        causa_provavel, solucao_sugerida, tag_dispositivo_associada,
                        origem_documento
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alarme.get('topico_limpo'),
                    alarme.get('codigo'),
                    alarme.get('tipo'),
                    alarme.get('descricao'),
                    alarme.get('causa_provavel'),
                    alarme.get('solucao_sugerida'),
                    alarme.get('tag_dispositivo_associada'),
                    alarme.get('origem_documento')
                ))
            self.conn.commit()
            logger.info(f"{len(alarmes_data)} alarmes inseridos com sucesso.")
        except sqlite3.Error as e:
            logger.error(f"Erro ao inserir alarmes: {e}")
            raise

# Exemplo de uso (para testes, se necessário)
if __name__ == "__main__":
    db_manager = DBManager("test_data_factory.db")
    try:
        db_manager.connect()
        db_manager.create_tables()

        # Exemplo de dados para inserção
        sample_alarmes = [
            {
                'topico_limpo': 'CAN OPEN',
                'codigo': '001',
                'tipo': 'WARNING',
                'descricao': 'CAN OPEN: BOOTING POWERTRAIN',
                'causa_provavel': 'Falha na inicialização',
                'solucao_sugerida': 'Verificar conexão CAN',
                'tag_dispositivo_associada': 'POWERTRAIN',
                'origem_documento': 'Lista_de_Alarmes_AGV.csv'
            },
            {
                'topico_limpo': 'GENERALS',
                'codigo': '002',
                'tipo': 'INFO',
                'descricao': 'GENERALS: IN MANUAL MODE',
                'causa_provavel': 'Operação manual',
                'solucao_sugerida': 'Nenhuma',
                'tag_dispositivo_associada': None,
                'origem_documento': 'Lista_de_Alarmes_AGV.csv'
            }
        ]
        db_manager.insert_alarmes(sample_alarmes)
        logger.info("Exemplo de inserção concluído.")

    except Exception as e:
        logger.error(f"Erro no exemplo de uso: {e}")
    finally:
        db_manager.close()
