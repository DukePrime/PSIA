# data_factory_project/src/utils/helpers.py

import re
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normaliza uma string: remove acentos, converte para minúsculas,
    substitui espaços e caracteres especiais por underscores.
    """
    if not isinstance(text, str):
        return str(text) # Garante que seja string antes de normalizar

    # Remove acentos
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    # Converte para minúsculas
    text = text.lower()
    # Substitui caracteres não alfanuméricos (exceto underscores) por underscore
    text = re.sub(r'[^a-z0-9_]+', '_', text)
    # Remove underscores duplicados
    text = re.sub(r'_+', '_', text)
    # Remove underscores do início e do fim
    text = text.strip('_')
    return text

def extract_project_id_from_filename(filename: str) -> str | None:
    """
    Extrai o ProjectID de um nome de arquivo PDF.
    Ex: "E250905.AGV.001 - AGV LOGÍSTICO ÔNIBUS - MBB_R1V1.pdf" -> "E250905.AGV.001"
    """
    # Regex para capturar o padrão "E250905.AGV.001" ou similar
    # Assume que o ProjectID é a primeira parte antes de " - " ou "__"
    match = re.match(r"([A-Z0-9\._-]+)", filename)
    if match:
        return match.group(1)
    return None

def extract_project_name_from_filename(filename: str) -> str | None:
    """
    Extrai o ProjectName de um nome de arquivo PDF.
    Ex: "E250905.AGV.001 - AGV LOGÍSTICO ÔNIBUS - MBB_R1V1.pdf" -> "AGV LOGÍSTICO ÔNIBUS - MBB_R1V1"
    """
    # Regex para capturar o nome do projeto após o ProjectID e " - "
    match = re.search(r"^[A-Z0-9\._-]+\s+-\s+(.+)\.pdf$", filename)
    if match:
        # Remove a extensão .pdf e qualquer parte de revisão como _R1V1
        project_name = match.group(1).strip()
        # Opcional: remover sufixos de revisão se não forem parte do nome "oficial"
        project_name = re.sub(r'(_R\d+V\d+)$', '', project_name)
        return project_name.strip()
    return None
