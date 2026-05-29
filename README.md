# Monitoramento de Focos de Calor - De Olho No Verde Queimadas🔥

## Sumário
1. [Descrição](#descrição)
2. [Uso](#uso)
   - [Sobre os arquivos](#sobre-os-arquivos)
3. [Instalação](#instalação)

## Descrição
Este repositório contém os scripts necessários para automatizar a extração de dados de satélite da NASA (FIRMS), cruzar informações geográficas de municípios/bairros do Rio de Janeiro, filtrar alarmes falsos em áreas industriais e **enviar relatórios diários de alertas automaticamente via WhatsApp**.

## Uso
O processo é executado de forma automática ao rodar o script principal. O sistema calcula um horário randômico na primeira hora da manhã para simular uma ação humana e aguarda o momento certo para disparar o relatório.

Para usar o script é necessário ter uma chave de acesso, que deverá ser colocada no `main.py`: 
``` python3
    # Let's set your map key that was emailed to you. It should look something like 'abcdef1234567890abcdef1234567890'
    MAP_KEY = 'your_map_key_here'  # Substitua pelo seu MAP_KEY real
```

### Sobre os arquivos
Diretório Raiz:

main.py: O script principal que consome a API da NASA, realiza as filtragens espaciais com o GeoPandas e constrói o texto do relatório.

zap.py: Módulo complementar de RPA (Robotic Process Automation) que simula o teclado/mouse para interagir com o WhatsApp Desktop e gerencia os logs do sistema.

calor_fixo.xlsx: Planilha com as coordenadas (latitude e longitude) de indústrias e plantas operacionais. Focos detectados em um raio de até 1.5 km destas coordenadas serão desconsiderados por serem calor fixo industrial.

RJ_setores_CD2022: Esta pasta deve conter o Shapefile oficial (RJ_setores_CD2022.shp e suas extensões) do IBGE. Ele é utilizado para o spatial join que identifica o Município, Bairro e Distrito de cada foco de calor.

logs: Pasta criada automaticamente pelo sistema onde o arquivo execucao.log será armazenado e rotacionado (máximo de 3 arquivos de 5MB cada).

## Instalação

Para utilizar os scripts, é necessária a instalação das seguintes bibliotecas:

* **pandas**: Para manipulação das tabelas da API e leitura da planilha de calor fixo.

* **geopandas**: Para leitura do Shapefile e cruzamento espacial dos dados de satélite (sjoin).

* **shapely**: Para manipulação de objetos geométricos.

* **geopy**: Para o cálculo de distância geodésica (geodesic) em quilômetros entre os focos e as indústrias.

* **pyautogui**: Para automação de interface (RPA), controle de cliques, atalhos e digitação no Windows.

* **openpyxl**: Mecanismo necessário para o pandas ler o arquivo Excel (calor_fixo.xlsx).
