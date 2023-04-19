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
        # print(ast)   

        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)

        if semantic_analyzer.has_errors():
            errors = semantic_analyzer.get_errors()
            for error in errors:
                print(error)
        else:
            pass
            #print("No errors Found")

        mips_generator = MIPSCodeGenerator(ast)
        code = mips_generator.generate_code()

        self.save_code_to_file(code, "t1.s")

    def save_code_to_file(self, code, file_name):
        with open(file_name, "w") as file:
            file.write(code)


SintaxAnalyzer(sys.argv[1])