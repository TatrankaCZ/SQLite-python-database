# Server

from http.server import HTTPServer, BaseHTTPRequestHandler

import random
from urllib.parse import parse_qs
import uuid

class MyServer(BaseHTTPRequestHandler):
    X = 0
    Y = 10

    mistnosti = {}

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        print(self.path)
        if self.path == "/favicon.ico":
            return
        if self.path == "/create":
            hadane_cislo = random.randrange(self.X, self.Y)
            id_mistostni = str(uuid.uuid4())
            self.mistnosti[id_mistostni] = hadane_cislo
            self.wfile.write(bytes(id_mistostni, "utf-8"))

        if self.path == "/list":
            for key in self.mistnosti:
                self.wfile.write(bytes(f"{key}\n", "utf-8"))

        if self.path.startswith("/guess"):
            print("jsme v guess")
            params = parse_qs(self.path[7:])
            print(params)
            print(params["number"])
            print(params["room_id"])
            number = int(params["number"][0])
            room_id = params["room_id"][0]

            if number > self.mistnosti[room_id]:
                self.wfile.write(bytes("MENSI", "utf-8"))
            elif number < self.mistnosti[room_id]:
                self.wfile.write(bytes("VETSI", "utf-8"))
            else:
                self.wfile.write(bytes("UHADNUTO", "utf-8"))
                MyServer.hadane_cislo = random.randrange(self.X, self.Y)





if __name__ == "__main__":
    webServer = HTTPServer(("localhost", 8001), MyServer)
    print("Server started http://%s:%s" % ("localhost", 8001))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


