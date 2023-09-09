import socket
from utils import *


def proxy_func(nombre_JSON="config", puerto=8000, buff_size = 1024):

    # variables globales ==================
    address = ('localhost', puerto)
    username = get_username(nombre_JSON)
    client_error_message = "No puedes ver esto! jaja sl2"

    # ============================

    print('Creando servidor ... ')

    # socket orientado a conexión servidor ======================================
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # le indicamos al server socket que debe atender peticiones en la dirección address
    server_socket.bind(address)

    server_socket.listen(3)                                                                         

    # nos quedamos esperando a que llegue una petición de conexión
    print('... Esperando clientes')
    while True:
        # cuando llega una petición de conexión la aceptamos
        # y se crea un nuevo socket que se comunicará con el cliente
        new_socket, new_socket_address = server_socket.accept()

        # luego recibimos el mensaje usando la función que programamos
        # esta función entrega el mensaje en string (no en bytes)
        print("entrando a recibir mensaje ...")
        recv_message = receive_full_mesage(new_socket, buff_size)
        host = get_server_host(recv_message)
        print(f"cliente pide conectar con: {host}")

        address_forbidden = is_forbidden(get_full_adress(recv_message))                                         

        if address_forbidden:
            final_response_message = create_HTTP_error(client_error_message)

        else:

            # ahora, debemos conectarnos con el servidor antes de responder, pasamos a ser un cliente
            # socket orientado a conexión cliente =======================================
            print("conectando con servidor ...")
            socket_servidor_destino = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_servidor_destino.connect((host, 80)) # http puerto 80 default

            # debemos reenviar el mensaje con nuestro header agregado
            recv_message = process_request(recv_message, username)
            print(f"request recibida procesada: \n {recv_message}")
            print("reenviando request al servidor...")
            socket_servidor_destino.send(recv_message.encode())

            print("recibiendo response del servidor ...")
            server_response = receive_full_mesage(
                socket_servidor_destino, buff_size)
            print(f"se recibió: \n {server_response}")
            
            # cerramos la conexion
            socket_servidor_destino.close()

            # creamos la respuesta
            final_response_message = create_response_message(
                server_response, username)

        # respondemos ===========================================================

        print(f"final response message: {final_response_message}")

        # el mensaje debe pasarse a bytes antes de ser enviado, para ello usamos encode
        new_socket.send(final_response_message.encode())

        # cerramos la conexión
        new_socket.close()
        print(f"conexión con {new_socket_address} ha sido cerrada")

        # seguimos esperando por si llegan otras conexiones


proxy_func() # iniciar proxy

