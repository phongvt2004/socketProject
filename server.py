import socket
from threading import Thread

HOST = '127.0.0.1'
PORT = 8888
FILE_CONFIG = ''



class Server:
    def __init__(self,server,host,port):
        server.bind((host, port))
        server.listen(1)
        self.server = server
        self.cache_exists = False
        self.cache_file = ''
        self.ontime = False
        self.whitelist = False
        
    def handle(conn):
        print("handle")  
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
                self.createThread(conn)
            except Exception as e:
                print(e)
                break
    def cache(self):
        print("cache")
    
    def check_time(self):
        print("time")
    
    def check_whitelist(self):
        print("whitelist")
    
    def check_method(self):
        print(self.data)
        method = self.data.split()[0]
        if (method != "GET" and method != "POST" and method != "HEAD"):
            return False
        else: return True
        
      

# Tạo một socket của server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    print('Server đang lắng nghe kết nối...')
    createServer = Server(server,HOST,PORT)
    createServer.run()
