# Sistema de Alertas de Focos de Incêndio em Unidades de Conservação

Sistema automatizado para **detecção e geração de alertas de focos de calor/incêndio no estado do Rio de Janeiro**, com foco em ocorrências localizadas dentro de **Unidades de Conservação (UCs)** e **Zonas de Amortecimento (ZAs)**.

O sistema consulta dados recentes do **NASA FIRMS**, realiza filtros e cruzamentos geoespaciais com bases de municípios, UCs e ZAs e prepara alertas para envio por **WhatsApp**. O script principal também mantém um estado das últimas notificações para reduzir o envio de mensagens duplicadas.

> **Importante:** este repositório deve conter o código-fonte e as bases geoespaciais necessárias ao processamento, mas **não deve conter credenciais, tokens, chaves de API ou outros segredos**. As informações sensíveis devem ser configuradas localmente no arquivo `config/config.ini`, que não deve ser versionado.

---

## Funcionalidades

### 1. Consulta de focos de calor

O `main.py` consulta a API do **FIRMS/NASA** para obter dados recentes de diferentes fontes de detecção, incluindo:

- `VIIRS_NOAA20_NRT`
- `VIIRS_NOAA21_NRT`
- `VIIRS_SNPP_NRT`
- `MODIS_NRT`

A área consultada é delimitada pelo *bounding box* do estado do Rio de Janeiro.

### 2. Filtragem por data

São mantidos os focos registrados na data corrente do processamento. A data e hora de aquisição fornecidas pelo VIIRS são convertidas para o horário de Brasília (UTC-3) para apresentação no alerta.

### 3. Exclusão de focos associados a áreas industriais

O projeto utiliza o arquivo `calor_fixo.xlsx` para identificar pontos associados a indústrias.

Cada foco é comparado com as coordenadas cadastradas das indústrias e, por padrão, é considerado industrial quando está a até **1,5 km** de uma indústria. Esses focos são removidos antes da análise de UCs e ZAs.

### 4. Análise geoespacial

Os focos são transformados em `GeoDataFrame` com CRS `EPSG:4326` e submetidos a *spatial joins* com as bases geográficas do projeto.

O fluxo identifica:

- município;
- bairro;
- distrito;
- Unidade de Conservação;
- Zona de Amortecimento.

Somente os focos que estejam dentro de uma UC ou de uma ZA são mantidos para a geração do alerta.

### 5. Identificação de UCs municipais e estaduais

O processamento utiliza separadamente as bases de:

- UCs municipais;
- UCs estaduais;
- Zonas de Amortecimento de UCs estaduais.

As geometrias são reprojetadas para o mesmo CRS dos focos antes dos cruzamentos espaciais e estas bases devem ser buscadas no portal Geoinea

### 6. Geração das mensagens de alerta

Para cada foco detectado, a mensagem pode conter:

- latitude;
- longitude;
- data de aquisição;
- hora convertida para Brasília;
- período do dia/noite;
- município;
- bairro;
- distrito;
- Unidade de Conservação;
- Zona de Amortecimento;
- satélite;
- instrumento de detecção.

O objetivo é produzir uma mensagem suficientemente detalhada para apoiar o acompanhamento das ocorrências.

### 7. Envio por WhatsApp

O arquivo `zap.py` contém a função de envio por meio da **API Whapi Cloud**.

O envio utiliza um token de autenticação e um identificador de grupo fornecidos pelo arquivo de configuração. 

### 8. Controle de mensagens repetidas

O projeto mantém o arquivo `config/mensagens_enviadas.json` para registrar o dia e a quantidade de focos da última mensagem processada.

Esse estado é utilizado para evitar o reenvio de uma mensagem quando a quantidade de focos encontrada permanece igual àquela já processada no mesmo dia.

### 9. Logging e rastreabilidade

O projeto possui um sistema de logging configurado em `zap.py`, utilizando:

- saída para o console;
- arquivo `logs/execucao.log`;
- `RotatingFileHandler` com limite de 5 MB por arquivo e até 3 arquivos de backup.

Os logs registram etapas importantes do processamento, erros, quantidade de registros e informações relacionadas à execução.

---

## Estrutura do projeto

