# create_project_structure.ps1

# Define o diretório raiz do projeto conforme fornecido
$projectBaseDir = "D:\PSIA\PSIA"
$projectRoot = Join-Path $projectBaseDir "data_factory_project"

Write-Host "Criando estrutura de pastas para o projeto em: $projectRoot"

# Cria a pasta raiz do projeto
New-Item -ItemType Directory -Path $projectRoot -Force | Out-Null

# Cria subpastas dentro de data_factory_project
New-Item -ItemType Directory -Path (Join-Path $projectRoot "data") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "data\raw_pdfs") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "data\raw_csvs") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "src") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "src\database") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "src\processors") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "src\utils") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "src\app_ui") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "tests") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "tests\unit") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "tests\integration") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "logs") -Force | Out-Null # Pasta de logs no root do projeto

Write-Host "Pastas criadas."

# Cria arquivos __init__.py para tornar os diretórios módulos Python
Write-Host "Criando arquivos __init__.py..."
New-Item -ItemType File -Path (Join-Path $projectRoot "src\__init__.py") -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $projectRoot "src\database\__init__.py") -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $projectRoot "src\processors\__init__.py") -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $projectRoot "src\utils\__init__.py") -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $projectRoot "src\app_ui\__init__.py") -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $projectRoot "tests\__init__.py") -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $projectRoot "tests\unit\__init__.py") -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $projectRoot "tests\integration\__init__.py") -Force | Out-Null
Write-Host "Arquivos __init__.py criados."

# Cria arquivos vazios para os pontos de entrada e configuração
Write-Host "Criando arquivos de configuração e entrada..."
New-Item -ItemType File -Path (Join-Path $projectRoot "data_factory_app.py") -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $projectRoot "requirements.txt") -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $projectRoot ".env") -Force | Out-Null
Write-Host "Arquivos de configuração e entrada criados."

Write-Host "Estrutura do projeto 'data_factory_project' criada com sucesso em $projectRoot!"
Write-Host "Agora você pode navegar para a pasta 'data_factory_project' e começar a preencher os arquivos de código."