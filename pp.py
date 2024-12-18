import http.server
import socketserver
import urllib
import json
import os

# Функция для записи имени и IP-адреса в файл
def save_ip_and_name(name, ip):
    with open("ips.txt", "a") as f:
        f.write(f"{name}: {ip}\n")

# Функция для получения IP для конкретного имени
def get_ip_for_name(name):
    if os.path.exists("ips.txt"):
        with open("ips.txt", "r") as f:
            for line in f:
                name_in_file, ip_in_file = line.strip().split(": ")
                if name_in_file == name:
                    return ip_in_file
    return None

# Функция для получения реального IP-адреса пользователя (если работает в локальной сети)
def get_real_ip(request):
    # Просто получаем IP-адрес клиента, если нет прокси
    ip = request.client_address[0]
    return ip

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Обработка запроса на сохранение имени и IP
        if self.path.startswith("/save_name"):
            # Извлекаем имя из запроса
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            name = query_params.get("name", [""])[0]

            # Получаем реальный IP-адрес пользователя
            client_ip = get_real_ip(self)

            # Проверяем, если у этого имени еще нет IP, то сохраняем его
            existing_ip = get_ip_for_name(name)
            if existing_ip is None:
                save_ip_and_name(name, client_ip)
                # Отправляем успешный ответ с IP
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = json.dumps({"success": True, "ip": client_ip})
                self.wfile.write(response.encode("utf-8"))
            else:
                # Если IP для имени уже существует, отдаем уже сохраненный IP
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = json.dumps({"success": False, "ip": existing_ip})
                self.wfile.write(response.encode("utf-8"))
        else:
            # Обслуживание других запросов (например, index.html)
            if self.path == "/":
                self.path = "/index.html"
            return super().do_GET()

# Устанавливаем порт для сервера
PORT = 1043

# Проверим, существует ли файл ips.txt. Если нет, создадим его.
if not os.path.exists("ips.txt"):
    with open("ips.txt", "w") as f:
        pass

Handler = MyHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Сервер запущен на порту {PORT}")
    httpd.serve_forever()