```text
Viirs_projeto/
│
├── .gitignore
├── README.md
├── calor_fixo.xlsx
├── comparacao.ipynb
├── main.py
├── mandar_mensagem_VIIRS.bat
├── zap.py
│
├── config/
│   ├── config.ini
│   └── mensagens_enviadas.json
│
├── logs/
│   └── execucao.log
│
├── RJ_setores_CD2022/
│   ├── RJ_setores_CD2022.cpg
│   ├── RJ_setores_CD2022.dbf
│   ├── RJ_setores_CD2022.prj
│   ├── RJ_setores_CD2022.shp
│   └── RJ_setores_CD2022.shx
│
├── UCs_Municipais/
│   └── GPL_UCS_MUN_2025_ME.*
│
└── UCs_ZAs/
    ├── ucs_estaduais.*
    └── gpl_ucs_estaduais_ZA.*
```

### Descrição dos principais arquivos e diretórios

| Item | Função |
|---|---|
| `main.py` | Script principal. Consulta os focos, executa os filtros e cruzamentos espaciais, gera os alertas e controla os horários de execução. |
| `zap.py` | Funções auxiliares, principalmente logging, controle de estado e envio de mensagens pela Whapi Cloud. |
| `config/` | Diretório para configurações locais e estado da aplicação. O `config.ini` contém informações sensíveis e deve permanecer fora do GitHub. |
| `calor_fixo.xlsx` | Cadastro de pontos de referência utilizados para remover ocorrências próximas a indústrias. |
| `RJ_setores_CD2022/` | Base espacial utilizada para associar os focos a município, bairro e distrito. |
| `UCs_Municipais/` | Bases espaciais de Unidades de Conservação municipais. |
| `UCs_ZAs/` | Bases espaciais de UCs estaduais e respectivas Zonas de Amortecimento. |
| `logs/` | Arquivos de log da execução. Recomenda-se não versionar os logs. |
| `mandar_mensagem_VIIRS.bat` | Arquivo auxiliar para execução no Windows. |

> Os arquivos `.shp` fazem parte de um *shapefile* e normalmente dependem também de `.dbf`, `.shx`, `.prj` e, quando existentes, arquivos auxiliares como `.cpg`, `.sbn` e `.sbx`. Esses arquivos devem ser mantidos juntos quando a base for distribuída.

---

## Como configurar o projeto

### 1. Instalar as dependências

O projeto utiliza bibliotecas Python, entre elas:

```text
pandas
geopandas
shapely
geopy
requests
pyautogui
pyperclip
```

Além dessas, o ambiente deve possuir as dependências transitivas exigidas pelo `GeoPandas` e pelos demais pacotes.

Recomenda-se criar um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bat
.venv\Scripts\activate
```

Depois, instalar as dependências do projeto.

> Este repositório ainda não possui um `requirements.txt` descrito na estrutura apresentada. Para facilitar a reprodução do ambiente, recomenda-se criar esse arquivo antes da publicação definitiva.

### 2. Configurar o `config/config.ini`

O usuário que instalar o projeto deverá criar localmente o arquivo:

```text
config/config.ini
```

Esse arquivo deve conter as credenciais e parâmetros sensíveis esperados pelo código. No estado atual de `main.py`, as chaves utilizadas são:

```ini
[FIRMS]
KEY=SUA_CHAVE_FIRMS
TOKEN=SEU_TOKEN_WHAPI
GRUPO=ID_DO_GRUPO_WHATSAPP
```

**Não copie credenciais reais para o exemplo acima e não faça commit do arquivo preenchido.** O valor de `GRUPO` é o identificador do grupo utilizado pela API de WhatsApp, e `TOKEN` é a credencial usada para autenticar as requisições à Whapi Cloud.

O repositório deve fornecer apenas um arquivo-modelo, por exemplo:

```text
config/config.example.ini
```

com valores fictícios ou placeholders.

### 3. Configurar o estado local

O arquivo:

```text
config/mensagens_enviadas.json
```

é criado/atualizado pelo sistema para controlar o estado das notificações. Ele não representa uma credencial, mas é um **artefato de execução local** e não é necessário para reproduzir o código do zero.

---

## Execução

O arquivo `main.py` é o ponto de entrada principal.

Ao final do arquivo, a função `main()` é chamada sequencialmente nos horários:

```text
07:00
10:30
16:00
17:00
```

Cada chamada aguarda o horário correspondente e executa o processamento.

Para executar diretamente:

```bash
python main.py
```

No Windows, também pode ser utilizado o `.bat` disponibilizado no projeto, desde que ele esteja corretamente configurado para o ambiente local.

---

## Fluxo de processamento

O fluxo lógico do sistema pode ser resumido da seguinte forma:

```text
             Início
                │
                ▼
       Consulta NASA FIRMS
                │
                ▼
       Junta fontes de focos
                │
                ▼
       Filtra focos do dia
                │
                ▼
   Remove focos próximos a indústrias
                │
                ▼
        Cria GeoDataFrame
                │
                ▼
    Identifica município/bairro/distrito
                │
                ▼
      Cruza com UCs municipais
                │
                ▼
       Cruza com UCs estaduais
                │
                ▼
       Cruza com Zonas de
          Amortecimento
                │
                ▼
  Mantém somente focos em UC/ZA
                │
                ▼
       Gera mensagem de alerta
                │
                ▼
       Verifica duplicidade
                │
                ▼
          Envia WhatsApp
                │
                ▼
               Fim
