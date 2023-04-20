from utils import *

class MIPSCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.code = ""
        self.string_constants = []
        self.tmp_counter = 0

    def generate_code(self):
        main_found = False
        self.code += "# standard Decaf preamble\n"
        self.code += "  .text\n"
        self.code += "  .align 2\n"
        self.code += "  .globl main\n"

        for decl in self.ast.declarations:
            if isinstance(decl, FunctionDecl):
                if decl.ident == "main":
                    main_found = True
                self.process_function_decl(decl)

        if not main_found:
            print("*** Error.\n*** Linker: function 'main' not defined")
            quit()
        
        return self.code

    def process_function_decl(self, function_decl):
        self.code += "{}:\n".format(function_decl.ident)
        self.code += "	# BeginFunc\n"
        self.code += "      subu $sp, $sp, 8  # decrement sp to make space to save ra, fp\n"
        self.code += "	  sw $fp, 8($sp)	# save fp\n"
        self.code += "	  sw $ra, 4($sp)	# save ra\n"
        self.code += "      addiu $fp, $sp, 8  # set up new fp\n"
        self.code += "	  subu $sp, $sp, 24	# decrement sp to make space for locals/temps\n"
        #self.code += "    sw $ra, 0($sp)  # save return address\n"

        for stmt in function_decl.stmt_block.stmts:
            if isinstance(stmt, ExprStmt):
                self.process_expr(stmt.expr)
            elif isinstance(stmt, PrintStmt):
                self.process_print_stmt(stmt)
        #self.code += "  lw $ra, 0($sp)  # restore return address\n"
        self.code += "      move $sp, $fp		# pop callee frame off stack\n"
        self.code += "	  lw $ra, -4($fp)	# restore saved ra\n"
        self.code += "	  lw $fp, 0($fp)	# restore saved fp\n"
        self.code += "  jr $ra  # return to caller\n"

    def process_expr(self, expr):
        if isinstance(expr, BinaryExpr):
            self.process_binary_expr(expr)
        elif isinstance(expr, Call):
            self.process_call(expr)
        elif isinstance(expr, Constant) and isinstance(expr.value, str):  # Handle string constants
            self.process_string_constant(expr)

    def process_binary_expr(self, binary_expr):
        # Assuming left and right operands are either Constant or LValue
        left_operand = binary_expr.left
        right_operand = binary_expr.right

        if isinstance(left_operand, Constant):
            self.code += f"  li $t0, {left_operand.value}\n"
        elif isinstance(left_operand, LValue):
            self.code += f"  lw $t0, {left_operand.ident}\n"

        if isinstance(right_operand, Constant):
            self.code += f"  li $t1, {right_operand.value}\n"
        elif isinstance(right_operand, LValue):
            self.code += f"  lw $t1, {right_operand.ident}\n"

        if binary_expr.operator == "PLUS":
            self.code += "  add $t2, $t0, $t1\n"
        elif binary_expr.operator == "MINUS":
            self.code += "  sub $t2, $t0, $t1\n"
        elif binary_expr.operator == "MULTIPLY":
            self.code += "  mul $t2, $t0, $t1\n"
        elif binary_expr.operator == "DIVIDE":
            self.code += "  div $t2, $t0, $t1\n"
        # Add other binary operators as needed

        self.code += f"  sw $t2, {binary_expr.left.ident}\n"

    def process_call(self, call):
        # Assuming this handles print integer and print string calls only
        if call.ident == "_PrintInt":
            self.code += "  li $v0, 1  # system call for print integer\n"
            self.code += "  syscall\n"
        elif call.ident == "_PrintString":
            self.code += "  li $v0, 4  # system call for print string\n"
            self.code += "  syscall\n"

    def process_print_stmt(self, print_stmt):
        for expr in print_stmt.exprs:
            if isinstance(expr, LValue):
                self.code += f" lw $a0, {expr.ident}\n"
                # self.process_call(Call("_PrintInt" if isinstance(expr, Constant) else "_PrintString", []))
                # self.code += " la $a0, newline\n"
                # self.process_call(Call("_PrintString", []))
            elif isinstance(expr, Constant):
                if isinstance(expr.value, int):
                    self.code += f" li $a0, {expr.value}\n"
                    # self.process_call(Call("_PrintInt", []))
                elif isinstance(expr.value, str):
                    index = self.string_constants.index(expr.value)
                    self.code += f" la $a0, str{index}\n"
                    # self.process_call(Call("_PrintString", []))
                    # self.code += " la $a0, newline\n"
                    # self.process_call(Call("_PrintString", []))

            self.code += "  subu $sp, $sp, 4  # decrement sp to make space for param\n"
            self.code += "  sw $t0, 4($sp)    # copy param value to stack\n"
            self.code += "  jal _PrintInt\n" if isinstance(expr, Constant) and isinstance(expr.value, int) else "  jal _PrintString\n"
            self.code += "  add $sp, $sp, 4  # pop params off stack\n"

    def process_string_constant(self, expr):
        string_value = expr.value
        if string_value not in self.string_constants:
            label = f"_string{len(self.string_constants) + 1}"
            self.string_constants[string_value] = label
            self.code += "  .data\n"
            self.code += f"  {label}: .asciiz \"{string_value}\"\n"
            self.code += "  .text\n"
        else:
            label = self.string_constants[string_value]

        tmp_name = self.new_tmp()
        self.code += f"  la $t2, {label}\n"
        self.code += f"  sw $t2, {tmp_name}($fp)\n"


    def new_tmp(self):
        tmp_name = f"_tmp{self.tmp_counter}"
        self.tmp_counter += 1
        return tmp_name
