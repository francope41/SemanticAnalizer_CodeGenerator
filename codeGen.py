from utils import *

class MIPSCodeGenerator:
    def __init__(self, semantic_analyzer):
        self.code = []
        self.generated_code = []

        self.semantic_analyzer = semantic_analyzer
        self.symbol_table = semantic_analyzer.get_symbol_table()
        self.label_count = 0

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
        self.code.append(f"{node.ident}:")
        for formal in node.formals:
            self.visit(formal)
        self.visit(node.stmt_block)

    def visit_VariableDecl(self, node):
        self.visit(node.variable)

    def visit_Variable(self, variable):
        variable_name = variable.ident
        variable_info = self.semantic_analyzer.find_symbol(variable_name)
        #memory_offset = variable_info['offset']
        memory_offset = variable_info.type_
        load_instr = f"lw $t0, {memory_offset}($fp)"  # Assuming variables are stored in the stack frame
        self.generated_code.append(load_instr)

    def visit_StmtBlock(self, node):
        for var_decl in node.variable_decls:
            self.visit(var_decl)
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_ExprStmt(self, node):
        self.visit(node.expr)
        # If the result of the expression is not used, pop it from the stack
        if not isinstance(node.expr, LValue):
            self.code.append("addi $sp, $sp, 4")

    def visit_PrintStmt(self, node):
        for expr in node.exprs:
            if isinstance(expr, LValue):
                variable_name = expr.ident
                variable_info = self.semantic_analyzer.find_symbol(variable_name)
                expr_type = variable_info.type_
            else:
                expr_type = self.semantic_analyzer.get_expr_type(expr)

            self.visit(expr)

            if expr_type == Type('int'):
                self.code.append("li $v0, 1")  # syscall for printing integer
            elif expr_type == Type('double'):
                self.code.append("li $v0, 3")  # syscall for printing double
            elif expr_type == Type('bool'):
                self.code.append("li $v0, 4")  # syscall for printing bool
            elif expr_type == Type('string'):
                self.code.append("li $v0, 4")  # syscall for printing string
            
            if expr_type == 'int':
                self.code.append("li $v0, 1")  # syscall for printing integer
            elif expr_type == 'double':
                self.code.append("li $v0, 3")  # syscall for printing double
            elif expr_type == 'bool':
                self.code.append("li $v0, 4")  # syscall for printing bool
            elif expr_type == 'string':
                self.code.append("li $v0, 4")  # syscall for printing string
            else:
                raise NotImplementedError(f"Unsupported type for printing: {expr_type}")

            self.code.append("syscall")  # Perform the syscall


    def visit_ReturnStmt(self, node):
        if node.expr is not None:
            self.visit(node.expr)
        self.code.append("jr $ra")

    def visit_LValue(self, lvalue):
        # Assuming lvalue.ident is the name of the variable
        variable_name = lvalue.ident

        # Retrieve the variable's information from the symbol table
        variable_info = self.semantic_analyzer.find_symbol(variable_name)

        # Assuming variable_info contains the memory offset of the variable
        memory_offset = variable_info.type_

        # Generate MIPS code to load the value of the variable into a register
        # Here, we use $t0 as the destination register, you may need to manage
        # register allocation depending on your specific requirements
        load_instr = f"lw $t0, {memory_offset}($fp)"  # Assuming variables are stored in the stack frame
        self.generated_code.append(load_instr)

    def visit_Call(self, node):
        self.code.append("addi $sp, $sp, -4")
        self.code.append("sw $ra, 0($sp)")

        for actual in node.actuals:
            self.visit(actual)
            self.code.append("addi $sp, $sp, -4")
            self.code.append("sw $a0, 0($sp)")

        # Call the function
        self.code.append(f"jal {node.ident}")

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

    # def visit_BinaryExpr(self, node):
    #     left_type = self.visit(node.left)
    #     right_type = self.visit(node.right)

    #     if node.operator == "PLUS":
    #         self.code.append("add $a0, $t0, $t1")
    #     elif node.operator == "MINUS":
    #         self.code.append("sub $a0, $t0, $t1")
    #     elif node.operator == "MUL":
    #         self.code.append("mul $a0, $t0, $t1")
    #     elif node.operator == "DIV":
    #         self.code.append("div $t0, $t1")
    #         self.code.append("mflo $a0")
    #     elif node.operator == "EQUALS":
    #         self.code.append("seq $a0, $t0, $t1")
    #     elif node.operator == "NOT_EQUALS":
    #         self.code.append("sne $a0, $t0, $t1")
    #     elif node.operator == "LESS_THAN":
    #         self.code.append("slt $a0, $t0, $t1")
    #     elif node.operator == "LESS_THAN_EQ":
    #         self.code.append("sle $a0, $t0, $t1")
    #     elif node.operator == "GREATER_THAN":
    #         self.code.append("sgt $a0, $t0, $t1")
    #     elif node.operator == "GREATER_THAN_EQ":
    #         self.code.append("sge $a0, $t0, $t1")
    #     else:
    #         raise NotImplementedError(f"Unsupported binary operator: {node.operator}")

    def visit_BinaryExpr(self, node):
        if node.operator == "PLUS":
            self.visit(node.left)
            self.code.append("sw $a0, 0($sp)")  # Save the result of the left expression on the stack
            self.visit(node.right)
            self.code.append("lw $t0, 0($sp)")  # Load the result of the left expression from the stack
            self.code.append("add $a0, $t0, $a0")  # Perform the addition
            self.code.append("addi $sp, $sp, 4")  # Pop the left expression result from the stack
        elif node.operator == "MINUS":
            self.visit(node.left)
            self.code.append("sw $a0, 0($sp)")  # Save the result of the left expression on the stack
            self.visit(node.right)
            self.code.append("lw $t0, 0($sp)")  # Load the result of the left expression from the stack
            self.code.append("sub $a0, $t0, $a0")  # Perform the subtraction
            self.code.append("addi $sp, $sp, 4")  # Pop the left expression result from the stack
        elif node.operator == "TIMES":
            self.visit(node.left)
            self.code.append("sw $a0, 0($sp)")  # Save the result of the left expression on the stack
            self.visit(node.right)
            self.code.append("lw $t0, 0($sp)")  # Load the result of the left expression from the stack
            self.code.append("mult $t0, $a0")  # Perform the multiplication
            self.code.append("mflo $a0")  # Move the result to $a0
            self.code.append("addi $sp, $sp, 4")  # Pop the left expression result from the stack
        elif node.operator == "DIVIDE":
            self.visit(node.left)
            self.code.append("sw $a0, 0($sp)")  # Save the result of the left expression on the stack
            self.visit(node.right)
            self.code.append("lw $t0, 0($sp)")  # Load the result of the left expression from the stack
            self.code.append("div $t0, $a0")  # Perform the division
            self.code.append("mflo $a0")  # Move the quotient to $a0
            self.code.append("addi $sp, $sp, 4")  # Pop the left expression result from the stack
        elif node.operator == "EQUAL":
            self.visit(node.right)
            self.code.append("sw $a0, 0($sp)")
            self.visit(node.left)
            variable_name = node.left.ident
            variable_info = self.symbol_table[variable_name]
            memory_offset = variable_info.type_
            self.code.append(f"lw $t0, 0($sp)")
            self.code.append(f"sw $t0, {memory_offset}($fp)")
            self.code.append("addi $sp, $sp, 4")  # Pop the right expression result from the stack
        else:
            raise NotImplementedError(f"Unsupported binary operator: {node.operator}")
        


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

    def create_label(self):
        label = f"label{self.label_count}"
        self.label_count += 1
        return label
   

