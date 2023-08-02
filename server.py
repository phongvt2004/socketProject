import socket
import json
import datetime
from threading import Thread

HOST = '127.0.0.1'
PORT = 8888
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
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: " + str(len(html)) + "\r\n\r\n" + str(html)
            
            conn.send(response.encode())
            return
        data = conn.recv(1024).decode('utf-8')
        if data:
            self.data = data
            print('Đã nhận:', data)
            response = 'Phản hồi từ server'
            conn.send(response.encode('utf-8'))
            
    def createThread(self,conn):
        print("createThread")
        
    def run(self):
        while True:
            try:
                conn, address = server.accept()
                print('Đã kết nối từ:', address)
                print("start thread")
                self.handle(conn)
            except Exception as e:
                print(e)
                break
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
        print(self.data)
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
        server_address = (hostn, 80)
        client_socket.connect(server_address)
        data = self.method+' / HTTP/1.0\r\nHost: http://'+self.url+'\r\n\r\n'+self.request_data
        client_socket.send(data.encode('utf-8'))
      

# Tạo một socket của server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    print('Server đang lắng nghe kết nối...')
    createServer = Server(server, HOST, PORT)
    createServer.run()



