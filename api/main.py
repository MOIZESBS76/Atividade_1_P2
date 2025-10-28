from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import os
import json
import logging
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Modelo Pydantic para a mensagem
class Message(BaseModel):
    nome: str
    texto: str

# Configurações do RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
QUEUE_NAME = "minha_fila"

connection = None
channel = None

def connect_to_rabbitmq():
    """Tenta conectar ao RabbitMQ com retries."""
    global connection, channel
    retries = 5
    for i in range(retries):
        try:
            logging.info(f"Tentando conectar ao RabbitMQ em {RABBITMQ_HOST}:{RABBITMQ_PORT} (Tentativa {i+1}/{retries})...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                retry_delay=5,
                connection_attempts=10
            ))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True) # durable=True para persistir a fila
            logging.info("Conectado ao RabbitMQ e fila declarada.")
            return True
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Erro de conexão AMQP com RabbitMQ: {e}")
            time.sleep(5) # Espera antes de tentar novamente
        except Exception as e:
            logging.error(f"Erro inesperado ao conectar ao RabbitMQ: {e}")
            time.sleep(5)
    logging.error("Não foi possível conectar ao RabbitMQ após múltiplas tentativas.")
    return False

@app.on_event("startup")
async def startup_event():
    """Executado quando a aplicação FastAPI inicia."""
    if not connect_to_rabbitmq():
        # Se a conexão falhar na inicialização, podemos decidir se queremos abortar
        # ou continuar e lidar com erros de publicação posteriormente.
        logging.critical("Falha na inicialização: Não foi possível conectar ao RabbitMQ.")
        # Dependendo da robustez desejada, você pode levantar uma exceção aqui
        # para que o contêiner falhe e seja reiniciado pelo Docker.
        # raise RuntimeError("Não foi possível conectar ao RabbitMQ na inicialização.")

@app.on_event("shutdown")
async def shutdown_event():
    """Executado quando a aplicação FastAPI desliga."""
    global connection
    if connection and connection.is_open:
        logging.info("Fechando conexão com RabbitMQ.")
        connection.close()

@app.post("/enviar")
async def enviar_mensagem(message: Message):
    """
    Recebe um JSON com uma mensagem e a envia para uma fila do RabbitMQ.
    """
    global channel, connection
    if not channel or not channel.is_open:
        logging.warning("Canal do RabbitMQ não está aberto. Tentando reconectar.")
        if not connect_to_rabbitmq():
            raise HTTPException(status_code=500, detail="Serviço de mensageria indisponível.")

    try:
        message_body = json.dumps(message.dict())
        channel.basic_publish(
            exchange='',         # Exchange padrão (default exchange)
            routing_key=QUEUE_NAME, # Roteia para a fila com o mesmo nome
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Torna a mensagem persistente
            )
        )
        logging.info(f"Mensagem enviada para RabbitMQ: {message_body}")
        return {"status": "mensagem enviada", "mensagem": message.dict()}
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem para RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem: {e}")

@app.get("/")
async def root():
    return {"message": "API FastAPI rodando!"}