```

---

# Segurança e proteção de dados

A publicação do projeto no GitHub é possível, mas exige uma separação clara entre **código/dados públicos** e **segredos operacionais**.

A análise abaixo considera o código disponibilizado neste projeto e o conteúdo atualmente observado em `main.py` e `zap.py`.

## 1. Principal risco: credenciais no `config.ini`

`main.py` lê diretamente do arquivo `config/config.ini`:

- chave `FIRMS.KEY`;
- token `FIRMS.TOKEN`;
- identificador `FIRMS.GRUPO`.

A chave e o token são informações de autenticação. **Nunca devem ser publicados no GitHub**, mesmo que o repositório seja privado por algum período.

A proteção recomendada é:

1. adicionar `config/config.ini` ao `.gitignore`;
2. criar `config/config.example.ini` com valores fictícios;
3. informar no README que o usuário deve copiar o arquivo de exemplo para `config.ini`;
4. nunca colocar credenciais em commits;
5. caso um segredo seja acidentalmente publicado, revogá-lo/rotacioná-lo imediatamente.

### Exemplo de `.gitignore`

```gitignore
# Configurações e segredos
config/config.ini

# Estado e arquivos gerados
config/mensagens_enviadas.json
logs/

# Ambiente Python
.venv/
__pycache__/
*.py[cod]
```

O `.gitignore` do repositório deve ser revisado antes do primeiro `git add .`.

---

## 2. Risco importante encontrado no logging: exposição da chave FIRMS

Há um problema relevante no código atual.

O `main.py` monta a URL de consulta ao status da chave usando:

```python
url_status = f'https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY={MAP_KEY}'
```

Em seguida, em caso de erro, essa URL é registrada no log:

```python
logging.error(
    f"There is an issue with the query for transaction count: {url_status}. Error: {e}"
)
```

Isso significa que **a chave `MAP_KEY` pode aparecer diretamente no `logs/execucao.log`**.

Esse risco é especialmente importante porque o diretório `logs/` contém um arquivo de aproximadamente 1,25 MB no ambiente apresentado.

### Recomendação

Não registrar URLs que contenham credenciais. Em vez de:

```python
logging.error(f"Erro na consulta: {url_status}. Error: {e}")
```

usar algo semelhante a:

```python
logging.error(f"Erro na consulta de status da chave FIRMS. Error: {e}")
```

Também é recomendável revisar logs já existentes antes de publicá-los no GitHub.

---

## 3. Risco dos logs

Os logs podem conter informações operacionais e dados dos focos.

No `main.py`, a lista final de ocorrências é convertida para dicionários e registrada com:

```python
logging.info(item)
```

Esses registros podem conter, entre outros dados:

- latitude;
- longitude;
- município;
- bairro;
- distrito;
- Unidade de Conservação;
- Zona de Amortecimento;
- data e hora da ocorrência;
- satélite e instrumento.

Além disso, em `zap.py`, erros da API podem registrar informações retornadas pelo serviço.

### Recomendação

Para um repositório público, o diretório `logs/` deve ser tratado como **saída local da aplicação**, e não como parte do código-fonte versionado.

O ideal é:

```gitignore
logs/
*.log
```

O arquivo de log existente deve ser removido da árvore do repositório antes do primeiro *push*.

Se ele já tiver sido commitado anteriormente, simplesmente apagar o arquivo local não basta: será necessário removê-lo também do histórico Git e verificar se nenhuma credencial foi exposta.

---

## 4. Dados geográficos não são necessariamente segredos, mas devem ser classificados

As bases em:

```text
RJ_setores_CD2022/
UCs_Municipais/
UCs_ZAs/
```

são dados geográficos utilizados como insumo operacional.

O código apresentado não demonstra que essas bases sejam dados pessoais ou credenciais. Entretanto, antes de colocá-las em um repositório público, deve-se verificar:

- a licença de uso;
- a origem oficial da base;
- as restrições de redistribuição;
- se a versão disponibilizada pode ser publicada diretamente;
- se o repositório precisa preservar metadados e atribuição da fonte.

Portanto, **o fato de uma camada ser tecnicamente acessível não significa automaticamente que sua redistribuição no GitHub seja permitida**.

---

## 5. `calor_fixo.xlsx` deve ser avaliado antes da publicação

O arquivo `calor_fixo.xlsx` é utilizado para identificar focos próximos a indústrias.

Ele merece uma análise específica antes da publicação porque pode conter informações que não deveriam ser redistribuídas, como:

- coordenadas precisas de instalações;
- nomes de empresas;
- identificadores internos;
- informações operacionais;
- dados não publicados.

O código sozinho não permite afirmar que esse arquivo é público ou que sua redistribuição é autorizada.

### Recomendação

Antes do commit, verificar a origem, licença e conteúdo do arquivo. Caso ele contenha informação restrita, o ideal é:

- mantê-lo fora do GitHub; ou
- disponibilizar uma versão anonimizada/generalizada; ou
- substituí-lo por uma instrução de configuração para que o usuário forneça sua própria base.

---

## 6. Identificador do grupo do WhatsApp

O identificador do grupo (`GRUPO`) não possui a mesma criticidade de um token secreto, mas ainda é uma informação operacional que pode não ser conveniente publicar.

Por esse motivo, recomenda-se mantê-lo no `config.ini` juntamente com as demais configurações.

---

## 7. Token da Whapi Cloud

O token utilizado em `zap.py` é enviado no cabeçalho HTTP:

```python
headers = {
    "Authorization": f"Bearer {WHAPI_TOKEN}",
    "Content-Type": "application/json"
}
```

Esse token é uma **credencial de autenticação** e deve ser tratado como segredo.

Nunca deve ser:

- escrito diretamente em `main.py` ou `zap.py`;
- incluído no README;
- colocado em um notebook;
- registrado em logs;
- enviado em mensagens de erro;
- versionado pelo Git.

---

## 8. Uso de `pyautogui`

O projeto importa `pyautogui` e possui código relacionado a automação de interface gráfica. A função `mover_mouse()` atualmente não é utilizada, mas permanece no projeto.

Esse tipo de automação possui riscos operacionais diferentes de uma integração HTTP pura, pois depende do estado da máquina e da interface gráfica.

Para uma implantação em servidor, recomenda-se reduzir dependências de automação de desktop sempre que a API utilizada fornecer uma interface programática estável.

---

## 9. Estado de execução não deve ser tratado como segredo

`mensagens_enviadas.json` armazena o dia e o número de focos processados. Não há, pelo código analisado, uma credencial nesse arquivo.

Mesmo assim, ele é um **arquivo de estado gerado localmente** e não precisa ser versionado.

Manter esse arquivo fora do Git reduz ruído no histórico e evita diferenças entre máquinas.

---

## 10. Tratamento de erros e exposição de informações

O código utiliza vários blocos `try/except` e registra exceções detalhadas. Isso é positivo para diagnóstico, mas logs detalhados em ambiente produtivo precisam ser tratados como dados potencialmente sensíveis.

Em especial, deve-se evitar incluir nos logs:

- tokens;
- API keys;
- URLs contendo credenciais;
- cabeçalhos HTTP de autenticação;
- respostas completas de APIs que possam conter dados sensíveis;
- identificadores internos desnecessários.

Uma boa prática é registrar **o contexto do erro**, e não necessariamente todo o conteúdo retornado pelo serviço externo.

---

## 11. GitHub: checklist antes da publicação

Antes do primeiro `git push`, recomenda-se verificar:

- [X] `config/config.ini` está no `.gitignore`.
- [X] `config/mensagens_enviadas.json` está no `.gitignore`.
- [X] `logs/` está no `.gitignore`.
- [X] não existem arquivos `.log` versionados.
- [X] não existem tokens no código.
- [X] não existem API keys no código.
- [X] não existem senhas em notebooks (`.ipynb`).
- [X] não existem URLs contendo credenciais.
- [X] `calor_fixo.xlsx` foi revisado quanto à licença e ao conteúdo.
- [X] as bases geográficas foram verificadas quanto à licença de redistribuição.
- [X] o histórico Git não contém credenciais antigas.
- [X] foi criado um `config.example.ini` sem valores reais.

Uma revisão mínima pode ser feita com uma busca textual antes do commit, procurando termos como:

```text
TOKEN
KEY
SECRET
PASSWORD
BEARER
API_KEY
MAP_KEY
```

Também é recomendável utilizar ferramentas de detecção de segredos, como **Gitleaks** ou **GitHub Secret Scanning**, quando disponíveis.

---

# Recomendações para uma publicação segura

Para deixar o projeto adequado para GitHub, a estrutura recomendada é:

```text
Viirs_projeto/
│
├── .gitignore
├── README.md
├── config/
│   └── config.example.ini
├── main.py
├── zap.py
├── calor_fixo.xlsx              # somente se a redistribuição for permitida
├── RJ_setores_CD2022/           # somente se a redistribuição for permitida
├── UCs_Municipais/              # somente se a redistribuição for permitida
└── UCs_ZAs/                     # somente se a redistribuição for permitida
```

Os seguintes itens devem permanecer apenas localmente:

```text
config/config.ini
config/mensagens_enviadas.json
logs/
```

---

# Observações técnicas

## Sistema de referência espacial

Os focos são criados inicialmente em `EPSG:4326`, utilizando longitude e latitude. As demais camadas são convertidas para o CRS do `GeoDataFrame` dos focos antes dos *spatial joins*.

## Critério espacial

Os cruzamentos utilizam `predicate='within'`. Portanto, o alerta considera os pontos cuja geometria esteja dentro das geometrias das áreas analisadas.

## Critério de proximidade de indústrias

A verificação industrial utiliza distância geodésica por meio de `geopy.distance.geodesic`, com raio padrão de 1,5 km.

## Horários de execução

O script atual chama `main()` quatro vezes, nos horários:

```text
07:00
10:30
16:00
17:00
```

A função `hora_envio()` permanece em espera até que o horário informado seja atingido.

---

# Limitações atuais

O projeto possui algumas características que devem ser consideradas antes de uma implantação mais ampla:

1. O `config.ini` é carregado por caminho relativo. A execução depende do diretório de trabalho correto.
2. Não existe, na estrutura apresentada, um `requirements.txt`, dificultando a reprodução exata do ambiente.
3. O controle de duplicidade é baseado na quantidade de focos e no dia, não em um identificador único de cada foco. Isso pode gerar situações em que o número de focos coincida apesar de serem ocorrências diferentes.
4. O `main.py` realiza várias operações de I/O e processamento geoespacial em uma única rotina, o que dificulta testes unitários isolados.
5. O logging atual é detalhado demais para um repositório que será público, principalmente porque algumas exceções podem incluir informações de requisições.

---

# Resumo de segurança

**O código pode ser disponibilizado no GitHub, mas o repositório precisa separar claramente código público de configuração e artefatos operacionais.**

O ponto mais crítico identificado na versão analisada é a possibilidade de **vazamento da chave FIRMS por meio de logs**, pois a URL que contém `MAP_KEY` é incluída em uma mensagem de erro. O token da Whapi Cloud e a configuração do grupo também devem permanecer exclusivamente no `config/config.ini` local.

Além disso, os logs podem conter coordenadas e informações detalhadas sobre focos e o arquivo `calor_fixo.xlsx` deve ser analisado quanto à possibilidade de conter dados de instalações privadas ou restritos.

A regra operacional para o projeto deve ser:

> **Código, documentação e dados comprovadamente públicos podem ir para o GitHub; credenciais, estado de execução, logs e dados cuja licença ou sensibilidade não tenha sido verificada devem permanecer fora do repositório.**

