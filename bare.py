from ita import Loader, Parser, Generator

loader = Loader("sablony")
parser = Parser( loader )
generator = Generator( parser )

print( generator.run("cviceni") )   