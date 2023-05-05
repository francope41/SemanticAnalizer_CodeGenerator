# Programming Languages and Compilers
# Project 1, Phase II, Parser
# By Eulises Franco - 03/07/2023
#### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -####

# Import required libraries
import sys
import numpy as np
from utils import *
from semantic import SemanticAnalyzer
from CodeGen import ASTToMIPS
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
            quit()
        else:
            pass
            #print("No errors Found")

        mips_generator = MIPSCodeGenerator(ast)
        code = mips_generator.generate_code()

        converter = ASTToMIPS()
        mips_instructions = converter.generate_mips(ast)
        #print(mips_instructions)

        self.save_code_to_file(mips_instructions, "t1.s")

        with open('t1.s', 'r') as f:
            original_contents = f.read()

        # Open the second file for reading
        with open('../pp3-post/defs.asm', 'r') as f:
            defs_contents = f.read()

        # Concatenate the contents of the two files
        new_contents = original_contents + '\n' + defs_contents

        # Open the first file for writing and write the concatenated contents
        with open('t1.s', 'w') as f:
            f.write(new_contents)

    def save_code_to_file(self, code, file_name):
        with open(file_name, "w") as file:
            file.write(code)


SintaxAnalyzer(sys.argv[1])