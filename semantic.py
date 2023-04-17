from utils import *


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.errors = []
        self.loop_depth = 0
        self.current_function_name = None  # Add current function name attribute

    def analyze(self, ast_root):
        for node in ast_root.declarations:
            self.Functions_toSymbols(node)
        
        for node in ast_root.declarations:
            self.visit(node)

    def visit(self, node):
        method_name = "visit_{}".format(node.__class__.__name__)
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception("No visit_{} method".format(node.__class__.__name__))

    def visit_Program(self, node):
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_VariableDecl(self, node):
        variable = node.variable
        if variable.ident in self.symbol_table:
            self.errors.append(
                "Variable {} is already declared".format(variable.ident))
        else:
            self.symbol_table[variable.ident] = variable.type_

    def visit_FunctionDecl(self, node):
        # if node.ident in self.symbol_table:
        #     self.errors.append("Function {} is already declared".format(node.ident))
        # else:
        #     self.symbol_table[node.ident] = {
        #         'type':node.type_,
        #         'formals':node.formals
        #     }

            for formal in node.formals:
                self.visit(formal)
                #self.symbol_table.add_symbol(formal.variable.ident, formal.variable)

            self.current_function_name = node.ident  # Set current function name
            self.visit(node.stmt_block)
            self.current_function_name = None  # Clear current function name after visiting

    def visit_Variable(self, node):
        if node.ident in self.symbol_table:
            self.errors.append("Function {} is already declared".format(node.ident))
        else:
            self.symbol_table[node.ident] = node.type_

    def visit_StmtBlock(self, node):
        for var_decl in node.variable_decls:
            self.visit(var_decl)
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_ExprStmt(self, node):
        self.visit(node.expr)

    def get_expr_type(self, expr):
        if isinstance(expr, Constant):
            if isinstance(expr.value,int):
                return Type('int')
            elif isinstance(expr.value,float):
                return Type('double')
            elif isinstance(expr.value,bool):
                return Type('bool')
            
            elif isinstance(expr.value,str):
                return Type('string')
            else:
                raise NotImplementedError("Unsupported constant type {}".format(type(expr.value).__name__))

        elif isinstance(expr, LValue):
            symbol = self.find_symbol(expr.ident)
            if symbol is None:
                self.errors.append("Undeclared variable: {}".format(expr.ident))    
                return None
            
            try:
                return Type(symbol.type_)
            except:
                return Type(symbol["type"].type_)
        elif isinstance(expr, BinaryExpr):

            left_type = self.get_expr_type(expr.left)
            right_type = self.get_expr_type(expr.right)   
            if left_type is None or right_type is None:
                return None
            
            operator = expr.operator
           
            if operator in {'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE','MODULUS'}:
                if operator == 'PLUS':
                    oper_sign = '+'
                elif operator == 'MINUS':
                    oper_sign = '-'
                elif operator == 'MULTIPLY':
                    oper_sign = '*'
                elif operator == 'DIVIDE':
                    oper_sign = '/'
                elif operator == 'MODULUS':
                    oper_sign = '%'

                if left_type.type_ in {'int', 'double'} and right_type.type_ in {'int', 'double'}:
                    return Type('double') if left_type.type_ == 'double' or right_type.type_ == 'double' else Type('int')
                else:
                    self.errors.append("*** Incompatible operands: {} {} {}".format(left_type.type_, oper_sign, right_type.type_))

            elif operator in {'AND','OR'}:
                if operator == 'AND':
                    oper_sign = '&&'
                elif operator == 'OR':
                    oper_sign = '||'
                elif operator == 'NOT':
                    oper_sign = '!'

                if left_type.type_ == 'bool' and right_type.type_ == 'bool':
                    return Type('bool')
                else:
                    self.errors.append("*** yIncompatible operands: {} {} {}".format(left_type.type_, oper_sign, right_type.type_))
                    return None
                
            elif operator in {'EQUAL', 'NOT_EQUAL', 'LESS_THAN', 'LESS_THAN_EQUAL', 'GREATER_THAN', 'GREATER_THAN_EQUAL'}:
                if operator == 'EQUAL':
                    oper_sign = '='
                elif operator == 'NOT_EQUAL':
                    oper_sign = '!='
                elif operator == 'LESS_THAN':
                    oper_sign = '<'
                elif operator == 'LESS_THAN_EQUAL':
                    oper_sign = '<='
                elif operator == 'GREATER_THAN':
                    oper_sign = '>'
                elif operator == 'GREATER_THAN_EQUAL':
                    oper_sign = '>='
                
                if left_type.type_ in {'int', 'double'} and right_type.type_ in {'int', 'double'}:
                    return Type('bool')
                else:
                    self.errors.append("*** zIncompatible operands: {} {} {}".format(left_type.type_, operator, right_type.type_))
                    return None
            else:
                raise NotImplementedError(
                    "Unsupported binary operator: {}".format(operator))
            
        elif isinstance(expr, UnaryExpr):
            operand_type = self.get_expr_type(expr.operand)
            operator = expr.operator
            if operator == 'MINUS':
                if operand_type.type_ in {'int', 'double'}:
                    return operand_type
                else:
                    self.errors.append("*** Incompatible operand: {} {}".format(operator, operand_type.type_))
                    return None
                
            elif operator == 'NOT':
                if operand_type.type_ == 'bool':
                    return Type('bool')
                else:
                    self.errors.append("*** Incompatible operand: {} {}".format(operator, operand_type.type_))
                    return None
            else:
                raise NotImplementedError("Unsupported unary operator: {}".format(operator))
            
        elif isinstance(expr, Call):
            function_name = expr.ident
            function_info = self.find_symbol(function_name)
            if function_info is None:
                self.errors.append("Undeclared function: {}".format(function_name))
                return None
            
            if len(expr.actuals) != len(function_info['formals']):
                self.errors.append("Function {} called with incorrect number of arguments".format(function_name))
                return None
            
            has_error = False
            for actual, formal in zip(expr.actuals, function_info['formals']):
                actual_type = self.get_expr_type(actual)
                formal_type = formal.type_
                print(expr.actuals)
                if actual_type.type_ != formal_type.type_:
                    self.errors.append(
                    "Type mismatch in function call: {} passed for {}".format(actual_type, formal_type))
                    has_error = True

            if has_error:
                return None
            return Type(function_info['type'])
            #return function_info['return_type']
        else:
            raise NotImplementedError(
                "Unsupported expression type: {}".format(type(expr).__name__))

    def visit_IfStmt(self, node):
        self.visit(node.expr)
        self.visit(node.stmt)
        if node.else_stmt is not None:
            self.visit(node.else_stmt)

    def visit_WhileStmt(self, node):
        self.loop_depth += 1
        self.visit(node.expr)
        self.visit(node.stmt)
        self.loop_depth -= 1

    def visit_ForStmt(self, node):
        self.loop_depth += 1
        self.visit(node.init_expr)
        self.visit(node.cond_expr)
        cond_expr_type = self.get_expr_type(node.cond_expr)
        if cond_expr_type.type_ != 'bool':
            self.errors.append("Test expression must have boolean type")
        
        self.visit(node.update_expr)
        self.visit(node.stmt)
        self.loop_depth -= 1

    def visit_BreakStmt(self, node):
        if self.loop_depth == 0:  # Check if we are not inside a loop
            self.errors.append("break is only allowed inside a loop")

    def visit_ReturnStmt(self, node):
        if node.expr is not None:
            actual_return_type = self.get_expr_type(node.expr)
            expected_return_type = self.symbol_table[self.current_function_name]['type']
            if actual_return_type.type_ != expected_return_type.type_:
                self.errors.append("Incompatible return: {} given, {} expected".format(actual_return_type.type_, expected_return_type.type_))
        else:
            expected_return_type = self.symbol_table[self.current_function_name]['type']
            if expected_return_type.type_ != 'void':
                self.errors.append("Incompatible return: void given, {} expected".format(expected_return_type.type_))

    def visit_PrintStmt(self, node):
        for expr in node.exprs:
            self.visit(expr)

    def visit_LValue(self, node):
        if node.ident not in self.symbol_table:
            self.errors.append("Variable {} is not declared".format(node.ident))

    def visit_Call(self, node):
        if node.ident not in self.symbol_table:
            self.errors.append("Function {} is not declared".format(node.ident))
        
        function_info = self.find_symbol(node.ident)

        # Check the length of the arguments.
        if len(node.actuals) != len(function_info['formals']):
            self.errors.append("Function {} called with incorrect number of arguments".format(node.ident))
        else:
            # Compare the actual argument types with the expected argument types.
            for idx, (actual, formal) in enumerate(zip(node.actuals, function_info['formals'])):
                actual_type = self.get_expr_type(actual)
                formal_type = formal.type_
                if actual_type.type_ != formal_type.type_:
                    self.errors.append("Incompatible argument {}: {} given, {} expected".format(idx + 1, actual_type.type_, formal_type.type_))

        for actual in node.actuals:
            self.visit(actual)

    def visit_BinaryExpr(self, node):
        self.visit(node.left)
        self.visit(node.right)
        left_type = self.get_expr_type(node.left)
        right_type = self.get_expr_type(node.right)

        # print(node.operator)
        if left_type and right_type:

            if node.operator in {'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE','MODULUS'}:
                if node.operator == 'PLUS':
                    oper_sign = '+'
                elif node.operator == 'MINUS':
                    oper_sign = '-'
                elif node.operator == 'MULTIPLY':
                    oper_sign = '*'
                elif node.operator == 'DIVIDE':
                    oper_sign = '/'
                elif node.operator == 'MODULUS':
                    oper_sign = '%'

                if (left_type.type_ == 'int' and right_type.type_ == 'double') or (left_type.type_ == 'double' and right_type.type_ == 'int'):
                    self.errors.append("*** Incompatible operands: {} {} {}".format(left_type.type_, oper_sign, right_type.type_))

            elif node.operator in {'AND','OR','NOT'}:
                if node.operator == 'AND':
                    oper_sign = '&&'
                elif node.operator == 'OR':
                    oper_sign = '||'
                elif node.operator == 'NOT':
                    oper_sign = '!'

                if left_type.type_ == 'bool' and right_type.type_ == 'bool':
                    return Type('bool')
                    
                else:
                    self.errors.append("*** Incompatible operands: {} {} {}".format(left_type.type_, oper_sign, right_type.type_))
                    return None
                
            elif node.operator in {'EQUAL', 'NOT_EQUAL', 'LESS_THAN', 'LESS_THAN_EQUAL', 'GREATER_THAN', 'GREATER_THAN_EQUAL'}:
                if node.operator == 'EQUAL':
                    oper_sign = '='
                elif node.operator == 'NOT_EQUAL':
                    oper_sign = '!='
                elif node.operator == 'LESS_THAN':
                    oper_sign = '<'
                elif node.operator == 'LESS_THAN_EQUAL':
                    oper_sign = '<='
                elif node.operator == 'GREATER_THAN':
                    oper_sign = '>'
                elif node.operator == 'GREATER_THAN_EQUAL':
                    oper_sign = '>='
                
                if left_type and right_type:
                    if (left_type.type_ in {'int','double','bool'} and right_type.type_ in {'int','double','bool'}):
                        if left_type.type_ != right_type.type_:
                            # print(left_type)
                            # print(node.operator)
                            # print(right_type)
                            self.errors.append("*** Incompatible operands: {} {} {}".format(left_type.type_, node.operator, right_type.type_))
                            return None
                        else:
                            return Type('bool')
            else:
                self.get_expr_type(node)
                # raise NotImplementedError(
                #     "Unsupported binary node.operator: {}".format(node.operator))
        
    def visit_UnaryExpr(self, node):
        self.visit(node.operand)
        operand_type = self.get_expr_type(node.operand)
        operator = node.operator

        if operator == 'MINUS':
            if operand_type.type_ not in {'int', 'double'}:
                self.errors.append("*** Incompatible operand: {} {}".format('-', operand_type.type_))
        elif operator == 'NOT':
            if operand_type.type_ != 'bool':
                self.errors.append("*** Incompatible operand: {} {}".format("!", operand_type.type_))
        else:
            raise NotImplementedError("Unsupported unary operator: {}".format(operator))
        
    def visit_Constant(self, node):
        pass

    def visit_ReadInteger(self, node):
        pass

    def visit_ReadLine(self, node):
        pass

    def get_symbol_table(self):
        return self.symbol_table

    def has_errors(self):
        return len(self.errors) > 0

    def get_errors(self):
        return self.errors

    def find_symbol(self, symbol_name):
        symbol = self.symbol_table.get(symbol_name)
        if symbol is None:
            raise Exception("Symbol {} not found".format(symbol_name))
        return symbol

    def Functions_toSymbols(self, node):
        if isinstance(node,VariableDecl):
            variable = node.variable
            if variable.ident in self.symbol_table:
                self.errors.append(
                    "Variable {} is already declared".format(variable.ident))
            else:
                self.symbol_table[variable.ident] = variable.type_

        elif isinstance(node, FunctionDecl):
            if node.ident in self.symbol_table:
                self.errors.append("Function {} is already declared".format(node.ident))
            else:
                self.symbol_table[node.ident] = {
                    'type':node.type_,
                    'formals':node.formals
                }
