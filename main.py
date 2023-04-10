# Programming Languages and Compilers
# Project 1, Phase II, Parser
# By Eulises Franco - 03/07/2023
#### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -####

# Import required libraries
import sys
import numpy as np
from utils import *
from semantic import SemanticAnalyzer
from codeGen import MIPSCodeGenerator

#### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -####


class SintaxAnalyzer:
    def __init__(self, program):
        #Tokenize Program
        Lexer = Lex_Analyzer(program)
        tokens, linesList = Lexer.Tokenize()
        #Parse Program
        parser = Parser(tokens)
        ast = parser.parse_program()

        semantic_analyzer = SemanticAnalyzer(ast)
        semantic_analyzer.analyze()

        mips_generator = MIPSCodeGenerator()
        mips_generator.generate(ast)

        generated_code = '\n'.join(mips_generator.code)
        print(generated_code)



SintaxAnalyzer(sys.argv[1])