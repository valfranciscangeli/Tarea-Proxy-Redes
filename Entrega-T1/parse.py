# contiene las funciones que permiten traducir un mensaje
# http a json

import json

#  variables globales ===============================
salto = "\r\n"
doble_salto = "\r\n\r\n"
separador_headers = ": "
# ====================================================

""" Crea una estructura json a partir de una start line http, diccionario de headers y un body (frecuentemente html) """


def create_JSON_HTTP(start_line: str, headers: dict, body: str):
    data = {
        "head": [
            start_line,
            headers
        ],
        "body": [
            {
                "content": body
            }
        ]
    }

    return json.dumps(data)
# ====================================================


""" Transforma un mensaje http a una estructura json """


def parse_HTTP_message(http_message):

    head, body = http_message.split(doble_salto)

    headers = head.split(salto)
    start_line = headers.pop(0)  # linea inicial de los headers

    split_headers = dict()

    for header in headers:
        name, content = header.split(separador_headers)
        split_headers[name] = content

    return create_JSON_HTTP(start_line, split_headers, body)


# ====================================================

""" Crea un mensaje http a partir de una estructura json """


def create_HTTP_message(json_message) -> str:
    json_message = json.loads(json_message)
    start_line, head = json_message["head"]
    body = json_message["body"][0]["content"]

    """ print(f"start_line: {start_line}")
    print(f"head: {head}")
    print(f"body: {body}") """

    compose_head = start_line + salto

    for name, content in head.items():
        compose_head = compose_head + name + separador_headers + content + salto

    compose_head += salto

    composed_message = compose_head+body

    # print(f"composed message: \n{composed_message}")

    return composed_message


# test:
json_message = json.dumps({"head": ["GET /pagina-ejemplo HTTP/1.1", {"Host": "www.ejemplo.com", "User-Agent": "MiNavegador/1.0",
                          "Accept": "text/html", "Connection": "keep-alive", "Content-Length": "45"}], "body": [{"content": ""}]})
http_message = "GET /pagina-ejemplo HTTP/1.1\r\nHost: www.ejemplo.com\r\nUser-Agent: MiNavegador/1.0\r\nAccept: text/html\r\nConnection: keep-alive\r\nContent-Length: 45\r\n\r\n"

assert parse_HTTP_message(create_HTTP_message(json_message)) == json_message
assert create_HTTP_message(parse_HTTP_message(http_message)) == http_message
