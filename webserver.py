from http.server import HTTPServer, BaseHTTPRequestHandler

Dict = {"temperature": "28", "humidity": "0",
        "water_level": "0", "pH_level": "0",
        "tds_level": "0", "light": "15",
        "turn_on_heater" : "ok", "turn_on_cooling" :"ok",
        "turn_off_heater" : "ok", "turn_off_cooling" :"ok",
        }

class hydroponicsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-typ', 'text/html')
        self.end_headers()
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
        elif self.path[1:] == "turn_on_cooling":
            Dict["temperature"] = "23"
        self.wfile.write(Dict[self.path[1:]].encode())
            
def main():
    PORT = 8080
    server = HTTPServer(('',PORT), hydroponicsHandler)
    print('Server running on port %s' % PORT)
    server.serve_forever()
        
if __name__ == '__main__':
    main()