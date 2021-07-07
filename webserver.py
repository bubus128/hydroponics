from http.server import HTTPServer, BaseHTTPRequestHandler

class gownoHnadler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-typ', 'text/html')
        self.end_headers()
        Dict = {"temperature": "0", "humidity": "0",
                "water_level": "0", "pH_level": "0",
                "tds_level": "0", "light": "15",}
        if self.path[1:] == "temperature":
            print("X")
        elif self.path[1:] == "humidity":
            print("X")
        elif self.path[1:] == "water_level":
            print("X")
        elif self.path[1:] == "pH_level":
            print("X")
        elif self.path[1:] == "tds_level":
            print("X")
        elif self.path[1:] == "light":
            print("X")
        self.wfile.write(Dict[self.path[1:]].encode())
            
def main():
    PORT = 8080
    server = HTTPServer(('',PORT), gownoHnadler)
    print('Server running on port %s' % PORT)
    server.serve_forever()
        
if __name__ == '__main__':
    main()