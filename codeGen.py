from utils import *

class MIPSCodeGenerator:
    def __init__(self):
        self.code = []

    def generate(self, ast_root):
        self.write_data_segment()
        self.write_text_segment()
        self.visit(ast_root)

    def write_data_segment(self):
        self.code.append(".data")

    def write_text_segment(self):
        self.code.append(".text")
        self.code.append(".globl main")

    def visit(self, node):
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{node.__class__.__name__} method")

    def visit_Program(self, node):
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_FunctionDecl(self, node):
        self.code.append(f"{node.identifier}:")
        for formal in node.formals:
            self.visit(formal)
        self.visit(node.stmt_block)

    def visit_VariableDecl(self, node):
        self.visit(node.variable)

    def visit_Variable(self, node):
        pass  # Handle variable code generation

    # Implement other visit methods for each node type here

    def visit_StmtBlock(self, node):
        for var_decl in node.variable_decls:
            self.visit(var_decl)
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_ExprStmt(self, node):
        self.visit(node.expr)

    def visit_PrintStmt(self, node):
        for expr in node.exprs:
            self.visit(expr)
            # Assuming the expression result is stored in $a0

            if expr.type == Type('int'):
                self.code.append("li $v0, 1")  # syscall for printing integer
            elif expr.type == Type('double'):
                self.code.append("li $v0, 3")  # syscall for printing double
            elif expr.type == Type('bool'):
                self.code.append("li $v0, 4")  # syscall for printing bool
            elif expr.type == Type('string'):
                self.code.append("li $v0, 4")  # syscall for printing string
            else:
                raise NotImplementedError(f"Unsupported type for printing: {expr.type}")

            self.code.append("syscall")  # Perform the syscall

    def visit_ReturnStmt(self, node):
        if node.expr is not None:
            self.visit(node.expr)
        self.code.append("jr $ra")

    def visit_LValue(self, node):
        # Assuming the variable's address is stored in the symbol table,
        # and it can be accessed using the variable's identifier
        address = self.symbol_table[node.identifier]

        if address is None:
            raise ValueError(f"Undeclared variable: {node.identifier}")

        # Load the variable value into $a0
        self.code.append(f"lw $a0, {address}($gp)")

    def visit_Call(self, node):
        # Save registers before the function call
        self.code.append("addi $sp, $sp, -4")
        self.code.append("sw $ra, 0($sp)")

        # Push actuals onto the stack
        for actual in node.actuals:
            self.visit(actual)
            # Assuming the actual's value is stored in $a0
            self.code.append("addi $sp, $sp, -4")
            self.code.append("sw $a0, 0($sp)")

        # Call the function
        self.code.append(f"jal {node.identifier}")

        # Restore registers after the function call
        self.code.append("lw $ra, 0($sp)")
        self.code.append("addi $sp, $sp, 4")

        # Pop actuals off the stack
        self.code.append(f"addi $sp, $sp, {4 * len(node.actuals)}")

    def visit_Constant(self, node):
        if isinstance(node.value, int):
            self.code.append(f"li $a0, {node.value}")
            return Type("int")
        elif isinstance(node.value, str):
            # Assuming a string label was created earlier in the data segment
            self.code.append(f"la $a0, {node.value}_label")
            return Type("string")
        else:
            raise Exception("Unsupported constant type")

    def visit_BinaryExpr(self, node):
        self.visit(node.left)
        self.visit(node.right)
        # Perform the operation based on the operator
        pass  # Implement the specific operation for the binary expression here

    def visit_UnaryExpr(self, node):
        self.visit(node.operand)
        # Assuming the operand result is stored in $a0

        if node.operator == "MINUS":
            self.code.append("neg $a0, $a0")  # Negate the result
        elif node.operator == "NOT":
            self.code.append("xori $a0, $a0, 1")  # Logical NOT by XOR-ing with 1
        else:
            raise NotImplementedError(f"Unsupported unary operator: {node.operator}")

    def visit_IfStmt(self, node):
        else_label = self.create_label()
        end_label = self.create_label()

        self.visit(node.expr)  # Evaluate the condition
        # Assuming the condition result is stored in $a0
        self.code.append(f"beqz $a0, {else_label}")  # If the condition is false, go to else_label

        self.visit(node.stmt)  # Execute the true branch
        self.code.append(f"j {end_label}")  # Jump to the end_label

        self.code.append(f"{else_label}:")
        if node.else_stmt is not None:
            self.visit(node.else_stmt)  # Execute the false branch

        self.code.append(f"{end_label}:")

    def visit_WhileStmt(self, node):
        cond_label = self.create_label()
        end_label = self.create_label()

        self.code.append(f"{cond_label}:")
        self.visit(node.expr)  # Evaluate the condition
        # Assuming the condition result is stored in $a0
        self.code.append(f"beqz $a0, {end_label}")  # If the condition is false, go to end_label

        self.visit(node.stmt)  # Execute the loop body
        self.code.append(f"j {cond_label}")  # Jump back to the condition check

        self.code.append(f"{end_label}:")

    def visit_ForStmt(self, node):
        cond_label = self.create_label()
        end_label = self.create_label()

        self.visit(node.init_expr)  # Execute the initialization expression

        self.code.append(f"{cond_label}:")
        self.visit(node.cond_expr)  # Evaluate the condition
        # Assuming the condition result is stored in $a0
        self.code.append(f"beqz $a0, {end_label}")  # If the condition is false, go to end_label

        self.visit(node.stmt)  # Execute the loop body

        self.visit(node.update_expr)  # Execute the update expression
        self.code.append(f"j {cond_label}")  # Jump back to the condition check

        self.code.append(f"{end_label}:")

    def visit_BreakStmt(self, node):
        # Assuming a corresponding end_label was defined in the enclosing loop
        self.code.append(f"j end_label")

   

    # Continue implementing other visit methods for the remaining node types

