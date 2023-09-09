from parse import *
import json
from date import *
from strings import *

# ===============================================
# variables globales:
doble_salto = "\r\n\r\n"
salto = "\r\n"
separador_headers = ": "


# ===============================================

""" esta función se encarga de recibir el mensaje completo desde el cliente/servidor
# en caso de que el mensaje sea más grande que el tamaño del buffer 'buff_size', esta función funcionará así:
- Para saber si el mensaje ya llegó por completo, se busca el fin del HEAD (doble salto)
- Si no se ha encontrado el "doble salto", se continua pidiendo partes del tamaño del buffer.
- una vez que tenemos todo el HEAD, se busca el header "Content-Lenght"
- Se asume que el largo del body es 0 si el header no se encuentra.
- Se continua pidiendo partes del mensaje hasta completar el tamaño del body.
"""


def receive_full_mesage(connection_socket, buff_size: int) -> str:
    print("estamos recibiendo el mensaje ...")
    # recibimos la primera parte del mensaje
    recv_message = connection_socket.recv(buff_size)
    print(f"se recibieron los primeros {buff_size} caracteres ...")
    print(f"contenido preliminar: \n{recv_message}")
    fp_message = recv_message

    # verificamos si llegó el head completo o si aún faltan partes del mensaje
    # mensaje_decoded = full_message.decode()
    is_end_of_head = contains_end_of_head(fp_message.decode())
    if is_end_of_head:
        print("llegó todo el head ...")

    # entramos a un while para recibir el resto y seguimos esperando información
    # mientras el buffer no contenga fin de head

    print("entramos a esperar todo el head ...")
    while not is_end_of_head:
        # recibimos un nuevo trozo del mensaje
        recv_message = connection_socket.recv(buff_size)

        # lo añadimos al mensaje "completo"
        fp_message += recv_message

        # verificamos si es la última parte del mensaje
        is_end_of_head = contains_end_of_head(fp_message.decode())

    # si llegamos acá es porque recibió todo el HEAD
    print("llegó todo el head ...")

    # ahora vemos el body:
    decoded_message = fp_message.decode()
    head, body = decoded_message.split(doble_salto)

    print(f"head: \n {head}")
    print(f"body: \n {body}")

    body = body.encode()

    body_length = len(body)
    print(f"han llegado {body_length} caracteres del body")
    headers = head.split(salto)
    total_body_length = 0
    index_c_length = find_index_with_substring("Content-Length:", headers)

    if index_c_length != -1:
        total_body_length = int((headers[index_c_length]).split()[1])

    is_all_body = body_length == total_body_length

    if is_all_body:
        print("llegó todo el body ...")
    else:
        print(
            f"faltan {total_body_length-body_length} caracteres del body ...")

        print("entramos a esperar todo el body ...")
        while not is_all_body:
            # recibimos un nuevo trozo del mensaje
            print("recibiendo otro trozo de body ...")
            recv_message = connection_socket.recv(buff_size)

            # lo añadimos al body
            body += recv_message

            # verificamos si es la última parte del body

            body_length = len(body)

            is_all_body = body_length == total_body_length

    print("llegó todo el body ...")

    # finalmente retornamos el mensaje
    print("retornando mensaje decodificado ...")
    fp_message = head + doble_salto+body.decode()
    return fp_message


# ===============================================
""" Esta funcion revisa el mensaje de response reemplazando las palabras prohibidas en el body segun el archivo restrictions.json """


def create_response_message(received_message, username):

    head, body = received_message.split(doble_salto)

    with open("restrictions.json") as file:
        data = json.load(file)
    forbidden_words = data["forbidden_words"]

    print("reemplazando palabras prohibidas ...")
    for word in forbidden_words:
        for llave, valor in word.items():
            body = body.replace(llave, valor)

    new_content_lenght = len(body.encode())  # nuevo largo del body
    headers = head.split(salto)

    connection_index = find_index_with_substring(
        "Connection: keep-alive", headers)
    keep_a_index = find_index_with_substring("Content-Length:", headers)

    if connection_index != -1:
        del headers[connection_index]  # eliminamos el header Connection
    if keep_a_index != -1:
        del headers[keep_a_index]  # eliminamos el header Content-Length

    # reemplazamos el header
    content_lenght = f"Content-Length:{new_content_lenght}"

    head = salto.join(headers)  # recomponemos el HEAD
    head += salto + content_lenght

    return head + doble_salto + body


# ===============================================
"Esta función devuelve el contenido del header 'Host' de un mensaje http"


def get_server_host(message: str) -> str:
    host = None
    lineas_solicitud = message.split('\r\n')
    for linea in lineas_solicitud:
        if linea.startswith('Host:'):
            host = linea.split(' ')[1]
            break

    return host


# ===============================================
""" Esta funcion entrega la direccion pedida completa
revisando el header 'Host' y la startline """


def get_full_adress(message: str) -> str:
    host = get_server_host(message)
    mensaje = json.loads(parse_HTTP_message(message))
    start_line = mensaje["head"][0]
    address = start_line.split()[1]

    if not (host in address):
        return host+address
    else:
        return address


assert get_full_adress(http_message) == "www.ejemplo.com/pagina-ejemplo"

# ===============================================
""" Esta funcion revisa si la direccion pedida esta prohibida segun el archivo de restrictions.json """


def is_forbidden(hostname: str, file_name: str = "restrictions", protocol: str = "http://") -> bool:
    with open(f"{file_name}.json") as file:
        data = json.load(file)

    blocked = data["blocked"]

    return hostname in blocked or (protocol+hostname) in blocked


assert is_forbidden("www.dcc.uchile.cl/")
assert not is_forbidden("www.example.com/")

# ===============================================
""" Esta funcion compone el mensaje de error de pagina prohibida """


def create_HTTP_error(custom_message="Access to the requested resource is forbidden on this server."):

    start_line = "HTTP/1.1 403 Forbidden"

    body = f"<!DOCTYPE html> \
            <html> \
            <head> \
                <title>Error 403 - Forbidden</title> \
            </head> \
            <body> \
                <h1>403 - Forbidden</h1> \
                <p>{custom_message}</p> \
            </body> \
            </html>" \

    length = len(body.encode())  # largo del body
    headers = {
        "Date": get_current_datetime(),
        "Content-Type": "text/html",
        "Content-Length": str(length)
    }

    return create_HTTP_message(create_JSON_HTTP(start_line, headers, body))


# ===============================================
""" Esta funcion compone el header X-ElQuePregunta con el username en config.json"""


def add_custom_header(message: str, username: str) -> str:
    head, body = message.split(doble_salto)
    head += salto+f"X-ElQuePregunta: {username}"
    return head+doble_salto+body

# ===============================================


def process_request(message, username):
    message = add_custom_header(message, username)
    head, body = message.split(doble_salto)
    headers = head.split(salto)

    connection_index = find_index_with_substring(
        "Connection: keep-alive", headers)
    if connection_index != -1:
        del headers[connection_index]  # eliminamos el header Connection

    head = salto.join(headers)  # recomponemos el HEAD

    return head + doble_salto + body

# ===============================================


""" Devuelve el username contenido en el archivo de configuracion """


def get_username(json_file):
    # abrimos el archivo de configuracion
    with open(f"{json_file}.json") as file:
        data = json.load(file)
        # cargamos el nombre de usuario
        if "username" in data["parameters"][0]:
            return data["parameters"][0]["username"]
    return "Undefined"
