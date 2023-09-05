import socket
from utils import *

# variables globales ==================

buff_size = 4
address = ('localhost', 8000)

print('Creando servidor ... ')
# socket orientado a conexión

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
    # esta función entrega el mensaje en string (no en bytes) y sin el end_of_message
    print("entrando a recibir mensaje ...")
    recv_message = receive_full_mesage(new_socket, buff_size)

    # respondemos 

    final_response_message = create_response_message(recv_message)
    
    print(f"final response message: {final_response_message}")
    
    # el mensaje debe pasarse a bytes antes de ser enviado, para ello usamos encode
    new_socket.send(final_response_message.encode())

    # cerramos la conexión
    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada")

    # seguimos esperando por si llegan otras conexiones