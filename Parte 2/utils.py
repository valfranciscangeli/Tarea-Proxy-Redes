from parse import *
import json
from date import *

# ==================================
# variables globales:
doble_salto = "\r\n\r\n"
salto = "\r\n"
separador_headers = ": "

# ==================================


def find_index_with_substring(substring, string_list):
    for index, string in enumerate(string_list):
        if substring in string:
            return index
    return -1

# ===============================================


def contains_end_of_head(message, end_sequence=doble_salto):
    return end_sequence in message

# ===============================================

# esta función se encarga de recibir el mensaje completo desde el cliente
# en caso de que el mensaje sea más grande que el tamaño del buffer 'buff_size', esta función va esperar a que
# llegue el resto.
# Para saber si el mensaje ya llegó por completo, se busca el fin del HEAD y que el body tenga el largo pedido en el header Content-Lenght


def receive_full_mesage(connection_socket, buff_size):
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


def create_response_message(received_message, username):

    head, body = received_message.split(doble_salto)

    with open("Parte 2/restrictions.json") as file:
        data = json.load(file)

    forbidden_words = data["forbidden_words"]
    print(f"body: \n{body}")
    print("reemplazando palabras prohibidas ...")
    for word in forbidden_words:
        for llave, valor in word.items():
            body = body.replace(llave, valor)

    new_content_lenght = len(body.encode())
    headers = head.split(salto)
    del headers[find_index_with_substring("Content-Length:", headers)]

    content_lenght = f"Content-Length:{new_content_lenght}"
    custom_header = f"X-ElQuePregunta: {username}"
    head = salto.join(headers)
    head += salto + content_lenght + salto + custom_header

    return head + doble_salto+body

# ===============================================


def get_server_host(message: str) -> str:
    host = None
    lineas_solicitud = message.split('\r\n')
    for linea in lineas_solicitud:
        if linea.startswith('Host:'):
            host = linea.split(' ')[1]
            break

    return host

# ===============================================


def get_full_adress(message: str) -> (str, int):
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


def is_forbidden(hostname: str, file_name: str = "restrictions", file_address: str = "Parte 2", protocol: str = "http://") -> bool:
    with open(f"{file_address}/{file_name}.json") as file:
        data = json.load(file)

    blocked = data["blocked"]

    return hostname in blocked or (protocol+hostname) in blocked


assert is_forbidden("www.dcc.uchile.cl/")
assert not is_forbidden("www.example.com/")

# ===============================================
error = """ HTTP/1.1 403 Forbidden
Date: Thu, 08 Sep 2023 15:45:00 GMT
Content-Type: text/html
Content-Length: 93

<!DOCTYPE html>
<html>
<head>
    <title>Error 403 - Forbidden</title>
</head>
<body>
    <h1>403 - Forbidden</h1>
    <p>Access to the requested resource is forbidden on this server.</p>
</body>
</html> """


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

    length = len(body.encode())
    headers = {
        "Date": get_current_datetime(),
        "Content-Type": "text/html",
        "Content-Length": str(length)
    }

    return create_HTTP_message(create_JSON_HTTP(start_line, headers, body))

# print(create_HTTP_error())
