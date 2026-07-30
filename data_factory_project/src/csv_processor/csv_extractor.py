import pandas as pd
import re
import os
from typing import Optional
from src.utils.logger_config import setup_logger
from src.database.db_manager import DBManager

logger = setup_logger()

class CSVExtractor:
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        logger.info("CSVExtractor inicializado.")

    def _clean_topic(self, topic: str) -> str:
        """
        Remove a numeração inicial do tópico (ex: "6.1.1 ANS" -> "ANS").
        """
        if pd.isna(topic):
            return ""
        # Remove a numeração e espaços extras
        cleaned_topic = re.sub(r'^\d+(\.\d+)*\s*', '', str(topic)).strip()
        return cleaned_topic

    def _extract_device_tag(self, description: str) -> Optional[str]:
        """
        Extrai a TAG do dispositivo associada a partir da descrição do alarme.
        Prioriza padrões específicos e, se não encontrar, tenta padrões mais genéricos.
        """
        if pd.isna(description):
            return None

        description = str(description).upper()

        # --- Padrões Específicos (Ordem importa: mais específicos primeiro) ---

        # 1. Padrões de "COMMUNICATION FAILURE - [TAG]" ou "BOOTING [TAG]"
        # Ex: 'SYSTEM PROFINET: 80FQ1 COMMUNICATION FAILURE - SCANNER FRONT' -> 'SCANNER FRONT'
        # Ex: 'CAN OPEN: BOOTING POWERTRAIN' -> 'POWERTRAIN'
        match_comm_boot = re.search(r'(?:COMMUNICATION FAILURE -|BOOTING)\s*([A-Z0-9\s-]+)$', description)
        if match_comm_boot:
            return match_comm_boot.group(1).strip()

        # 2. Padrões de "WHEELS [FRONT/REAR] STEERING"
        # Ex: 'WHEELS FRONT STEERING: RIGHT STROKE' -> 'WHEELS FRONT STEERING'
        match_wheels_steering = re.search(r'^(WHEELS\s(?:FRONT|REAR)\sSTEERING)', description)
        if match_wheels_steering:
            return match_wheels_steering.group(1).strip()

        # 3. Padrões de TAGs conhecidas no início ou meio da descrição
        # Ex: 'SYSTEM PROFINET: 80FQ1...' -> '80FQ1'
        # Ex: 'NAVIGATION: ANTICOLLISION ON' -> 'ANTICOLLISION'
        # Ex: 'NAVIGATION: PRECISE POSITIONING NOT REACHED' -> 'POSITIONING'
        # Ex: 'NAVIGATION: CHECKPOINTFAILED' -> 'NAVIGATION' (ou 'CHECKPOINT' se for o caso)
        # Ex: 'NAVIGATION: LINE LOST' -> 'NAVIGATION'
        # Ex: 'SYSTEM: SYSTEM BOOTING' -> 'SYSTEM'
        # Ex: 'GENERALS: BYPASS KEY ACTIVATED' -> 'BYPASS'
        # Ex: 'NAVIGATION: DATA NOT VALID FROM MC' -> 'MC'
        
        # ... (código anterior) ...

        # 3. Padrões de TAGs conhecidas no início ou meio da descrição
        # Ex: 'SYSTEM PROFINET: 80FQ1...' -> '80FQ1'
        # ...
        patterns_specific_keywords = [
            r'\b(80FQ1)\b', r'\b(80FQ2)\b', r'\b(91XF2)\b', r'\b(75BS2)\b', r'\b(75BS4)\b', # Códigos específicos
            r'\b(SCANNER FRONT)\b', r'\b(SCANNER REAR)\b', r'\b(SCALANCE)\b',
            r'\b(ENCODER FRONT)\b', r'\b(ENCODER REAR)\b',
            r'\b(ANTICOLLISION)\b', r'\b(POSITIONING)\b', r'\b(CHECKPOINT)\b',
            r'\b(BYPASS)\b', r'\b(MC)\b', r'\b(SYSTEM)\b', r'\b(NAVIGATION)\b',
            r'\b(GENERALS)\b', r'\b(POWERTRAIN)\b', r'\b(LIFT)\b',
            r'\b(STO)\b', # <-- ADICIONE ESTA LINHA
            r'\b(TL\d+)\b', r'\b(FC\d+)\b', r'\b(BS\d+)\b', r'\b(WF\d+)\b', r'\b(MA\d+)\b',
            r'\b(QA\d+)\b', r'\b(BG\d+)\b', r'\b(SF\d+)\b', r'\b(XD\d+)\b', r'\b(XG\d+)\b',
            r'\b(KF\d{3}\.\d{2})\b', r'\b(KF\d{3})\b', r'\b(FN\d+)\b', r'\b(FQ\d+)\b',
            r'\b(PJ\d+)\b', r'\b(QB\d+)\b', r'\b(TB\d+)\b', r'\b(WG\d+)\b', r'\b(D\d+)\b',
            r'\b(R\d+)\b', r'\b(XF\d+)\b', r'\b(BY\d+)\b', r'\b(PH\d+)\b', r'\b(GB\d+)\b',
            r'\b(PF\d+)\b', r'\b(SZ\d+)\b', r'\b(U[C]?\d+)\b', r'\b(RCAN\d+)\b',
            r'\b(PLS\sFRONT)\b', r'\b(PLS\sREAR)\b', r'\b(PGV)\b', r'\b(ANS)\b',
            r'\b(BATTERY)\b', r'\b(FRONT\sLEFT)\b', r'\b(REAR\sRIGHT)\b',
            r'\b(TABLE\sLEFT)\b', r'\b(TABLE\sRIGHT)\b', r'\b(STEERING\sFRONT)\b',
            r'\b(STEERING\sREAR)\b', r'\b(LIFT\s-\sFL)\b', r'\b(LIFT\s-\sFR)\b',
            r'\b(LIFT\s-\sRL)\b', r'\b(LIFT\s-\sRR)\b', r'\b(BCC)\b', r'\b(DB9)\b',
            r'\b(XDPE)\b', r'\b(PLACA\sDE\sDADOS)\b',
            r'=(?:[A-Z0-9]+)\+P\d+-(BS\d+)', # Ex: =001FTF001+P101-BS1 -> BS1
        ]

        # ... (restante do código) ...

        for pattern in patterns_specific_keywords:
            match = re.search(pattern, description)
            if match:
                # Para o padrão de =...-BSx, queremos o grupo 1 (BSx)
                if pattern == r'=(?:[A-Z0-9]+)\+P\d+-(BS\d+)':
                    return match.group(1).strip()
                return match.group(0).strip()

        # --- Padrões Genéricos de Fallback (se nada específico for encontrado) ---

        # Tenta capturar a primeira palavra antes de ':' ou '-' como uma TAG
        # Ex: 'CAN OPEN: BOOTING POWERTRAIN' -> 'CAN OPEN' (se os outros não pegarem)
        match_prefix = re.match(r'([A-Z0-9\s]+?)(?:\s*[:\-–—,.]|$)', description)
        if match_prefix:
            potential_tag = match_prefix.group(1).strip()
            # Evita que palavras muito comuns sejam consideradas TAGs genéricas
            common_words = ["CAN OPEN", "GENERALS", "NAVIGATION", "SYSTEM", "WHEELS", "FRONT", "REAR", "STEERING",
                            "LEFT", "RIGHT", "STROKE", "DATA", "NOT", "VALID", "FROM", "MC", "LINE", "LOST", "FOUND",
                            "ANTICOLLISION", "ON", "CHECKPOINTFAILED", "PRECISE", "POSITIONING", "REACHED", "BOOTING",
                            "COMMUNICATION", "FAILURE", "PROFINET", "KEY", "ACTIVATED", "BYPASS", "SYNCHRONIZED",
                            "IN", "MANUAL", "AUTOMATIC", "MODE", "AND", "AUTOSTART", "POWER", "LIFT", "SENSOR",
                            "MODULE", "CONTROL", "UNIT", "ERROR", "ALARM", "WARNING", "STATUS", "MESSAGE", "FAULT",
                            "PROBLEM", "ISSUE", "DETECTED", "REPORTED", "FAILURE", "MALFUNCTION", "OVERLOAD",
                            "UNDERVOLTAGE", "OVERCURRENT", "TEMPERATURE", "LIMIT", "SPEED", "PHASE", "EMERGENCY",
                            "BATTERY", "SAVE", "OTHER", "BLANK", "SEGMENT", "VELOCITY", "STALL", "NOT", "OPERATIONAL",
                            "CRITICAL", "HOST", "OVER", "UNDER", "BAD", "PARAMETER", "REGEN", "MOVE", "LOW",
                            "ABSOLUTE", "ABS", "TABLE", "GOVERNANCE", "RULE", "OF", "LAW", "HUMAN", "RIGHTS",
                            "JUSTICE", "EQUALITY", "INCLUSION", "DIVERSITY", "EQUITY", "ACCESSIBILITY", "SOCIAL",
                            "IMPACT", "SUSTAINABILITY", "DEVELOPMENT", "GOALS", "SDGS", "POVERTY", "ALLEVIATION",
                            "HUNGER", "ERADICATION", "GOOD", "HEALTH", "WELLBEING", "QUALITY", "EDUCATION", "GENDER",
                            "EQUALITY", "CLEAN", "WATER", "SANITATION", "AFFORDABLE", "CLEAN", "ENERGY", "DECENT",
                            "WORK", "ECONOMIC", "GROWTH", "INDUSTRY", "INNOVATION", "INFRASTRUCTURE", "REDUCED",
                            "INEQUALITIES", "SUSTAINABLE", "CITIES", "COMMUNITIES", "RESPONSIBLE", "CONSUMPTION",
                            "PRODUCTION", "CLIMATE", "ACTION", "LIFE", "BELOW", "WATER", "LIFE", "ON", "LAND",
                            "PEACE", "JUSTICE", "STRONG", "INSTITUTIONS", "PARTNERSHIPS", "FOR", "THE", "GOALS"]

            # Se a TAG potencial não for uma palavra comum, retorna ela
            if potential_tag and not any(word == potential_tag for word in common_words):
                return potential_tag
            # Se a TAG potencial for uma das palavras comuns, mas for "GENERALS", "NAVIGATION", "SYSTEM", "BYPASS", "ANTICOLLISION", "POSITIONING", "MC"
            # que você indicou como TAGs válidas, então retorna.
            if potential_tag in ["GENERALS", "NAVIGATION", "SYSTEM", "BYPASS", "ANTICOLLISION", "POSITIONING", "MC", "WHEELS"]:
                return potential_tag

        logger.warning(f"Nenhuma TAG de dispositivo encontrada para a descrição: '{description}'")
        return None

        """
        Extrai a TAG do dispositivo associada a partir da descrição do alarme.
        Prioriza padrões específicos e, se não encontrar, tenta padrões mais genéricos.
        """
        if pd.isna(description):
            return None

        description = str(description).upper()

        # --- Novos padrões adicionados/ajustados para capturar casos como 'POWERTRAIN' e 'LIFT' ---

        # Padrão para "BOOTING [TAG]" ou "COMMUNICATION FAILURE - [TAG]"
        # Tenta capturar a última palavra ou grupo de palavras após "BOOTING" ou "COMMUNICATION FAILURE -"
        match_booting_comm_failure = re.search(r'(?:BOOTING|COMMUNICATION FAILURE -)\s*([A-Z0-9\s-]+)$', description)
        if match_booting_comm_failure:
            # Retorna o grupo capturado, que é a TAG
            return match_booting_comm_failure.group(1).strip()

        # --- Fim dos novos padrões ---


        # Lista de padrões de TAGs conhecidas ou formatos comuns (MANTENHA O RESTO DA LISTA AQUI)
        patterns = [
            r'\b(TL\d+)\b',  # Ex: TL1, TL10
            r'\b(FC\d+)\b',  # Ex: FC1, FC2
            r'\b(BS\d+)\b',  # Ex: BS1, BS2
            r'\b(WF\d+)\b',  # Ex: WF1, WF100
            r'\b(MA\d+)\b',  # Ex: MA1
            r'\b(QA\d+)\b',  # Ex: QA1
            r'\b(BG\d+)\b',  # Ex: BG1
            r'\b(SF\d+)\b',  # Ex: SF1
            r'\b(XD\d+)\b',  # Ex: XD1
            r'\b(XG\d+)\b',  # Ex: XG1, XG100
            r'\b(KF\d{3}\.\d{2})\b', # Ex: KF001.10
            r'\b(KF\d{3})\b', # Ex: KF001
            r'\b(FN\d+)\b',  # Ex: FN1
            r'\b(FQ\d+)\b',  # Ex: FQ1
            r'\b(PJ\d+)\b',  # Ex: PJ1
            r'\b(QB\d+)\b',  # Ex: QB1
            r'\b(TB\d+)\b',  # Ex: TB1
            r'\b(WG\d+)\b',  # Ex: WG1, WG10
            r'\b(D\d+)\b',   # Ex: D1
            r'\b(R\d+)\b',   # Ex: R1
            r'\b(XF\d+)\b',  # Ex: XF1, XF100
            r'\b(BY\d+)\b',  # Ex: BY1
            r'\b(PH\d+)\b',  # Ex: PH1
            r'\b(GB\d+)\b',  # Ex: GB1
            r'\b(PF\d+)\b',  # Ex: PF1
            r'\b(SZ\d+)\b',  # Ex: SZ1
            r'\b(U[C]?\d+)\b', # Ex: U1, UC1
            r'\b(RCAN\d+)\b', # Ex: RCAN1
            r'\b(PLS\sFRONT)\b', # Ex: PLS FRONT
            r'\b(PLS\sREAR)\b',  # Ex: PLS REAR
            r'\b(PGV)\b',    # Ex: PGV
            r'\b(ANS)\b',    # Ex: ANS
            r'\b(BATTERY)\b',# Ex: BATTERY
            r'\b(FRONT\sLEFT)\b', # Ex: FRONT LEFT
            r'\b(REAR\sRIGHT)\b', # Ex: REAR RIGHT
            r'\b(TABLE\sLEFT)\b', # Ex: TABLE LEFT
            r'\b(TABLE\sRIGHT)\b',# Ex: TABLE RIGHT
            r'\b(STEERING\sFRONT)\b', # Ex: STEERING FRONT
            r'\b(STEERING\sREAR)\b',  # Ex: STEERING REAR
            r'\b(LIFT\s-\sFL)\b', # Ex: LIFT - FL
            r'\b(LIFT\s-\sFR)\b', # Ex: LIFT - FR
            r'\b(LIFT\s-\sRL)\b', # Ex: LIFT - RL
            r'\b(LIFT\s-\sRR)\b', # Ex: LIFT - RR
            r'\b(BCC)\b',    # Ex: BCC
            r'\b(DB9)\b',    # Ex: DB9
            r'\b(XDPE)\b',   # Ex: XDPE
            r'\b(PLACA\sDE\sDADOS)\b', # Ex: PLACA DE DADOS
            r'=(?:[A-Z0-9]+)\+P\d+-(BS\d+)', # Ex: =001FTF001+P101-BS1 -> BS1
        ]

        # ... (o restante da sua função _extract_device_tag permanece inalterado) ...

        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                # Para o padrão de =...-BSx, queremos o grupo 1 (BSx)
                if pattern == r'=(?:[A-Z0-9]+)\+P\d+-(BS\d+)':
                    return match.group(1).strip()
                return match.group(0).strip()

        # Padrão genérico de fallback: tenta capturar a primeira sequência de letras/números
        # que pareça uma TAG no início da descrição ou após certos delimitadores.
        match_generic = re.match(r'([A-Z0-9\s\-_]+?)(?:\s*[:\-–—,.]|$)', description)
        if match_generic:
            potential_tag = match_generic.group(1).strip()
            # Filtra palavras comuns que não são TAGs
            common_words = ["FAULT", "ERROR", "WARNING", "DRIVE", "MOTOR", "LIFT", "POSITION", "ENCODER",
                            "CURRENT", "VOLTAGE", "TEMPERATURE", "SAFE", "TORQUE", "MODULE", "LIMIT",
                            "SPEED", "PHASE", "EMERGENCY", "BATTERY", "SAVE", "OTHER", "BLANK", "SEGMENT",
                            "VELOCITY", "POWER", "STALL", "NOT", "OPERATIONAL", "CRITICAL", "HOST", "OVER",
                            "UNDER", "BAD", "PARAMETER", "REGEN", "MOVE", "LOW", "ABSOLUTE", "ABS", "FRONT",
                            "REAR", "LEFT", "RIGHT", "TABLE", "CAN", "OPEN", "POWERTRAIN", "BREAKER", "DISARMED",
                            "FEEDBACK", "AUTOMATIC", "CHARGER", "BUTTON", "RELEASED", "PANELS", "CLOSED",
                            "STEERING", "SYSTEM", "GENERALS", "NAVIGATION", "SECURITY", "DIRECTION", "ELEVATION",
                            "AGV", "VEHICLE", "CONTROL", "UNIT", "COMMUNICATION", "SENSOR", "LASER", "SCANNER",
                            "GOVERNANCE", "RULE", "OF", "LAW", "HUMAN", "RIGHTS", "JUSTICE", "EQUALITY",
                            "INCLUSION", "DIVERSITY", "EQUITY", "ACCESSIBILITY", "SOCIAL", "IMPACT",
                            "SUSTAINABILITY", "DEVELOPMENT", "GOALS", "SDGS", "POVERTY", "ALLEVIATION", "HUNGER",
                            "ERADICATION", "GOOD", "HEALTH", "WELLBEING", "QUALITY", "EDUCATION", "GENDER",
                            "EQUALITY", "CLEAN", "WATER", "SANITATION", "AFFORDABLE", "CLEAN", "ENERGY",
                            "DECENT", "WORK", "ECONOMIC", "GROWTH", "INDUSTRY", "INNOVATION", "INFRASTRUCTURE",
                            "REDUCED", "INEQUALITIES", "SUSTAINABLE", "CITIES", "COMMUNITIES", "RESPONSIBLE",
                            "CONSUMPTION", "PRODUCTION", "CLIMATE", "ACTION", "LIFE", "BELOW", "WATER", "LIFE",
                            "ON", "LAND", "PEACE", "JUSTICE", "STRONG", "INSTITUTIONS", "PARTNERSHIPS", "FOR",
                            "THE", "GOALS"]

            if potential_tag and not any(word in potential_tag for word in common_words):
                return potential_tag

        logger.warning(f"Nenhuma TAG de dispositivo encontrada para a descrição: '{description}'")
        return None

    def extract_and_load(self, csv_filepath: str):
        """
        Extrai dados de um arquivo CSV, padroniza-os e os carrega no banco de dados.
        """
        if not os.path.exists(csv_filepath):
            logger.error(f"Arquivo CSV não encontrado: {csv_filepath}")
            raise FileNotFoundError(f"O arquivo CSV especificado não foi encontrado: {csv_filepath}")

        logger.info(f"Lendo arquivo CSV: {csv_filepath}")
        try:
            df = pd.read_csv(csv_filepath, sep=';', encoding='latin1') # ou 'cp1252'
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo CSV '{csv_filepath}': {e}")
            raise

        # Renomear colunas para corresponder ao esquema do banco de dados
        df.rename(columns={
            'ID': 'codigo',
            'Classe': 'tipo',
            'Descrição': 'descricao',
            'Possíveis Causas': 'causa_provavel',
            'Sugestão de Correção': 'solucao_sugerida',
            'Tópico': 'topico' # Manter 'Tópico' para processamento antes de renomear para 'topico_limpo'
        }, inplace=True)

        # Aplicar funções de padronização e extração
        df['topico_limpo'] = df['topico'].apply(self._clean_topic)
        df['tag_dispositivo_associada'] = df['descricao'].apply(self._extract_device_tag)
        df['origem_documento'] = os.path.basename(csv_filepath) # Adiciona o nome do arquivo como origem

        # Selecionar e reordenar colunas para inserção
        df_to_insert = df[[
            'topico_limpo', 'codigo', 'tipo', 'descricao',
            'causa_provavel', 'solucao_sugerida', 'tag_dispositivo_associada',
            'origem_documento'
        ]]

        # Inserir no banco de dados
        if not df_to_insert.empty:
            try:
                # A conexão e criação de tabelas já devem ter sido feitas pelo script principal
                # Aqui, apenas inserimos os dados
                self.db_manager.insert_alarmes(df_to_insert.to_dict(orient='records'))
                logger.info(f"{len(df_to_insert)} registros inseridos na tabela 'alarmes'.")
            except Exception as e:
                logger.error(f"Erro ao inserir dados no banco de dados: {e}")
                raise
        else:
            logger.warning("DataFrame vazio, nada para salvar no banco de dados.")
