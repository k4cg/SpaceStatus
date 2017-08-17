#!/usr/bin/python3
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import json
import cgi
from urllib import parse

doc_file = "/var/www/htdocs/spacestatus/heimatlicher_status.json"
#doc_file = "./status.json"

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['content-length'])
        ctype = self.headers['Content-Type']
        data = self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        doc = {}
        with open(doc_file, 'r') as f:
            doc = json.loads(f.read())

        if ctype == 'application/x-www-form-urlencoded':
            postvars = parse.parse_qs(data.decode())
            #refactor postvars
            for key, value in postvars.items():
                if len(value) == 1:
                    postvars[key] = value[0]
            doc.update(postvars)
        elif ctype == 'application/json':
            in_doc = json.loads(data.decode())
            doc.update(in_doc)

        with open(doc_file, 'w') as f:
            f.write(json.dumps(doc))
            f.close()
        

def run_server(server_class=HTTPServer, handler_class=RequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
