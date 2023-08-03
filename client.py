import socket

# Tạo một socket của client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Kết nối đến server qua địa chỉ và cổng
server_address = ('localhost', 8889)
client_socket.connect(server_address)

# Gửi dữ liệu đến server
data = 'GET /www.google.com HTTP/1.0\r\nHost: http://localhost:8888\r\nConnection: keep-alive\r\n\r\n'
client_socket.send(data.encode('utf-8'))

# Nhận phản hồi từ server
response = client_socket.recv(2048).decode('utf-8')
print('Đã nhận phản hồi:\r\n', response)
while True:
    msg=input()
    client_socket.send(msg.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    print('Đã nhận phản hồi:\r\n', response)
# Đóng kết nối
client_socket.close()
