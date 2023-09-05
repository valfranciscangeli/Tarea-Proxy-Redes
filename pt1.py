import socket



# funcion de parseo http a estructura============
def parse_HTTP_message(http_message):
    head_end_str = '\r\n\r\n'
    head_end = http_message.find(head_end_str)
    head = http_message[:head_end]
    body_init = head_end + head_end_str
    body = http_message[body_init:]

    


# =============================
def receive_message(connection_socket, buff_size):
    # recibimos la primera parte del mensaje
    recv_message = connection_socket.recv(buff_size)
    full_message = recv_message

    
    return full_message.decode()



# server ==========================
buff_size = 400
new_socket_address = ('localhost', 8000)

print('Creando socket - Servidor')
# armamos el socket
# los parámetros que recibe el socket indican el tipo de conexión
# socket.SOCK_STREAM = socket orientado a conexión
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# le indicamos al server socket que debe atender peticiones en la dirección address
# para ello usamos bind
server_socket.bind(new_socket_address)

# luego con listen (función de sockets de python) le decimos que puede
# tener hasta 3 peticiones de conexión encoladas
# si recibiera una 4ta petición de conexión la va a rechazar
server_socket.listen(3)

# nos quedamos esperando a que llegue una petición de conexión
print('... Esperando clientes')
while True:
    # cuando llega una petición de conexión la aceptamos
    # y se crea un nuevo socket que se comunicará con el cliente
    new_socket, new_socket_address = server_socket.accept()

    recv_message = receive_message(new_socket, buff_size)


    print(f' -> Se ha recibido el siguiente mensaje: \n {recv_message}')

    # cerramos la conexión
    # notar que la dirección que se imprime indica un número de puerto distinto al 5000
    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada")

    # seguimos esperando por si llegan otras conexiones
