import logging
import socket
import configparser
import threading
import time


def process_message(data):
    try:
        message = data.decode().split()
        print(message)
    except:
        message = ""
        print("empty message")
    if not message:
        message = 'index.html'
    return message


def get_extension(message):
    if message[-1] == '?':
        message = message[:-1]
    try:
        exp = message.split('.')[1]
    except:
        exp = ''

    content = {"css": "text/css", "min": "text/css", "html": "text/html", "png": "image/png", "jpeg": "image/jpeg",
               "js": "text/javascript", "jpg": "image/jpeg", "json": "text/json"}

    try:
        content_type = content[exp]
    except KeyError:
        content_type = None

    return content_type


def process_response(message):
    exp = get_extension(message)
    response = "HTTP/1.1 "
    if not exp:
        logging.info(f'{message} - {addr[0]} - 403 FORBIDDEN')
        response += '403 FORBIDDEN\r\n'

    else:
        try:
            logging.info(f'{message} - {addr[0]} - 200 OK')
            file = open(DIRECTORY + message, "rb")
            message = file.read()
            length = len(message)
            file.close()
            response += "200 OK\r\n"
        except FileNotFoundError:
            response += '404 NOT FOUND\r\n'
            logging.info(f'{message} - {addr[0]} - 404 NOT FOUND')
        else:
            response += f"Content-Type:{exp}\r\n"
            response += f"Date: {time.ctime()}\r\n"
            response += "Server: Server v0.0.1\r\n"
            response += f"Content-Length: {length}\r\n"
            response += "Connection: close\r\n"
            response += "\r\n"
    return response


def get_response(conn):
    while True:
        print("entered get_response")
        logging.info("CONNECTION WITH " + str(conn))
        data = conn.recv(MAX)
        message = process_message(data)
        response = process_response(message)
        if message:
            msg = response.encode() + message
            conn.send(msg)
        else:
            msg = response.encode()
            conn.send(msg)
        logging.info(f'SENT RESPONSE {response}')
        conn.close()
        return


if __name__ == "__main__":
    logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    config = configparser.ConfigParser()
    config.read('config.ini')
    HOST = config["Settings"]["HOST"]
    PORT = int(config["Settings"]["PORT"])
    DEFAULT_PORT = int(config["Settings"]["DEFAULT_PORT"])
    DIRECTORY = config["Settings"]["DIRECTORY"]
    MAX = int(config["Settings"]["MAX"])
    sock = socket.socket()
    try:
        sock.bind((HOST, PORT))
        print("СЕРВЕР РАБОТАЕТ НА ПОРТЕ " + str(PORT))
        logging.info("SERVER IS STARTING ON " + str(PORT))
    except:
        sock.bind(("localhost", DEFAULT_PORT))
        print("SERVER IS STARTING ON 8080")
        logging.info("SERVER IS STARTING ON 8080")
    sock.listen()
    # ================================================

    while True:
        conn, addr = sock.accept()
        print(conn)
        t1 = threading.Thread(target=get_response, args=[conn])
        t1.start()
