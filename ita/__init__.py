import os
MODULE_PATH = os.path.dirname(__file__)
VERBOSE = True

from ita import loader_file
from ita import parser
from ita import generator

FileLoader = loader_file.FileLoader
Loader = loader_file.FileLoader
Parser = parser.Parser
Generator = generator.Generator

__all__ = ["VERBOSE", "MODULE_PATH", "web", "cli", "Generator", "Parser", "Loader", "FileLoader"] 