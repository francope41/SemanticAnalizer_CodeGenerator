from utils import *

class SemanticAnalyzer:
    def __init__(self, ast_program):
        self.ast_program = ast_program
        self.symbol_table = [{}]  # A list of dictionaries to hold symbol tables for each scope

    def analyze(self):
        self.visit_program(self.ast_program)

    def enter_scope(self):
        self.symbol_table.append({})

    def exit_scope(self):
        self.symbol_table.pop()

    def add_symbol(self, symbol, node):
        if symbol in self.symbol_table[-1]:
            raise Exception(f"Symbol '{symbol}' already declared in the current scope")
        self.symbol_table[-1][symbol] = node

    def find_symbol(self, symbol):
        for scope in reversed(self.symbol_table):
            if symbol in scope:
                return scope[symbol]
        raise Exception(f"Symbol '{symbol}' not found in any scope")

    def visit_program(self, program):
        # Visit declarations
        for node in program:
            if isinstance(node, VariableDecl):
                self.visit_variable_decl(node)
            elif isinstance(node, FunctionDecl):
                self.add_symbol(node.ident, node)  # Add function symbol without visiting its body
            else:
                raise Exception("Invalid declaration node")

        # # Visit usage
        # for node in program:
        #     if isinstance(node, FunctionDecl):
        #         self.visit_function_decl(node)


    def visit_variable_decl(self, variable_decl):
        variable = variable_decl.variable
        self.add_symbol(variable.ident, variable)

    def visit_function_decl(self, function_decl):
        self.add_symbol(function_decl.ident, function_decl)

        self.enter_scope()
        for formal in function_decl.formals:
            self.visit_variable_decl(formal)

        self.visit_stmt_block(function_decl.stmt_block)
        self.exit_scope()

    def visit_stmt_block(self, stmt_block):
        self.enter_scope()

        for variable_decl in stmt_block.variable_decls:
            self.visit_variable_decl(variable_decl)

        for stmt in stmt_block.stmts:
            self.visit_stmt(stmt)

        self.exit_scope()

    def visit_stmt(self, stmt):
        if isinstance(stmt, ExprStmt):
            self.visit_expr(stmt.expr)
        elif isinstance(stmt, IfStmt):
            self.visit_expr(stmt.condition)
            self.visit_stmt(stmt.true_branch)
            if stmt.false_branch:
                self.visit_stmt(stmt.false_branch)
        elif isinstance(stmt, WhileStmt):
            self.visit_expr(stmt.condition)
            self.visit_stmt(stmt.body)
        elif isinstance(stmt, ForStmt):
            if stmt.init_expr:
                self.visit_expr(stmt.init_expr)
            self.visit_expr(stmt.condition)
            if stmt.update_expr:
                self.visit_expr(stmt.update_expr)
            self.visit_stmt(stmt.body)
        elif isinstance(stmt, BreakStmt):
            pass
        elif isinstance(stmt, ReturnStmt):
            if stmt.expr:
                self.visit_expr(stmt.expr)
        elif isinstance(stmt, PrintStmt):
            for expr in stmt.exprs:
                self.visit_expr(expr)
        elif isinstance(stmt, StmtBlock):
            self.visit_stmt_block(stmt)
        else:
            raise Exception("Invalid statement node")

    def visit_expr(self, expr):
        if isinstance(expr, BinaryExpr):
            left_type = self.visit_expr(expr.left)
            right_type = self.visit_expr(expr.right)
            # Perform type checking on left_type and right_type and return the resulting type.
            # Return the appropriate type based on your language rules.
        elif isinstance(expr, Constant):
            return expr.value
        elif isinstance(expr, LValue):
            return self.visit_lvalue(expr)
        elif isinstance(expr, Call):
            return self.visit_call(expr)
        elif isinstance(expr, UnaryExpr):
            operand_type = self.visit_expr(expr.operand)
            # Perform type checking on operand_type and return the resulting type.
            # Return the appropriate type based on your language rules.
        else:
            raise Exception("Invalid expression node")

    def visit_lvalue(self, lvalue):
        variable = self.find_symbol(lvalue.ident)
        return variable.type_

    def visit_call(self, call):
        func = self.find_symbol(call.ident)
        if len(call.actuals) != len(func.formals):
            raise Exception("Incorrect number of arguments in function call")

        for actual, formal in zip(call.actuals, func.formals):
            actual_type = self.visit_expr(actual)
            if actual_type != formal.type:
                raise Exception("Type mismatch in function call arguments")

        return func.ret_type
    


