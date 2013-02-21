from ita_parser import Parser
from generator import Generator


p = Parser()

p.loadDir("base")
p.loadDir("cviceni3")

g = Generator( p.rules )
print(g.run("cviceni"))
