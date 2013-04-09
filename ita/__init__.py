VERBOSE = True

from ita import loader_file
from ita import parser
from ita import generator


Loader = loader_file.FileLoader
Parser = parser.Parser
Generator = generator.Generator

__all__ = ["VERBOSE", "web", "cli", "Generator", "Parser", "Loader"] 