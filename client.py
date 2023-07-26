import socket

# Tạo một socket của client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Kết nối đến server qua địa chỉ và cổng
server_address = ('localhost', 3000)
client_socket.connect(server_address)

# Gửi dữ liệu đến server
data = 'GET /www.google.com HTTP/1.0\r\nHost: http://127.0.0.1:12345\r\n\r\n'
client_socket.send(data.encode('utf-8'))

# Nhận phản hồi từ server
response = client_socket.recv(1024).decode('utf-8')
print('Đã nhận phản hồi:', response)

# Đóng kết nối
client_socket.close()
