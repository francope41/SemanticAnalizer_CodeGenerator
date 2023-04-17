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


        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)


        if semantic_analyzer.has_errors():
            errors = semantic_analyzer.get_errors()
            for error in errors:
                print(error)
        else:
            print("No errors Found")


        # mips_generator = MIPSCodeGenerator(semantic_analyzer)
        # mips_generator.generate(ast)

        # generated_code = '\n'.join(mips_generator.code)
        # print(generated_code)

        #ast_root = Program([FunctionDecl(Type('void'), 'main', [], StmtBlock([VariableDecl(Variable(Type('int'), 'c')), VariableDecl(Variable(Type('string'), 's'))], [ExprStmt(BinaryExpr('EQUAL', LValue('s'), Constant('hello'))), ExprStmt(BinaryExpr('EQUAL', LValue('c'), Call('test', [Constant(4), Constant(5)]))), PrintStmt([LValue('c')]), PrintStmt([LValue('s')])])), FunctionDecl(Type('int'), 'test', [Variable(Type('int'), 'a'), Variable(Type('int'), 'b')], StmtBlock([], [ReturnStmt(BinaryExpr('PLUS', LValue('a'), LValue('b')))]))])

        #analyzer = SemanticAnalyzer()
        #analyzer.analyze(ast_root)
        
        # code_generator = MIPSCodeGenerator(analyzer)
        # code_generator.generate(ast_root)

        # generated_code = code_generator.generated_code

        # for line in generated_code:
        #     print(line)



SintaxAnalyzer(sys.argv[1])