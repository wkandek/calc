from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote 
import time
import ply.yacc as yacc
import ply.lex as lex

# web server config 
hostName = "0.0.0.0"
serverPort = 8080

# statistics variables
wellformed = 0
nonwellformed = 0


# calculater parser
tokens = (
    'NAME',
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'EQUALS',
    'LPAREN',
    'RPAREN',
)

# Tokens

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'


# parser routines
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lex.lex()

# Precedence rules for the arithmetic operators
precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

# dictionary of names (for storing variables)
names = { }

def p_statement_assign(p):
    'statement : NAME EQUALS expression'
    names[p[1]] = p[3]

def p_statement_expr(p):
    'statement : expression'
    global wellformed 
    p[0] = p[1]
    wellformed = wellformed + 1

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    if p[2] == '+'  : p[0] = p[1] + p[3]
    elif p[2] == '-': p[0] = p[1] - p[3]
    elif p[2] == '*': p[0] = p[1] * p[3]
    elif p[2] == '/': p[0] = p[1] / p[3]

def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = -p[2]

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_expression_name(p):
    'expression : NAME'
    try:
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0

def p_error(p):
    print("Syntax error at '%s'" % p.value)
    global nonwellformed
    nonwellformed = nonwellformed + 1


def write_form(self,result):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes("<html><head><title>Calc</title></head>", "utf-8"))
    self.wfile.write(bytes("<body>", "utf-8"))
    self.wfile.write(bytes(str(result), "utf-8"))
    self.wfile.write(bytes("<br>", "utf-8"))
    self.wfile.write(bytes("<form action='parse' method='post'><input name='tocalc' type='text'><br><input type='submit'></form>", "utf-8"))
    self.wfile.write(bytes("</body></html>", "utf-8"))


def write_healthz(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes("<html><head><title>healthz</title></head>", "utf-8"))
    self.wfile.write(bytes("<body>", "utf-8"))
    self.wfile.write(bytes("CalcVersion=0.1", "utf-8"))
    self.wfile.write(bytes("<br>", "utf-8"))
    self.wfile.write(bytes("wellformed=", "utf-8"))
    self.wfile.write(bytes(str(wellformed), "utf-8"))
    self.wfile.write(bytes("<br>", "utf-8"))
    self.wfile.write(bytes("nonwellformed=", "utf-8"))
    self.wfile.write(bytes(str(nonwellformed), "utf-8"))
    self.wfile.write(bytes("<br>", "utf-8"))
    self.wfile.write(bytes("</body></html>", "utf-8"))


class CalcServer(BaseHTTPRequestHandler):

    def do_GET(self):
        # react to health checks, everything else is a request for a form
        if "/healthz" == self.path[0:8]:
            write_healthz(self)
        elif "/api" == self.path[0:4]:
            logstr = self.path[5:]
            ulogstr = unquote(logstr)
            if "=" in ulogstr:
                operation = ulogstr.split("=",1)[1]
            else:
                operation = ulogstr
            result = parser.parse(operation)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            outstr = "{"+"\"operation\":\"{}\",\"result\":\"{}\"".format(operation,result)+"}"
            self.wfile.write(bytes(str(outstr), "utf-8"))
        else:
            write_form(self,"")

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) 
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        if self.path == "/api":
            logstr = "{0}".format(post_data.decode('utf-8'))
            ulogstr = unquote(logstr)
            if "=" in ulogstr:
                operation = ulogstr.split("=",1)[1]
            else:
                operation = ulogstr
#            self.wfile.write(bytes(str(operation), "utf-8"))
            result = parser.parse(operation)
            outstr = "{"+"\"operation\":\"{}\",\"result\":\"{}\"".format(operation,result)+"}"
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(str(outstr), "utf-8"))
        else:
            logstr = "Body:\n{0}\n".format(post_data.decode('utf-8'))
            ulogstr = unquote(logstr)
            operation = ulogstr.split("=",1)[1]
            result = parser.parse(operation)
            write_form(self, result)

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), CalcServer)
    print("CalcServer started http://%s:%s" % (hostName, serverPort))
    parser = yacc.yacc()

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("CalcServer stopped.")


