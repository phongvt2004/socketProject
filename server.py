import socket
import json
import datetime
import threading
import os

HOST = '127.0.0.1'
PORT = 8889
FILE_CONFIG = ''
cache_folder='cache'

data = {
    "cache_time": 900, #seconds
    "whitelisting": ["oosc.online", "example.com"],
    "time": "0-24" #range of time
}

class Server:
    def __init__(self,server,host,port):
        server.bind((host, port))
        server.listen(1)
        self.server = server
        self.cache_exists = False
        self.cache_file = ''
        self.request_data = ''
        
    def handle(self,conn):
        print("handle")
        start_time, end_time, name_whitelist = self.read_extractjson()
        if (self.check_time(start_time, end_time)):
            print('ok')
        else:
            html = self.response_html()
            response = "HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: " + str(len(html)) + "\r\n\r\n" + str(html)
            
            conn.send(response.encode())
            return
        data = conn.recv(1024).decode('iso-8859-1')
        if data:
            self.request = data
            if(self.check_method()):
                print(data,'\n')
                url=self.get_image_url_from_request(data)
                new_request = data.split('\r\nHost: ')
                new_request[1] = new_request[1].split('\r\n')
                self.url = new_request[1][0]
                new_request[1] = '\r\n'.join(new_request[1])
                new_request = '\r\nHost: '.join(new_request)
                new_request = new_request.split('\r\n')
                print(new_request,'\n')
                for i in range(len(new_request)):
                    # print(new_request[i].find('Accept-Encoding')+'\r\n')
                    if(new_request[i].find('Accept-Encoding') != -1):
                        new_request.pop(i)
                        break
                for i in range(len(new_request)):
                    if(new_request[i].find('User-Agent') != -1):
                        new_request.pop(i)
                        break
                new_request = '\r\n'.join(new_request)
                self.request = new_request
                print(self.request,'\n')
                response = self.request_server(url)
                print(response,'\n')
                #if url:
                #    self.save_image_cache(url,response)
                # response = '123'
                conn.send(response.encode('iso-8859-1'))
                conn.close()
            else:
                html = self.response_html()
                response = "HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: " + str(len(html)) + "\r\n\r\n" + str(html)
                
                conn.send(response.encode())
                return
            
    def createThread(self,conn):
        thread=threading.Thread(target= Server.handle, args=(self,conn))
        thread.start()
        print (f"Số kết nối: {threading.active_count()-1}")
        
    def run(self):
        while True:
            try:
                conn, address = server.accept()
                print('Đã kết nối từ:', address)
                print("start thread")
                self.handle(conn)
                # self.createThread(conn)
            except Exception as e:
                print(e)
                break
            finally:
                conn.close()

    def get_image_url_from_request(self, request):
        # Tách các dòng trong yêu cầu
        lines = request.split("\r\n")
        # Tìm dòng Accept
        accept_line = next((line for line in lines if line.startswith("Accept:")), None)
        # Kiểm tra xem dòng Accept có tồn tại hay không và có chứa giá trị hình ảnh hay không
        if accept_line and ("image" in accept_line):
            # Lấy dòng yêu cầu (request line)
            request_line = lines[0]
            # Tách các thành phần của dòng yêu cầu
            method, url, _ = request_line.split(" ")
            return url
        return None
    
    def save_image_cache(self,image_url, data):
        # Tạo thư mục cache nếu chưa tồn tại
        # Phân tích URL để lấy tên tệp hình ảnh
        image_name = image_url.split("/")[-1]
        # Kiểm tra xem hình ảnh đã tồn tại trong bộ nhớ cache chưa
        if os.path.exists(os.path.join(cache_folder, image_name)):
            print("Hình ảnh đã tồn tại trong cache.")
            return
        try:
            # Nhận phản hồi từ máy chủ
            response = b""
            response += data
            # Tách phần thân của phản hồi HTTP
            headers, body = response.split(b"\r\n\r\n", 1)
            # Kiểm tra xem phản hồi có mã trạng thái 200 (OK) hay không
            if b"200 OK" in headers:
                # Lưu hình ảnh vào bộ nhớ cache
                with open(os.path.join(cache_folder, image_name), "wb") as file:
                    file.write(body)
                print("Hình ảnh đã được lưu vào cache.")
            else:
                print("Không thể lưu hình ảnh từ máy chủ.")
        except Exception as e:
            print("Lỗi trong quá trình lấy và lưu cache hình ảnh:", str(e))
            return None  
        
    def check_time(self, start_hrs, end_hrs):
        if (start_hrs == None or end_hrs == None):
            return False
        time = datetime.datetime.now()
        current_hour = int(time.strftime("%H"))
        print(current_hour)
        print(start_hrs)
        if (start_hrs <= current_hour and current_hour < end_hrs) :
            return True
        else:
            return False
    
    def check_whitelist(self, list_name, website_togo):
        if not list_name:
            return False
        for website in list_name:
            if (website == website_togo):
                return True
            else:
                return False

    def check_method(self):
        self.method = self.request.split()[0]
        if (self.method != "GET" and self.method != "POST" and self.method != "HEAD"):
            return False
        else: return True

    def extract_time(self, time_string):
        start_time, end_time = map(int, time_string.split('-'))
        return start_time, end_time

    def read_extractjson(self):
        try:
            with open("config.json", "r") as infile:
                data_in = json.load(infile)
        except FileNotFoundError or FileExistsError:
            print('Không thể mở được file config!')
            return None, None, []
        start_time, end_time = self.extract_time(data_in.get("time", ""))
        name_whitelist = data_in.get("whitelisting", [])
        return start_time, end_time, name_whitelist
    
    def response_html(self):
        HTMLFile = open("403.html", "r")
        return HTMLFile.read()
    
    def request_server(self, url):
        hostn = self.url.replace("www.","",1)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (hostn, 80)
        client_socket.connect(server_address)
        client_socket.send(self.request.encode('iso-8859-1'))
        # self.handle_chunked_encoding(client_socket)
        response = client_socket.recv(40960).decode('iso-8859-1')
        new_response= response
        if url:
            self.save_image_cache(url,new_response.encode('iso-8859-1'))
        if(response.split('\r\n\r\n')[0].find('HTTP/1.1') != -1 and response.split('\r\n\r\n')[1].find('HTTP/1.1') != -1):
            response = response.split('\r\n\r\n')
            response.pop(0)
            response = '\r\n\r\n'.join(response)
        print(response)
        if response.find('content-length') != -1:
            response = self.handle_length(client_socket, response, 'content-length')
        elif response.find('Content-Length') != -1:
            response = self.handle_length(client_socket, response,'Content-Length')
        elif response.find('chunked') != -1:
            response = self.handle_chunk(client_socket, response)
        return response
    
    def handle_length(self, client_socket, response,query):
        header = response.split('\r\n\r\n')[0]
        body = response.split('\r\n\r\n')[1]
        total_length = (' '.join(header.split('\r\n'))).split(' ')
        print(total_length)
        total_length = int(total_length[total_length.index(query+":")+1])
        length = len(response)-len(header)-4
        while length < total_length:
            new_receive = client_socket.recv(1024).decode('iso-8859-1')
            length += len(new_receive)
            response+=new_receive
        return response
    
    def handle_chunk(self, client_socket, response):
        body = response.split('\r\n\r\n')[1]
        real_receive = body.split('\r\n')[1]
        while True:
            new_receive = client_socket.recv(1024).decode('iso-8859-1')
            response+=new_receive
            # print(new_receive)
            if response.find('\r\n0\r\n\r\n') != -1:
                print(response.split('\r\n0\r\n\r\n'))
                # if(len(response.split('\r\n0\r\n\r\n')) > 0):
                #     response = response.split('\r\n0\r\n\r\n')[0] + '\r\n0\r\n\r\n'
                break
        print('Đã nhận phản hồi:\r\n', response)
        return response

# Tạo một socket của server
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Server đang lắng nghe kết nối...')
    createServer = Server(server, HOST, PORT)
    createServer.run()
finally:
    server.close()



