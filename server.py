import socket
import json
import datetime
import threading

HOST = '127.0.0.1'
PORT = 8889
FILE_CONFIG = ''

data = {
    "cache_time": 900, #seconds
    "whitelisting": ["oosc.online", "example.com"],
    "time": "8-20" #range of time
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
        start_time, end_time = self.read_extractjson()
        if (self.check_time(start_time, end_time)):
            print('ok')
        else:
            html = self.response_html()
            response = "HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: " + str(len(html)) + "\r\n\r\n" + str(html)
            
            conn.send(response.encode())
            return
        data = conn.recv(1024).decode('utf-8')
        if data:
            self.data = data
            if(self.check_method()):
                print(data)
                self.url = data.split()[1].partition("/")[2]
                self.request_data = data.split('\r\n\r\n')[1]
                response = self.request_server()
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
                #self.handle(conn)
                self.createThread(conn)
            except Exception as e:
                print(e)
                break
            finally:
                conn.close()
    def cache(self):
        print("cache")
    
    def check_time(self, start_hrs, end_hrs):
        time = datetime.datetime.now()
        current_hour = int(time.strftime("%H"))
        if (start_hrs <= current_hour and current_hour <= end_hrs) :
            return True
        else:
            return False
    
    def check_whitelist(self):
       print("whitelist")



    def check_method(self):
        self.method = self.data.split()[0]
        if (self.method != "GET" and self.method != "POST" and self.method != "HEAD"):
            return False
        else: return True

    def extract_time(self, time_string):
        start_time, end_time = map(int, time_string.split('-'))
        return start_time, end_time

    def read_extractjson(self):
        with open("config.json", "r") as infile:
            data_in = json.load(infile)
        start_time, end_time = self.extract_time(data_in["time"])
        return start_time, end_time
    
    def response_html(self):
        HTMLFile = open("403.html", "r")
        return HTMLFile.read()
    
    def request_server(self):
        hostn = self.url.replace("www.","",1)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (hostn, 80)
        client_socket.connect(server_address)
        data = self.method+' / HTTP/1.1\r\nHost: '+self.url+self.request_data+'\r\nConnection: keep-alive'+'\r\n\r\n'
        print(data)
        client_socket.send(data.encode('utf-8'))
        # self.handle_chunked_encoding(client_socket)
        response = client_socket.recv(4096).decode('iso-8859-1')
        # response = self.handle_chunk(client_socket, response)
        print('Đã nhận phản hồi:\r\n', response)
        return response
    
    def handle_chunk(self, client_socket, response):
        body = response.split('\r\n\r\n')[1]
        length = body.split('\r\n')[0]
        length = int(length, base=16)
        real_receive = body.split('\r\n')[1]
        real_receive_length = len(real_receive)
        while True:
            new_receive = client_socket.recv(1024).decode('iso-8859-1')
            real_receive_length += len(new_receive)
            response+=new_receive
            # print(new_receive)
            if response.find('\r\n0\r\n\r\n') != -1:
                response = response.split('\r\n0\r\n\r\n')[0] + '\r\n0\r\n\r\n'
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



