
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.errors = []

    def analyze(self, ast_root):
        for node in ast_root.declarations:
            self.visit(node)
            
    def visit(self, node):
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{node.__class__.__name__} method")

    def visit_Program(self, node):
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_VariableDecl(self, node):
        variable = node.variable
        if variable.ident in self.symbol_table:
            self.errors.append(f"Variable {variable.ident} is already declared")
        else:
            self.symbol_table[variable.ident] = variable.type_

    def visit_FunctionDecl(self, node):
        if node.ident in self.symbol_table:
            self.errors.append(f"Function {node.ident} is already declared")
        else:
            self.symbol_table[node.ident] = node.type_
            self.visit(node.stmt_block)

    def visit_StmtBlock(self, node):
        for var_decl in node.variable_decls:
            self.visit(var_decl)
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_ExprStmt(self, node):
        self.visit(node.expr)

    def visit_IfStmt(self, node):
        self.visit(node.expr)
        self.visit(node.stmt)
        if node.else_stmt is not None:
            self.visit(node.else_stmt)

    def visit_WhileStmt(self, node):
        self.visit(node.expr)
        self.visit(node.stmt)

    def visit_ForStmt(self, node):
        self.visit(node.init_expr)
        self.visit(node.cond_expr)
        self.visit(node.update_expr)
        self.visit(node.stmt)

    def visit_BreakStmt(self, node):
        pass

    def visit_ReturnStmt(self, node):
        if node.expr is not None:
            self.visit(node.expr)

    def visit_PrintStmt(self, node):
        for expr in node.exprs:
            self.visit(expr)

    def visit_LValue(self, node):
        if node.ident not in self.symbol_table:
            self.errors.append(f"Variable {node.ident} is not declared")

    def visit_Call(self, node):
        if node.ident not in self.symbol_table:
            self.errors.append(f"Function {node.ident} is not declared")
        for actual in node.actuals:
            self.visit(actual)

    def visit_BinaryExpr(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryExpr(self, node):
        self.visit(node.operand)

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
            raise Exception(f"Symbol {symbol_name} not found")
        return symbol