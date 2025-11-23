class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        people=[{"name":"Alice", "age":30, "occupation": "Designer"},
                {"name":"Ben", "age":34, "occupation": "Engineer"},
                {"name":"Chloe", "age":22, "occupation": "Student"},
                {"name":"Eve", "age":45, "occupation": "Doctor"},
            ]
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b(""
        "<html>"
             "<head>"
             "    <title>People</title>"
             "</head>"
             "<body>"
                 "<h1>People Directory</h1>"
                 "<table border='1' cellpadding='6' cellspacing='0'>"
                    "<tr>"
                        "<th>Name</th>"
                        "<th>Age</th>"
                        "<th>Occupation</th>"
                    "</tr>"
                    "<tr>"
                        "<td>Alice</td>"
                        "<td>30</td>"
                        "<td>Designer</td>"
                    "</tr>"
                    "<tr>"
                        "<td>Ben</td>"
                        "<td>34</td>"
                        "<td>Engineer</td>"
                    "</tr>"
                    "<tr>"
                        "<td>Chloe</td>"
                        "<td>22</td>"
                        "<td>Student</td>"
                    "</tr>"
                    "<tr>"
                        "<td>David</td>"
                        "<td>41</td>"
                        "<td>Doctor</td>"
                    "</tr>"
             "</body>"
        "</html>"))
  
