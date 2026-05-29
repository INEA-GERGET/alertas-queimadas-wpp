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

Ao executar o `main.py`, o terminal exibirá o progresso das requisições e a validação do fuso horário:
```text
2026-05-29 07:02:15 - root - INFO - main.py:48 - Hoje é: 2026-05-29
2026-05-29 07:02:16 - root - INFO - main.py:64 - Our current transaction count is 142
2026-05-29 07:02:20 - root - INFO - main.py:101 - Lista de focos encontrados e filtrados com sucesso.
