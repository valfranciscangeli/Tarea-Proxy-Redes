from parse import *
import json
from date import *

# ==================================
# variables globales:
doble_salto = "\r\n\r\n"
salto = "\r\n"
separador_headers = ": "

# ==================================

# esta función se encarga de recibir el mensaje completo desde el cliente
# en caso de que el mensaje sea más grande que el tamaño del buffer 'buff_size', esta función va esperar a que
# llegue el resto.
# Para saber si el mensaje ya llegó por completo, se busca el fin del HEAD y que el body tenga el largo pedido en el header Content-Lenght


def contains_end_of_head(message, end_sequence=doble_salto):
    return message.endswith(end_sequence)


def receive_full_mesage(connection_socket, buff_size):
    # recibimos la primera parte del mensaje
    recv_message = connection_socket.recv(buff_size)
    full_message = recv_message

    # verificamos si llegó el head completo o si aún faltan partes del mensaje
    mensaje_decoded = full_message.decode()
    is_end_of_head = contains_end_of_head(full_message.decode())

    # entramos a un while para recibir el resto y seguimos esperando información
    # mientras el buffer no contenga fin de head
    while not is_end_of_head:
        # recibimos un nuevo trozo del mensaje
        recv_message = connection_socket.recv(buff_size)

        # lo añadimos al mensaje "completo"
        full_message += recv_message

        # verificamos si es la última parte del mensaje
        is_end_of_head = contains_end_of_head(full_message.decode())

    # si llegamos acá es porque recibió todo el HEAD (bien, comprobado)
    # ahora vemos el body:

    message_len = len(full_message)
    decoded_message = full_message.decode()
    head, body = decoded_message.split(doble_salto)
    body_length = len(body.encode())
    total_body_length = 0

    head_parsed = json.loads(parse_HTTP_message(head+doble_salto))

    if "Content-Length" in head_parsed["head"][1]:
        total_body_length = int(head_parsed["head"][1]["Content-Length"])

    is_all_body = body_length == total_body_length

    if total_body_length > 0:
        while not is_all_body:
            # recibimos un nuevo trozo del mensaje
            recv_message = connection_socket.recv(buff_size)

            # lo añadimos al mensaje "completo"
            full_message += recv_message

            # verificamos si es la última parte del mensaje
            head, body = decoded_message.split(doble_salto)
            body_length = len(body.encode())
            is_all_body = body_length == total_body_length

    # finalmente retornamos el mensaje
    return full_message.decode()


# ===============================================

def create_response_message(received_message):
    body = f'<!DOCTYPE html> \
                <html lang="es">\
                    <head>    \
                        <meta charset="UTF-8">   \
                        <title>CC4303</title>\
                    </head>\
                    <body>    \
                        <h1>Bienvenide ... oh? no puedo ver tu nombre :c!</h1>\
                        <h3><a href="replace">¿Qué es un proxy?</a></h3>\
                    </body>\
                </html>'

    head = f'HTTP/1.1 200 OK{salto}Server: nginx/1.17.0{salto}Date: {get_current_datetime()}{salto}Content-Type: text/html; charset=utf-8{salto}Content-Length: {len(body.encode())}{salto}Connection: keep-alive{salto}Access-Control-Allow-Origin: *{doble_salto}'
    
    return head +   body