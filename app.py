import os
import socket
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.buf_size = 1024
        with open('./response.bin', 'rb') as f:
            self.response = f.read()
        self.dir_path = './request'
        self.create_dir(self.dir_path)
    def create_dir(self, dir_path):
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        except OSError:
            print(f"Error: Failed to create the directory.")

    def parse_multipart_data(self, header, data):
        """
        Header Example
        b'POST / HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nUser-Agent: curl/7.81.0\r\nAuthorization: JWT b181ce4155b7413ebd1d86f1379151a7e035f8bd\r\nAccept: application/json\r\nContent-Length: 136108\r\nContent-Type: multipart/form-data; boundary=------------------------26aa1864d1201af9'
        """
        boundary = header.split(b'boundary=')[1]

        # Split the data by boundary
        data_list = data.split(boundary)
        for i in range(1, len(data_list)-1):
            content = data_list[i].split(b'\r\n\r\n',1)
            name = content[0].split(b'name="')[1].split(b'"')[0]
            if name == b'image':
                content_type = content[0].split(b'Content-Type: ')[1].split(b'\r\n')[0]
                content_data = content[1].split(b'\r\n')[0]
                file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.jpg"
                with open(f"{self.dir_path}/{file_name}", 'wb') as f:
                    f.write(content_data)
        return content_type
    


    
    def run(self,ip,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket sever...")
        print("\"Ctrl + C\" to stop the server.")

        try:
            while True:
                client_sock, req_addr = self.sock.accept()
                client_sock.settimeout(5)
                print("Request message...")
                
                recieve_data = b""
                while True:
                    try:
                        buf = client_sock.recv(self.buf_size)
                        recieve_data += buf
                        if not buf:
                            break
                    except socket.timeout:
                        break
                
                if not recieve_data:
                    client_sock.close()
                    continue
                
                header, data = recieve_data.split(b'\r\n\r\n',1)
                content_type = self.parse_multipart_data(header, data)
                print(f"Content-Type: {content_type.decode()}")

                # Save the request data
                with open(f"{self.dir_path}/request_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.bin", 'wb') as f:
                    f.write(recieve_data)

                client_sock.sendall(self.response)

                client_sock.close()
        except KeyboardInterrupt:
            print("Stop the socket server.")
            self.sock.close()

if __name__ == '__main__':
    server = SocketServer()
    server.run("127.0.0.1", 8000)