
class MIPSCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.code = ""
        self.indent = 0

    def generate_code(self):
        self.visit(self.ast)
        return self.code

    def visit(self, node):
        if isinstance(node, IntNode):
            self.code += "li $v0, 1\n"
        elif isinstance(node, DoubleNode):
            self.code += "li $v0, 2\n"
        elif isinstance(node, BoolNode):
            self.code += "li $v0, 3\n"
        elif isinstance(node, StringNode):
            self.code += "li $v0, 4\n"
        elif isinstance(node, IfNode):
            self.code += "beq $t0, $zero, else_label\n"
            self.indent += 1
            self.visit(node.condition)
            self.indent -= 1
            self.code += "j end_if_label\n"
            self.code += "else_label:\n"
            self.indent += 1
            self.visit(node.else_body)
            self.indent -= 1
            self.code += "end_if_label:\n"

    def indent_code(self):
        return "    " * self.indent

class Node:
    pass

class IntNode(Node):
    pass

class DoubleNode(Node):
    pass

class BoolNode(Node):
    pass

class StringNode(Node):
    pass

class IfNode(Node):
    def __init__(self, condition, body, else_body):
        self.condition = condition
        self.body = body
        self.else_body = else_body

ast = IfNode(IntNode(), [IntNode()], [DoubleNode()])
generator = MIPSCodeGenerator(ast)
generated_code = generator.generate_code()
print(generated_code)