from utils import *
class ASTToMIPS:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 2
        self.string_counter = 1
        self.labels = {}
        self.symbol_table = {}

    def get_new_temp(self):
        temp = f"$t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def get_new_string_label(self):
        label = f"_string{self.string_counter}"
        self.string_counter += 1
        return label

    def traverse(self, node):
        if isinstance(node, Program):
            self.instructions.append("\t.text")
            self.instructions.append("\t.align 2")
            self.instructions.append("\t.globl main")

            for child in node.declarations:
                self.traverse(child)
        elif isinstance(node, FunctionDecl):
            self.instructions.append(f"{node.ident}:")
            self.instructions.append("\tsubu $sp, $sp, 8")
            self.instructions.append("\tsw $fp, 8($sp)")
            self.instructions.append("\tsw $ra, 4($sp)")
            self.instructions.append("\taddiu $fp, $sp, 8")

            stack_space = len(node.stmt_block.variable_decls) * 4
            self.instructions.append(f"\tsubu $sp, $sp, {stack_space}")

            for child in node.stmt_block.variable_decls + node.stmt_block.stmts:
                self.traverse(child)

            # EndFunc
            self.instructions.append("\tmove $sp, $fp")
            self.instructions.append("\tlw $ra, -4($fp)")
            self.instructions.append("\tlw $fp, 0($fp)")
            self.instructions.append("\tjr $ra")
        elif isinstance(node, VariableDecl):
            pass
        elif isinstance(node, ExprStmt):
            self.traverse(node.expr)
        elif isinstance(node, BinaryExpr):
            left_temp = self.traverse(node.left)
            right_temp = self.traverse(node.right)
            result_temp = self.get_new_temp()

            if node.operator == 'EQUAL':
                if left_temp.startswith('$'):  # If left_temp is a register
                    self.instructions.append(f"\tsw {right_temp}, 0({left_temp})")
                else:  # If left_temp is an offset
                    self.instructions.append(f"\tsw {right_temp}, {left_temp}")
            elif node.operator == 'PLUS':
                left_value_temp = self.get_new_temp()
                right_value_temp = self.get_new_temp()
                self.instructions.append(f"\tlw {left_value_temp}, {left_temp}")
                self.instructions.append(f"\tlw {right_value_temp}, {right_temp}")
                self.instructions.append(f"\tadd {result_temp}, {left_value_temp}, {right_value_temp}")

            return result_temp
        elif isinstance(node, LValue):
            if node.ident not in self.symbol_table:
                index = len(self.symbol_table)
                self.symbol_table[node.ident] = index

            offset = -(self.symbol_table[node.ident] + 1) * 4
            return f'{offset}($fp)'
        elif isinstance(node, Constant):
            if isinstance(node.value, int):
                self.instructions.append(f"li {self.temp_counter}, {node.value}")
            elif isinstance(node.value, str):
                label = f"_string{len(self.symbol_table)}"
                self.instructions.append(f".data")
                self.instructions.append(f"{label}: .asciiz {node.value}")
                self.instructions.append(f".text")
                #self.instructions.append(f"la {self.temp_counter}, {label}")
                self.instructions.append(f"la $t{self.temp_counter}, {label}")

                self.symbol_table[node.value] = label
            temp = f"$t{self.temp_counter}"
            self.temp_counter += 1
            return temp
        elif isinstance(node, Call):
            self.instructions.append(f"\tjal {node.ident}")
            for arg in node.actuals:
                self.traverse(arg)

    def generate_mips(self,ast):
        mips_generator = ASTToMIPS()
        mips_generator.traverse(ast)
        mips_code = "\n".join(mips_generator.instructions)
        return mips_code