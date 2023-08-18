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
        self.image_time = {}
        
    def handle(self,conn):
        print("handle")
        cache_time, start_time, end_time, name_whitelist = self.read_extractjson()
        self.check_image_time(self.image_time)
        #test
        check = False
        if (self.check_time(start_time, end_time)):
            print('ok')
        else:
            html = self.response_html()
            response = "HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: " + str(len(html)) + "\r\n\r\n" + str(html)
            
            conn.send(response.encode())
            return
        data = conn.recv(1024).decode('ISO-8859-1')
        if data:
            self.request = data
            if(self.check_method()):
                print(data,'\n')
                new_request = data.split('\r\nHost: ')
                new_request[1] = new_request[1].split('\r\n')
                self.url = new_request[1][0]
                new_request[1] = '\r\n'.join(new_request[1])
                new_request = '\r\nHost: '.join(new_request)
                new_request = new_request.split('\r\n')
                if (self.check_whitelist(name_whitelist, self.url)):
                    print ('ok')
                else:
                    html = self.response_html()
                    response = "HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: " + str(len(html)) + "\r\n\r\n" + str(html)
                    
                    conn.send(response.encode())
                    print('not')
                    print(response)
                    return
                print('ok')
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
                image_url=self.get_image_url_from_request(data)
                print(image_url)
                if image_url:
                    if self.check_image_exist(image_url):
                        response = self.image_response(image_url)
                    else:
                        response = self.request_server(image_url, cache_time)
                else:
                    response = self.request_server(image_url, cache_time)
                conn.send(response.encode('iso-8859-1'))
                conn.close()
            else:
                html = self.response_html()
                response = "HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: " + str(len(html)) + "\r\n\r\n" + str(html)
                
                conn.send(response.encode())
                return
            
    def createThread(self,conn):
        thread=threading.Thread(target= self.handle, args=(conn,))
        thread.start()
        thread.join()
        print (f"Số kết nối: {threading.active_count()-1}")
        
    def run(self):
        while True:
            try:
                conn, address = server.accept()
                print('Đã kết nối từ:', address)
                print("start thread")
                # self.handle(conn)
                self.createThread(conn)
            except Exception as e:
                print(e)
                break
            finally:
                conn.close()

    def check_image_exist(self, image_url):
        image_name = image_url.split("/")[-1]
        # Kiểm tra xem hình ảnh đã tồn tại trong bộ nhớ cache chưa
        image_web = image_url.split('//')[1].split('/')[0]
        image_web = image_web.split('.')
        image_web = '_'.join(image_web)
        print(os.path.join(os.path.dirname('./'),cache_folder,image_web, image_name))
        if os.path.exists(os.path.join(os.path.dirname('./'),cache_folder,image_web, image_name)):
            print("Image exists")
            return True
        else:
            return False

    def get_image_url_from_request(self, request):
        lines = request.split("\r\n")
        accept_line = next((line for line in lines if line.startswith("Accept:")), None)
        if accept_line and ("image" in accept_line):
            request_line = lines[0]
            method, url, _ = request_line.split(" ")
            image_name = url.split("/")[-1]
            if not image_name:
                return None
            return url
        return None
    
    def save_image_cache(self,image_url, data, cache_time):
        # Tạo thư mục cache nếu chưa tồn tại
        image_name = image_url.split("/")[-1]
        image_web = image_url.split('//')[1].split('/')[0]
        image_web = image_web.split('.')
        image_web = '_'.join(image_web)
        print(image_web)
        if not os.path.exists(os.path.join(cache_folder, image_web)):
            os.makedirs(os.path.join(cache_folder, image_web))
        # Phân tích URL để lấy tên tệp hình ảnh
        try:
            response = b""
            response += data
            # Tách phần thân của phản hồi HTTP
            headers, body = response.split(b"\r\n\r\n", 1)
            # Kiểm tra xem phản hồi có mã trạng thái 200 (OK) hay không
            if b"200 OK" in headers:
                # Lưu hình ảnh vào bộ nhớ cache
                with open(os.path.join(cache_folder,image_web, image_name), "wb") as file:
                    file.write(body)
                print("Hình ảnh đã được lưu vào cache.")
                self.image_time[image_web+image_name]=datetime.datetime.now()+datetime.timedelta(minutes=cache_time)
            else:
                print("Không thể lưu hình ảnh từ máy chủ.")
        except Exception as e:
            print("Lỗi trong quá trình lấy và lưu cache hình ảnh:", str(e))
            return None  
        
    def image_response(self, image_url):
        image_name = image_url.split("/")[-1]
        image_web = image_url.split('//')[1].split('/')[0]
        image_web = image_web.split('.')
        image_web = '_'.join(image_web)
        image_type = image_name.split(".")[-1]
        image_path = os.path.join(cache_folder,image_web,image_name)
        with open(image_path, "rb") as f:
            image_data = f.read()
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: image/"+str(image_type)+"\r\n"
        response += "Content-Length: " + str(len(image_data)) + "\r\n"
        response += "\r\n" + str(image_data.decode("iso-8859-1"))
        return response
    
    def delete_image(self, image_name):
        image_path=os.path.join(cache_folder,image_name)
        if os.path.exists(image_path):
            os.remove(image_path)

    def check_image_time(self, dict):
        images_to_delete = [] 
        for image_name,timestamp in dict.items():
            time=datetime.datetime.now()
            if time >= timestamp:
                self.delete_image(image_name)
                images_to_delete.append(image_name)
        for image in images_to_delete:
            del dict[image]
    
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
            if (website_togo.find(website) != -1):
                return True
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
        cache_time = int (data_in.get("cache_time", 0))
        start_time, end_time = self.extract_time(data_in.get("time", ""))
        name_whitelist = data_in.get("whitelisting", [])
        return cache_time, start_time, end_time, name_whitelist
    
    def response_html(self):
        HTMLFile = open("403.html", "r")
        return HTMLFile.read()
    
    def request_server(self, url, cache_time):
        hostn = self.url.replace("www.","",1)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (hostn, 80)
        client_socket.connect(server_address)
        client_socket.send(self.request.encode('iso-8859-1'))
        # self.handle_chunked_encoding(client_socket)
        response = client_socket.recv(4096).decode('iso-8859-1')
        new_response= response
        if(response.split('\r\n\r\n')[0].find('HTTP/1.1') != -1 and response.split('\r\n\r\n')[1].find('HTTP/1.1') != -1):
            response = response.split('\r\n\r\n')
            response.pop(0)
            response = '\r\n\r\n'.join(response)
        if response.find('content-length') != -1:
            response = self.handle_length(client_socket, response, 'content-length')
        elif response.find('Content-Length') != -1:
            response = self.handle_length(client_socket, response,'Content-Length')
        elif response.find('chunked') != -1:
            response = self.handle_chunk(client_socket, response)
        if url:
            self.save_image_cache(url,response.encode('iso-8859-1'), cache_time)
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



