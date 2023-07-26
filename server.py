import socket

# Tạo một socket của server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Lắng nghe kết nối từ client trên cổng 12345
server_socket.bind(('localhost', 12345))
server_socket.listen(1)

print('Server đang lắng nghe kết nối...')

# Chấp nhận kết nối từ client
client_socket, client_address = server_socket.accept()

print('Đã kết nối từ:', client_address)

# Nhận dữ liệu từ client và gửi phản hồi lại
while True:
    data = client_socket.recv(1024).decode('utf-8')
    if data:
        print('Đã nhận:', data)
        response = 'Phản hồi từ server'
        client_socket.send(response.encode('utf-8'))
    # else:
        # break

# Đóng kết nối
client_socket.close()
server_socket.close()
