import lex as lex


class Lex_Analyzer:
    def __init__(self, path):
        file = open(path, 'r')
        self.program = file
        self.tokens_list = []
        self.lines_list = []

    def Tokenize(self):
        # Define Tokens
        tokens = [
            'VOID', 'INT', 'DOUBLE', 'BOOL', 'STRING', 'NULL',
            'FOR', 'WHILE', 'IF', 'ELSE', 'RETURN', 'BREAK',
            'PRINT', 'READINTEGER', 'READLINE', 'IDENTIFIER',
            'BOOL_CONST', 'INT_CONST', 'DOUBLE_CONST', 'STRING_CONST', 'PLUS', 'MINUS',
            'MULTIPLY', 'DIVIDE', 'MODULUS',
            'LESS_THAN', 'LESS_THAN_EQUAL',
            'GREATER_THAN', 'GREATER_THAN_EQUAL',
            'EQUAL', 'EQUALITY', 'NOT_EQUAL', 'AND', 'OR', 'NOT',
            'SEMICOLON', 'COMMA', 'POINT', 'LEFT_PAREN', 'RIGHT_PAREN',
            'LEFT_BRACE', 'RIGHT_BRACE'
        ]

        # Specify regex for each token
        t_VOID = r'void'
        t_INT = r'int'
        t_DOUBLE = r'double'
        t_BOOL = r'bool'
        t_STRING = r'string'
        t_NULL = r'null'
        t_FOR = r'for'
        t_WHILE = r'while'
        t_IF = r'if'
        t_ELSE = r'else'
        t_RETURN = r'return'
        t_BREAK = r'break'
        t_PRINT = r'Print'
        t_READINTEGER = r'ReadInteger'
        t_READLINE = r'ReadLine'
        t_IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
        t_BOOL_CONST = r'true | false'
        # t_FALSE = r'false'
        t_INT_CONST = r'[0-9]+'
        t_DOUBLE_CONST = r'[0-9]+\.[0-9]*'
        t_STRING_CONST = r'\"(.*?)\"'
        t_PLUS = r'\+'
        t_MINUS = r'-'
        t_MULTIPLY = r'\*'
        t_DIVIDE = r'/'
        t_MODULUS = r'%'
        t_LESS_THAN = r'<'
        t_LESS_THAN_EQUAL = r'<='
        t_GREATER_THAN = r'>'
        t_GREATER_THAN_EQUAL = r'>='
        t_EQUAL = r'='
        t_EQUALITY = r'=='
        t_NOT_EQUAL = r'!='
        t_AND = r'&&'
        t_OR = r'\|\|'
        t_NOT = r'!'
        t_SEMICOLON = r';'
        t_COMMA = r','
        t_POINT = r'\.'
        t_LEFT_PAREN = r'\('
        t_RIGHT_PAREN = r'\)'
        t_LEFT_BRACE = r'{'
        t_RIGHT_BRACE = r'}'

        # Ignore Spaces and Comments
        t_ignore = ' \t\n'
        t_ignore_COMMENT = r'\/\/.*'

        # Invalid token actions
        def t_error(token):
            # print(f'Invalid Token: {token.value[0]}')
            token.lexer.skip(1)

        # Create Lexer
        lexer = lex.lex()

        # Open and read file to tokenize
        line_count = 1
        for line in self.program:
            self.lines_list.append(line)
            lexer.input(line)
            # Tokens item come as an array of 4 alements [Token, Type, Line, Column]
            for token in lexer:
                # print(token.type, token.value)
                if token.value in ['void', 'int', 'double', 'bool', 'string', 'null', 'for', 'while', 'if', 'else', 'return', 'break', 'Print', 'ReadInteger', 'ReadLine']:
                    tk_str = token.value
                    # self.tokens_list.append([token.value,"T_{}".format((tk_str.capitalize())),line_count,token.lexpos])
                    self.tokens_list.append(
                        {'type': token.value.upper(), 'value': token.value})

                elif token.value in ['true', 'false']:
                    # self.tokens_list.append([token.value,'T_BoolConstant',line_count,token.lexpos])
                    # self.tokens_list.append(token.type)
                    self.tokens_list.append(
                        {'type': token.type, 'value': token.value})

                else:
                    # self.tokens_list.append([token.value,token.type,line_count,token.lexpos])
                    # self.tokens_list.append(token.type)
                    self.tokens_list.append(
                        {'type': token.type, 'value': token.value})

            line_count += 1

        return self.tokens_list, self.lines_list


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def eat(self, token_type):
        if self.tokens[self.index]['type'] == token_type:
            self.index += 1
        else:
            raise Exception(
                f"Unexpected token: {self.tokens[self.index]['type']}")

    def peek(self):
        if self.index + 1 < len(self.tokens):
            return self.tokens[self.index + 1]['type']
        else:
            return None

    def parse_program(self):
        declarations = []

        while self.index < len(self.tokens) and self.tokens[self.index]['type'] != 'EOF':
            if self.tokens[self.index]['type'] in ["INT", "DOUBLE", "BOOL", "STRING", "VOID"]:
                decl = self.parse_decl()
                declarations.append(decl)
            else:
                raise Exception("Invalid token")

        return Program(declarations)

    def parse_decl(self):
        if self.tokens[self.index]['type'] in ["INT", "DOUBLE", "BOOL", "STRING", "VOID"]:
            if self.peek() == 'IDENTIFIER' and self.tokens[self.index + 2]['type'] == 'LEFT_PAREN':
                return self.parse_function_decl()
            else:
                return self.parse_variable_decl()
        else:
            raise Exception("Invalid token")

    def parse_variable_decl(self):
        var_type = Type(self.tokens[self.index]['value'])
        self.eat(self.tokens[self.index]['type'])
        identifier = self.tokens[self.index]['value']
        self.eat('IDENTIFIER')
        self.eat('SEMICOLON')
        return VariableDecl(Variable(var_type, identifier))

    def parse_function_decl(self):
        if self.tokens[self.index]['type'] == "VOID":
            var_type = Type(self.tokens[self.index]['value'])
            self.eat('VOID')
        else:
            var_type = Type(self.tokens[self.index]['value'])
            self.eat(self.tokens[self.index]['type'])

        identifier = self.tokens[self.index]['value']
        self.eat('IDENTIFIER')
        self.eat('LEFT_PAREN')
        formals = self.parse_formals()
        self.eat('RIGHT_PAREN')
        stmt_block = self.parse_stmt_block()

        return FunctionDecl(var_type, identifier, formals, stmt_block)

    def parse_formals(self):
        formals = []

        while self.tokens[self.index]['type'] != 'RIGHT_PAREN':
            var_type = Type(self.tokens[self.index]['value'])
            self.eat(self.tokens[self.index]['type'])
            identifier = self.tokens[self.index]['value']
            self.eat('IDENTIFIER')
            formals.append(Variable(var_type, identifier))

            if self.tokens[self.index]['type'] == 'COMMA':
                self.eat('COMMA')

        return formals

    def parse_stmt_block(self):
        self.eat('LEFT_BRACE')
        variable_decls = []
        stmts = []

        while self.tokens[self.index]['type'] in ["INT", "DOUBLE", "BOOL", "STRING"]:
            variable_decls.append(self.parse_variable_decl())

        while self.tokens[self.index]['type'] != 'RIGHT_BRACE':
            stmts.append(self.parse_stmt())

        self.eat('RIGHT_BRACE')

        return StmtBlock(variable_decls, stmts)

    def parse_stmt(self):
        if self.tokens[self.index]['type'] in ["INT", "DOUBLE", "BOOL", "STRING"]:
            return self.parse_variable_decl()
        elif self.tokens[self.index]['type'] == 'IF':
            return self.parse_if_stmt()
        elif self.tokens[self.index]['type'] == 'WHILE':
            return self.parse_while_stmt()
        elif self.tokens[self.index]['type'] == 'FOR':
            return self.parse_for_stmt()
        elif self.tokens[self.index]['type'] == 'BREAK':
            return self.parse_break_stmt()
        elif self.tokens[self.index]['type'] == 'RETURN':
            return self.parse_return_stmt()
        elif self.tokens[self.index]['type'] == 'PRINT':
            return self.parse_print_stmt()
        elif self.tokens[self.index]['type'] == 'LEFT_BRACE':
            return self.parse_stmt_block()
        else:
            return self.parse_expr_stmt()

    def parse_if_stmt(self):
        self.eat('IF')
        self.eat('LEFT_PAREN')
        expr = self.parse_expr()
        self.eat('RIGHT_PAREN')
        stmt = self.parse_stmt()
        else_stmt = None

        if self.tokens[self.index]['type'] == 'ELSE':
            self.eat('ELSE')
            else_stmt = self.parse_stmt()

        return IfStmt(expr, stmt, else_stmt)

    def parse_while_stmt(self):
        self.eat('WHILE')
        self.eat('LEFT_PAREN')
        expr = self.parse_expr()
        self.eat('RIGHT_PAREN')
        stmt = self.parse_stmt()

        return WhileStmt(expr, stmt)

    def parse_for_stmt(self):
        self.eat('FOR')
        self.eat('LEFT_PAREN')
        init_expr = self.parse_expr()
        self.eat('SEMICOLON')
        cond_expr = self.parse_expr()
        self.eat('SEMICOLON')
        update_expr = self.parse_expr()
        self.eat('RIGHT_PAREN')
        stmt = self.parse_stmt()

        return ForStmt(init_expr, cond_expr, update_expr, stmt)

    def parse_break_stmt(self):
        self.eat('BREAK')
        self.eat('SEMICOLON')
        return BreakStmt()

    def parse_return_stmt(self):
        self.eat('RETURN')
        expr = None

        if self.tokens[self.index]['type'] != 'SEMICOLON':
            expr = self.parse_expr()

        self.eat('SEMICOLON')
        return ReturnStmt(expr)

    def parse_print_stmt(self):
        self.eat('PRINT')
        self.eat('LEFT_PAREN')
        exprs = [self.parse_expr()]

        while self.tokens[self.index]['type'] == 'COMMA':
            self.eat('COMMA')
            exprs.append(self.parse_expr())

        self.eat('RIGHT_PAREN')
        self.eat('SEMICOLON')
        return PrintStmt(exprs)

    def parse_expr_stmt(self):
        expr = self.parse_expr()
        self.eat('SEMICOLON')
        return ExprStmt(expr)

    # Implement parse_expr, parse_lvalue, parse_call, and other functions here
    def parse_expr(self):
        left = self.parse_logical_or_expr()

        while self.tokens[self.index]['type'] in ['EQUAL']:
            operator = self.tokens[self.index]['type']
            self.eat(operator)
            right = self.parse_logical_or_expr()
            left = BinaryExpr(operator, left, right)

        return left

    def parse_logical_or_expr(self):
        left = self.parse_logical_and_expr()

        while self.tokens[self.index]['type'] in ['OR']:
            operator = self.tokens[self.index]['type']
            self.eat(operator)
            right = self.parse_logical_and_expr()
            left = BinaryExpr(operator, left, right)

        return left

    def parse_logical_and_expr(self):
        left = self.parse_equality_expr()

        while self.tokens[self.index]['type'] in ['AND']:
            operator = self.tokens[self.index]['type']
            self.eat(operator)
            right = self.parse_equality_expr()
            left = BinaryExpr(operator, left, right)

        return left

    def parse_equality_expr(self):
        left = self.parse_relational_expr()

        while self.tokens[self.index]['type'] in ['EQUAL_EQUAL', 'NOT_EQUAL']:
            operator = self.tokens[self.index]['type']
            self.eat(operator)
            right = self.parse_relational_expr()
            left = BinaryExpr(operator, left, right)

        return left

    def parse_relational_expr(self):
        left = self.parse_additive_expr()

        while self.tokens[self.index]['type'] in ['LESS', 'LESS_EQUAL', 'GREATER', 'GREATER_EQUAL']:
            operator = self.tokens[self.index]['type']
            self.eat(operator)
            right = self.parse_additive_expr()
            left = BinaryExpr(operator, left, right)

        return left

    def parse_additive_expr(self):
        left = self.parse_multiplicative_expr()

        while self.tokens[self.index]['type'] in ['PLUS', 'MINUS']:
            operator = self.tokens[self.index]['type']
            self.eat(operator)
            right = self.parse_multiplicative_expr()
            left = BinaryExpr(operator, left, right)

        return left

    def parse_multiplicative_expr(self):
        left = self.parse_unary_expr()

        while self.tokens[self.index]['type'] in ['STAR', 'SLASH', 'PERCENT']:
            operator = self.tokens[self.index]['type']
            self.eat(operator)
            right = self.parse_unary_expr()
            left = BinaryExpr(operator, left, right)

        return left

    def parse_unary_expr(self):
        if self.tokens[self.index]['type'] in ['MINUS', 'NOT']:
            operator = self.tokens[self.index]['type']
            self.eat(operator)
            operand = self.parse_unary_expr()
            return UnaryExpr(operator, operand)
        else:
            return self.parse_primary_expr()

    def parse_primary_expr(self):
        if self.tokens[self.index]['type'] == 'IDENTIFIER':
            if self.peek() == 'LEFT_PAREN':
                return self.parse_call()
            else:
                return self.parse_lvalue()
        elif self.tokens[self.index]['type'] == 'LEFT_PAREN':
            self.eat('LEFT_PAREN')
            expr = self.parse_expr()
            self.eat('RIGHT_PAREN')
            return expr
        elif self.tokens[self.index]['type'] in ['INT_CONST', 'DOUBLE_CONST', 'BOOL_CONST', 'STRING_CONST', 'NULL']:
            return self.parse_constant()
        else:
            raise Exception("Invalid token")

    def parse_lvalue(self):
        identifier = self.tokens[self.index]['value']
        self.eat('IDENTIFIER')
        return LValue(identifier)

    def parse_call(self):
        identifier = self.tokens[self.index]['value']
        self.eat('IDENTIFIER')
        self.eat('LEFT_PAREN')
        actuals = self.parse_actuals()
        self.eat('RIGHT_PAREN')
        return Call(identifier, actuals)

    def parse_actuals(self):
        actuals = []

        while self.tokens[self.index]['type'] != 'RIGHT_PAREN':
            actuals.append(self.parse_expr())

            if self.tokens[self.index]['type'] == 'COMMA':
                self.eat('COMMA')

        return actuals

    def parse_constant(self):
        if self.tokens[self.index]['type'] == 'INT_CONST':
            value = int(self.tokens[self.index]['value'])
            self.eat('INT_CONST')
        elif self.tokens[self.index]['type'] == 'DOUBLE_CONST':
            value = float(self.tokens[self.index]['value'])
            self.eat('DOUBLE_CONST')
        elif self.tokens[self.index]['type'] == 'BOOL_CONST':
            value = self.tokens[self.index]['value'] == 'true'
            self.eat('BOOL_CONST')
        elif self.tokens[self.index]['type'] == 'STRING_CONST':
            value = self.tokens[self.index]['value']
            self.eat('STRING_CONST')
        elif self.tokens[self.index]['type'] == 'NULL':
            value = None
            self.eat('NULL')
        else:
            raise Exception("Invalid token")

        return Constant(value)


