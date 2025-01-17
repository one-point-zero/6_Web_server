import socket
import os
from datetime import datetime
import threading

# Определение рабочей директории сервера
WORKING_DIR = os.path.abspath(".") # Устанавливается текущая директория как рабочая для сервера

# Функция для чтения файла из директории сервера
def read_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            return f.read(), 200 # Возвращает содержимое файла и статус код 200 (OK)
    except FileNotFoundError:
        return b"404 Not Found", 404 # Возвращает ошибку 404, если файл не найден

# Формирование HTTP-ответа
def generate_response(status_code, content, content_type="text/html"):
    # Сообщения статусов для ответа
    status_messages = {
        200: "OK",
        404: "Not Found"
    }
    
    status_message = status_messages.get(status_code, "Internal Server Error") # Получение текста статуса
    response = (
        f"HTTP/1.1 {status_code} {status_message}\r\n" # Статусная строка
        f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n" # Текущая дата и время в формате HTTP
        f"Server: SimplePythonServer/0.1\r\n" # Заголовок Server с названием сервера
        f"Content-Length: {len(content)}\r\n" # Длина содержимого ответа в байтах
        f"Content-Type: {content_type}\r\n" # Тип содержимого (по умолчанию text/html)
        f"Connection: close\r\n\r\n" # Закрытие соединения после ответа
    ).encode('utf-8')
    return response + content # Возвращает заголовки и содержимое в одном ответе

# Обработка клиента в отдельном потоке
def handle_client(client_socket):
    with client_socket:
        request = client_socket.recv(1024).decode('utf-8') # Получение запроса от клиента

        if not request: # Если запрос пустой, завершаем обработку
            return

        # Парсинг первой строки запроса
        request_line = request.splitlines()[0] # Первая строка запроса содержит метод, путь и версию протокола
        method, path, _ = request_line.split(" ", 2) # Разделяем строку на метод, путь и протокол

        if method != "GET": # Проверяем, что метод запроса - GET
            response = generate_response(405, b"405 Method Not Allowed") # Если нет, возвращаем ошибку 405
        else:
            # Определение пути к файлу
            if path == "/": # Если путь равен корню, устанавливаем index.html по умолчанию
                path = "/index.html"
            file_path = os.path.join(WORKING_DIR, path.lstrip("/")) # Убираем начальный слэш и формируем полный путь

            # Чтение файла и формирование ответа
            content, status_code = read_file(file_path) # Читаем содержимое файла
            content_type = "text/html" if file_path.endswith(".html") else "application/octet-stream" # Определяем тип содержимого
            response = generate_response(status_code, content, content_type) # Формируем HTTP-ответ

        client_socket.sendall(response) # Отправляем ответ клиенту

# Основная функция сервера
def start_server(host='127.0.0.1', port=8080):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Позволяет повторно использовать адрес сокета
        server_socket.bind((host, port)) # Привязываем сервер к указанному хосту и порту
        server_socket.listen(5) # Начинаем прослушивание соединений (макс. очередь - 5)
        print(f"Сервер запущен на {host}:{port}")

        while True:
            client_socket, client_address = server_socket.accept() # Принимаем новое соединение
            print(f"Новое соединение: {client_address}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket,)) # Создаём поток для клиента
            client_thread.start() # Запускаем поток

# Запуск сервера
if __name__ == "__main__":
    start_server()
