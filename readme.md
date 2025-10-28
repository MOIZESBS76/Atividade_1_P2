# FastAPI, RabbitMQ e Docker Compose Example

Este projeto demonstra uma arquitetura básica de microserviços utilizando **FastAPI** como API RESTful, **RabbitMQ** como message broker e **Python** para uma aplicação consumidora de mensagens, tudo orquestrado com **Docker Compose**.

A ideia principal é ter:
- Um serviço FastAPI que recebe requisições HTTP e publica mensagens em uma fila do RabbitMQ.
- Um serviço consumidor que escuta essa fila do RabbitMQ e processa as mensagens.
- Um serviço RabbitMQ para gerenciar a fila de mensagens.

## Tecnologias Utilizadas

- **Python 3.9+**: Linguagem de programação.
- **FastAPI**: Framework web moderno e rápido para construir APIs com Python.
- **Pika**: Biblioteca Python para comunicação com RabbitMQ.
- **RabbitMQ**: Message broker de código aberto.
- **Docker**: Plataforma para desenvolver, enviar e executar aplicações em contêineres.
- **Docker Compose**: Ferramenta para definir e executar aplicações Docker multi-contêiner.

## Estrutura do Projeto
├── api/ │ ├── Dockerfile │ ├── main.py │ └── requirements.txt ├── consumer/ │ ├── Dockerfile │ ├── consumer.py │ └── requirements.txt ├── docker-compose.yaml └── README.md


- **`api/`**: Contém a aplicação FastAPI.
    - `main.py`: Aplicação FastAPI que expõe um endpoint `/enviar` para publicar mensagens.
    - `requirements.txt`: Dependências Python para a API (fastapi, uvicorn, pika).
    - `Dockerfile`: Instruções para construir a imagem Docker da API.
- **`consumer/`**: Contém a aplicação consumidora de mensagens.
    - `consumer.py`: Script Python que se conecta ao RabbitMQ e consome mensagens da fila.
    - `requirements.txt`: Dependências Python para o consumidor (pika).
    - `Dockerfile`: Instruções para construir a imagem Docker do consumidor.
- **`docker-compose.yaml`**: Arquivo de configuração que define e orquestra os três serviços (FastAPI, RabbitMQ, Consumer).
- **`README.md`**: Este arquivo.

## Configuração e Execução

Certifique-se de ter o Docker e o Docker Compose instalados em sua máquina.

### 1. Construir as Imagens Docker

Navegue até o diretório raiz do projeto (`app/`) no seu terminal e execute o comando para construir as imagens:

```bash
docker-compose build --no-cache
A flag --no-cache garante que as imagens sejam construídas do zero, incorporando quaisquer alterações recentes nos arquivos de código-fonte ou requirements.txt.

2. Iniciar os Serviços
Após a construção das imagens, inicie todos os serviços definidos no docker-compose.yaml:

bash
Copiar

docker-compose up
Este comando irá:

Iniciar o contêiner rabbitmq.
Aguardar até que o rabbitmq esteja saudável (graças ao healthcheck e depends_on: condition: service_healthy).
Iniciar o contêiner fastapi_app.
Iniciar o contêiner consumer.
Você verá os logs de todos os serviços no seu terminal. O consumer começará a aguardar por mensagens e o fastapi_app estará disponível para receber requisições.

3. Verificar o Status da API (Opcional)
Você pode verificar se a API do FastAPI está funcionando acessando a URL base no seu navegador:

localhost
Você deverá ver uma resposta JSON como: {"message":"API FastAPI rodando!"}.

Como Usar
Enviando Mensagens via API
Para enviar uma mensagem para a fila do RabbitMQ através da API do FastAPI, você pode fazer uma requisição POST para o endpoint /enviar.

Endpoint: http://localhost:8000/enviar Método: POST Content-Type: application/json Corpo da Requisição (JSON):

json
Copiar

{
  "nome": "Seu Nome",
  "texto": "Sua mensagem aqui!"
}
Exemplo usando PowerShell:
Abra um novo terminal (mantendo o docker-compose up rodando no outro) e execute:

powershell
Copiar

$jsonBody = '{"nome": "Fulano de Tal", "texto": "Esta é uma nova mensagem enviada via POST!"}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonBody)
Invoke-WebRequest -Method Post -Uri "http://localhost:8000/enviar" -Headers @{"Content-Type" = "application/json"} -Body $bytes
Resposta da API (exemplo):
json
Copiar

{
  "status": "mensagem enviada",
  "mensagem": {
    "nome": "Fulano de Tal",
    "texto": "Esta é uma nova mensagem enviada via POST!"
  }
}
Visualizando o Consumidor em Ação
Após enviar a requisição POST, observe o terminal onde o docker-compose up está rodando. Nos logs do serviço consumer, você deverá ver a mensagem recebida e processada:

consumer-1 | 2025-10-27 23:44:58,761 - INFO - [x] Recebida: {'nome': 'Fulano de Tal', 'texto': 'Esta é uma nova mensagem enviada via POST!'}
Parando os Serviços
Para parar e remover todos os contêineres, redes e volumes associados a este projeto, execute:

bash
Copiar

docker-compose down --volumes --remove-orphans
--volumes: Remove os volumes de dados anônimos e nomeados (como os usados pelo RabbitMQ para persistência).
--remove-orphans: Remove contêineres para serviços que não estão mais definidos no arquivo Compose.
Notas Importantes
Orquestração de Inicialização: O docker-compose.yaml utiliza healthcheck para o RabbitMQ e depends_on: condition: service_healthy para os outros serviços. Isso garante que o FastAPI e o Consumer só tentem se conectar ao RabbitMQ quando ele estiver completamente inicializado e pronto para aceitar conexões, evitando ConnectionResetError e outras condições de corrida.
Gerenciamento do RabbitMQ: Você pode acessar a interface de gerenciamento do RabbitMQ em 
localhost
 com as credenciais guest/guest.
Contribuição
Sinta-se à vontade para bifurcar (fork) este repositório e enviar pull requests com melhorias.

Licença
Este projeto está licenciado sob a Licença MIT.