class Program:
    def __init__(self, declarations):
        self.declarations = declarations

    def __repr__(self):
        return "Program({})".format(self.declarations)


class Decl:
    pass


class VariableDecl(Decl):
    def __init__(self, variable):
        self.variable = variable

    def __repr__(self):
        return f"VariableDecl({self.variable})"


class FunctionDecl(Decl):
    def __init__(self, type_, ident, formals, stmt_block):
        self.type_ = type_
        self.ident = ident
        self.formals = formals
        self.stmt_block = stmt_block

    def __repr__(self):
        return f"FunctionDecl({self.type_}, {self.ident}, {self.formals}, {self.stmt_block})"


class Variable:
    def __init__(self, type_, ident):
        self.type_ = type_
        self.ident = ident

    def __repr__(self):
        return f"Variable({self.type_}, {self.ident})"


class Type:
    def __init__(self, type_):
        self.type_ = type_

    def __repr__(self):
        return f"Type({self.type_})"


class StmtBlock:
    def __init__(self, variable_decls, stmts):
        self.variable_decls = variable_decls
        self.stmts = stmts

    def __repr__(self):
        return f"StmtBlock({self.variable_decls}, {self.stmts})"


class Stmt:
    pass


class ExprStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"ExprStmt({self.expr})"


class IfStmt(Stmt):
    def __init__(self, expr, stmt, else_stmt):
        self.expr = expr
        self.stmt = stmt
        self.else_stmt = else_stmt

    def __repr__(self):
        return f"IfStmt({self.expr}, {self.stmt}, {self.else_stmt})"


