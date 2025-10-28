import pika
import os
import json
import time
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurações do RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
QUEUE_NAME = "minha_fila"

def callback(ch, method, properties, body):
    """
    Função de callback que será executada quando uma mensagem for recebida.
    """
    try:
        message_data = json.loads(body)
        logging.info(f" [x] Recebida: {message_data}")
        # Exibe no terminal o conteúdo recebido
        print(f"==========================================")
        print(f"Mensagem Recebida:")
        print(f"Nome: {message_data.get('nome', 'N/A')}")
        print(f"Texto: {message_data.get('texto', 'N/A')}")
        print(f"==========================================")
        ch.basic_ack(delivery_tag=method.delivery_tag) # Confirma o recebimento da mensagem
    except json.JSONDecodeError:
        logging.error(f" [x] Erro ao decodificar JSON: {body.decode()}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) # Nega e não requeue (mensagem inválida)
    except Exception as e:
        logging.error(f" [x] Erro ao processar mensagem: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True) # Nega e requeue (tentar novamente)


def start_consumer():
    """
    Inicia o consumidor de mensagens do RabbitMQ.
    """
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
            channel.queue_declare(queue=QUEUE_NAME, durable=True) # Garante que a fila existe
            logging.info(' [*] Esperando por mensagens. Para sair, pressione CTRL+C')

            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Erro de conexão AMQP com RabbitMQ: {e}")
            time.sleep(5)
        except KeyboardInterrupt:
            logging.info("Consumidor encerrado por interrupção do usuário.")
            if 'connection' in locals() and connection.is_open:
                connection.close()
            break
        except Exception as e:
            logging.error(f"Erro inesperado no consumidor: {e}")
            time.sleep(5)
    logging.error("Consumidor não conseguiu iniciar após múltiplas tentativas.")


if __name__ == '__main__':
    start_consumer()