class WhileStmt(Stmt):
    def __init__(self, expr, stmt):
        self.expr = expr
        self.stmt = stmt

    def __repr__(self):
        return f"WhileStmt({self.expr}, {self.stmt})"


class ForStmt(Stmt):
    def __init__(self, init_expr, cond_expr, update_expr, stmt):
        self.init_expr = init_expr
        self.cond_expr = cond_expr
        self.update_expr = update_expr
        self.stmt = stmt

    def __repr__(self):
        return f"ForStmt({self.init_expr}, {self.cond_expr}, {self.update_expr}, {self.stmt})"


class BreakStmt(Stmt):
    def __repr__(self):
        return "BreakStmt"


class ReturnStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"ReturnStmt({self.expr})"


class PrintStmt(Stmt):
    def __init__(self, exprs):
        self.exprs = exprs

    def __repr__(self):
        return f"PrintStmt({self.exprs})"


class Expr:
    pass


class LValue(Expr):
    def __init__(self, ident):
        self.ident = ident

    def __repr__(self):
        return f"LValue({self.ident})"


class Call(Expr):
    def __init__(self, ident, actuals):
        self.ident = ident
        self.actuals = actuals

    def __repr__(self):
        return f"Call({self.ident}, {self.actuals})"


class BinaryExpr(Expr):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryExpr({self.operator}, {self.left}, {self.right})"


class UnaryExpr(Expr):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryExpr({self.operator}, {self.operand})"


class Constant(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Constant({self.value})"


class ReadInteger(Expr):
    def __repr__(self):
        return "ReadInteger"


class ReadLine(Expr):
    def __repr__(self):
        return "ReadLine"

