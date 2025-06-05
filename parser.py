import sys
import re

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.current_token = self.tokens[self.current_index] if self.tokens else (0, "EOF", "$")
        self.parse_tree = []
        self.syntax_errors = []
        self.tree_depth = 0
        self.error_encountered = False
        self.error_line = None
        
        # Centralized grammar rules mapping to handlers
        self.grammar_rules = {
            "Program": self.handle_program,
            "Declaration-list": self.handle_declaration_list_rule,
            "Declaration": self.handle_declaration_rule,
            "Declaration-initial": self.handle_declaration_initial_rule,
            "Declaration-prime": self.handle_declaration_prime_rule,
            "Var-declaration-prime": self.handle_var_declaration_prime_rule,
            "Fun-declaration-prime": self.handle_fun_declaration_prime_rule,
            "Type-specifier": self.handle_type_specifier_rule,
            "Params": self.handle_params_rule,
            "Param-list": self.handle_param_list_rule,
            "Param": self.handle_param_rule,
            "Param-prime": self.handle_param_prime_rule,
            "Compound-stmt": self.handle_compound_stmt_rule,
            "Statement-list": self.handle_statement_list_rule,
            "Statement": self.handle_statement_rule,
            "Expression-stmt": self.handle_expression_stmt_rule,
            "Selection-stmt": self.handle_selection_stmt_rule,
            "Iteration-stmt": self.handle_iteration_stmt_rule,
            "Return-stmt": self.handle_return_stmt_rule,
            "Return-stmt-prime": self.handle_return_stmt_prime_rule,
            "Expression": self.handle_expression_rule,
            "B": self.handle_b_rule,
            "H": self.handle_h_rule,
            "Simple-expression-zegond": self.handle_simple_expression_zegond_rule,
            "Simple-expression-prime": self.handle_simple_expression_prime_rule,
            "C": self.handle_c_rule,
            "Relop": self.handle_relop_rule,
            "Additive-expression": self.handle_additive_expression_rule,
            "Additive-expression-prime": self.handle_additive_expression_prime_rule,
            "Additive-expression-zegond": self.handle_additive_expression_zegond_rule,
            "D": self.handle_d_rule,
            "Addop": self.handle_addop_rule,
            "Term": self.handle_term_rule,
            "Term-prime": self.handle_term_prime_rule,
            "Term-zegond": self.handle_term_zegond_rule,
            "G": self.handle_g_rule,
            "Factor": self.handle_factor_rule,
            "Var-call-prime": self.handle_var_call_prime_rule,
            "Var-prime": self.handle_var_prime_rule,
            "Factor-prime": self.handle_factor_prime_rule,
            "Factor-zegond": self.handle_factor_zegond_rule,
            "Args": self.handle_args_rule,
            "Arg-list": self.handle_arg_list_rule,
            "Arg-list-prime": self.handle_arg_list_prime_rule,
        }

    def get_next_token(self):
        if self.current_index < len(self.tokens) - 1:
            self.current_index += 1
            self.current_token = self.tokens[self.current_index]
        else:
            self.current_token = (self.current_token[0], "EOF", "$")

    def match(self, expected_lexeme):
        if self.current_token[2] == expected_lexeme:
            self.add_to_parse_tree(f"({self.current_token[1]}, {self.current_token[2]})", is_terminal=True)
            self.get_next_token()
            return True
        else:
            self.record_syntax_error(f"Unexpected token '{self.current_token[2]}', expected '{expected_lexeme}'")
            return False

    def record_syntax_error(self, message):
        if not self.error_encountered or self.error_line != self.current_token[0]:
            self.error_line = self.current_token[0]
            if message == "Unexpected EOF":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, Unexpected EOF")
            elif message == "missing ID":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, illegal ID")
            elif message == "missing Params":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, missing Params")
            elif message == "missing (":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, missing (")
            elif message == "illegal {":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, illegal {{")
            elif message == "illegal return":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, illegal return")
            elif message == "illegal NUM":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, illegal NUM")
            elif message == "illegal }":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, illegal }}")
            elif message == "illegal else":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, illegal else")
            elif message == "illegal void":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, illegal void")
            elif message == "illegal (":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, illegal (")
            elif message == "illegal ;":
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, illegal ;")
            else:
                self.syntax_errors.append(f"#{self.current_token[0]} : syntax error, {message}")
            self.error_encountered = True
            if message in ["illegal {", "illegal int", "illegal ID", "illegal =", "illegal NUM", "illegal ;", "illegal }"]:
                self.get_next_token()
            else:
                self.panic_mode()

    def panic_mode(self):
        synchronization_tokens = [
            ";", "{", "}",
            "if", "repeat", "return", "int", "void",
            "$", "else", "until",
        ]
        while self.current_token[2] not in synchronization_tokens and self.current_token[2] != "$":
            self.get_next_token()
        if self.current_token[2] in [";", "}"]:
            self.get_next_token()
        self.error_encountered = False

    def add_to_parse_tree(self, node_name, is_terminal=False):
        if self.tree_depth == 0:
            self.parse_tree.append(node_name)
        else:
            indent = "│   " * (self.tree_depth - 1)
            prefix = "└── " if self.tree_depth > 0 else ""
            self.parse_tree.append(f"{indent}{prefix}{node_name}")
        if not is_terminal:
            self.tree_depth += 1

    def remove_from_parse_tree(self):
        self.tree_depth -= 1

    def apply_rule(self, rule_name, rule_logic_method):
        self.add_to_parse_tree(rule_name)
        rule_logic_method()
        self.remove_from_parse_tree()

    def add_epsilon(self):
        self.add_to_parse_tree("epsilon", is_terminal=True)

    def match_or_error(self, expected_lexemes, error_msg):
        if self.current_token[2] in expected_lexemes:
            self.match(self.current_token[2])
        else:
            self.record_syntax_error(error_msg)

    def match_id_or_error(self, error_msg):
        if self.current_token[1] == "ID":
            self.add_to_parse_tree(f"(ID, {self.current_token[2]})", is_terminal=True)
            self.get_next_token()
        else:
            self.record_syntax_error(error_msg)

    def parse_program(self):
        self.apply_rule("Program", self.handle_program)

    def handle_program(self):
        self.apply_rule("Declaration-list", self.handle_declaration_list_rule)

    def handle_declaration_list_rule(self):
        if self.current_token[2] in ["int", "void"]:
            self.apply_rule("Declaration", self.handle_declaration_rule)
            self.apply_rule("Declaration-list", self.handle_declaration_list_rule)
        else:
            self.add_epsilon()

    def handle_declaration_rule(self):
        self.apply_rule("Declaration-initial", self.handle_declaration_initial_rule)
        self.apply_rule("Declaration-prime", self.handle_declaration_prime_rule)

    def handle_declaration_initial_rule(self):
        self.apply_rule("Type-specifier", self.handle_type_specifier_rule)
        self.match_id_or_error("missing ID")

    def handle_declaration_prime_rule(self):
        if self.current_token[2] == "(":
            self.apply_rule("Fun-declaration-prime", self.handle_fun_declaration_prime_rule)
        elif self.current_token[2] in ["[", ";"]:
            self.apply_rule("Var-declaration-prime", self.handle_var_declaration_prime_rule)
        else:
            self.record_syntax_error("illegal {")

    def handle_var_declaration_prime_rule(self):
        if self.current_token[2] == "[":
            self.match("[")
            if self.current_token[1] == "NUM":
                self.match(self.current_token[2])
            else:
                self.record_syntax_error("Expected NUM in array declaration")
            self.match("]")
            self.match(";")
        elif self.current_token[2] == ";":
            self.match(";")
        else:
            self.record_syntax_error("Expected '[' or ';'")

    def handle_fun_declaration_prime_rule(self):
        self.match("(")
        if self.current_token[2] != ")":
            self.apply_rule("Params", self.handle_params_rule)
        else:
            self.record_syntax_error("missing Params")
        self.match(")")
        self.apply_rule("Compound-stmt", self.handle_compound_stmt_rule)

    def handle_type_specifier_rule(self):
        if self.current_token[2] == "int":
            self.match("int")
        elif self.current_token[2] == "void":
            self.match("void")
        else:
            self.record_syntax_error("illegal int")

    def handle_params_rule(self):
        if self.current_token[2] == "void":
            self.match("void")
        elif self.current_token[2] == "int":
            self.match("int")
            self.match_id_or_error("missing ID")
            self.apply_rule("Param-prime", self.handle_param_prime_rule)
            self.apply_rule("Param-list", self.handle_param_list_rule)
        else:
            self.record_syntax_error("Expected 'int' or 'void' for parameters")

    def handle_param_list_rule(self):
        if self.current_token[2] == ",":
            self.match(",")
            self.apply_rule("Param", self.handle_param_rule)
            self.apply_rule("Param-list", self.handle_param_list_rule)
        else:
            self.add_epsilon()

    def handle_param_rule(self):
        self.apply_rule("Declaration-initial", self.handle_declaration_initial_rule)
        self.apply_rule("Param-prime", self.handle_param_prime_rule)

    def handle_param_prime_rule(self):
        if self.current_token[2] == "[":
            self.match("[")
            self.match("]")
        else:
            self.add_epsilon()

    def handle_compound_stmt_rule(self):
        self.match("{")
        self.apply_rule("Declaration-list", self.handle_declaration_list_rule)
        self.apply_rule("Statement-list", self.handle_statement_list_rule)
        self.match("}")

    def handle_statement_list_rule(self):
        if self.current_token[2] in ["if", "repeat", "return", "break", ";", "{"] or \
           self.current_token[1] in ["ID", "NUM"] or \
           self.current_token[2] == "(":
            self.apply_rule("Statement", self.handle_statement_rule)
            self.apply_rule("Statement-list", self.handle_statement_list_rule)
        else:
            self.add_epsilon()

    def handle_statement_rule(self):
        if self.current_token[2] == "{":
            self.apply_rule("Compound-stmt", self.handle_compound_stmt_rule)
        elif self.current_token[2] == "if":
            self.apply_rule("Selection-stmt", self.handle_selection_stmt_rule)
        elif self.current_token[2] == "repeat":
            self.apply_rule("Iteration-stmt", self.handle_iteration_stmt_rule)
        elif self.current_token[2] == "return":
            self.apply_rule("Return-stmt", self.handle_return_stmt_rule)
        else:
            self.apply_rule("Expression-stmt", self.handle_expression_stmt_rule)

    def handle_expression_stmt_rule(self):
        if self.current_token[2] == "break":
            self.match("break")
            self.match(";")
        elif self.current_token[2] == ";":
            self.match(";")
        else:
            self.apply_rule("Expression", self.handle_expression_rule)
            self.match(";")

    def handle_selection_stmt_rule(self):
        self.match("if")
        self.match("(")
        self.apply_rule("Expression", self.handle_expression_rule)
        self.match(")")
        self.apply_rule("Statement", self.handle_statement_rule)
        if self.current_token[2] == "else":
            self.match("else")
            self.apply_rule("Statement", self.handle_statement_rule)

    def handle_iteration_stmt_rule(self):
        self.match("repeat")
        self.apply_rule("Statement", self.handle_statement_rule)
        self.match("until")
        self.match("(")
        self.apply_rule("Expression", self.handle_expression_rule)
        self.match(")")

    def handle_return_stmt_rule(self):
        self.match("return")
        self.apply_rule("Return-stmt-prime", self.handle_return_stmt_prime_rule)

    def handle_return_stmt_prime_rule(self):
        if self.current_token[2] == ";":
            self.match(";")
        else:
            self.apply_rule("Expression", self.handle_expression_rule)
            self.match(";")

    def handle_expression_rule(self):
        if self.current_token[1] == "ID":
            self.match_id_or_error("missing ID")
            self.apply_rule("B", self.handle_b_rule)
        else:
            self.apply_rule("Simple-expression-zegond", self.handle_simple_expression_zegond_rule)

    def handle_b_rule(self):
        if self.current_token[2] == "=":
            self.match("=")
            self.apply_rule("Expression", self.handle_expression_rule)
        elif self.current_token[2] == "[":
            self.match("[")
            self.apply_rule("Expression", self.handle_expression_rule)
            self.match("]")
            self.apply_rule("H", self.handle_h_rule)
        else:
            self.apply_rule("Simple-expression-prime", self.handle_simple_expression_prime_rule)

    def handle_h_rule(self):
        if self.current_token[2] == "=":
            self.match("=")
            self.apply_rule("Expression", self.handle_expression_rule)
        else:
            self.add_epsilon()

    def handle_simple_expression_zegond_rule(self):
        self.apply_rule("Additive-expression-zegond", self.handle_additive_expression_zegond_rule)
        self.apply_rule("C", self.handle_c_rule)

    def handle_simple_expression_prime_rule(self):
        self.apply_rule("Additive-expression-prime", self.handle_additive_expression_prime_rule)
        self.apply_rule("C", self.handle_c_rule)

    def handle_c_rule(self):
        if self.current_token[2] in ["<=", "==", "<"]:
            self.apply_rule("Relop", self.handle_relop_rule)
            self.apply_rule("Additive-expression", self.handle_additive_expression_rule)
        else:
            self.add_epsilon()

    def handle_relop_rule(self):
        if self.current_token[2] == "<=":
            self.match("<=")
        elif self.current_token[2] == "==":
            self.match("==")
        elif self.current_token[2] == "<":
            self.match("<")

    def handle_additive_expression_rule(self):
        self.apply_rule("Term", self.handle_term_rule)
        self.apply_rule("D", self.handle_d_rule)

    def handle_additive_expression_prime_rule(self):
        self.apply_rule("Term-prime", self.handle_term_prime_rule)
        self.apply_rule("D", self.handle_d_rule)

    def handle_additive_expression_zegond_rule(self):
        self.apply_rule("Term-zegond", self.handle_term_zegond_rule)
        self.apply_rule("D", self.handle_d_rule)

    def handle_d_rule(self):
        if self.current_token[2] in ["+", "-"]:
            self.apply_rule("Addop", self.handle_addop_rule)
            self.apply_rule("Term", self.handle_term_rule)
            self.apply_rule("D", self.handle_d_rule)
        else:
            self.add_epsilon()

    def handle_addop_rule(self):
        if self.current_token[2] == "+":
            self.match("+")
        elif self.current_token[2] == "-":
            self.match("-")

    def handle_term_rule(self):
        self.apply_rule("Factor", self.handle_factor_rule)
        self.apply_rule("G", self.handle_g_rule)

    def handle_term_prime_rule(self):
        self.apply_rule("Factor-prime", self.handle_factor_prime_rule)
        self.apply_rule("G", self.handle_g_rule)

    def handle_term_zegond_rule(self):
        self.apply_rule("Factor-zegond", self.handle_factor_zegond_rule)
        self.apply_rule("G", self.handle_g_rule)

    def handle_g_rule(self):
        if self.current_token[2] == "*":
            self.match("*")
            self.apply_rule("Factor", self.handle_factor_rule)
            self.apply_rule("G", self.handle_g_rule)
        else:
            self.add_epsilon()

    def handle_factor_rule(self):
        if self.current_token[2] == "(":
            self.match("(")
            self.apply_rule("Expression", self.handle_expression_rule)
            self.match(")")
        elif self.current_token[1] == "ID":
            self.match_id_or_error("missing ID")
            self.apply_rule("Var-call-prime", self.handle_var_call_prime_rule)
        elif self.current_token[1] == "NUM":
            self.match(self.current_token[2])
        else:
            self.record_syntax_error("Expected '(', ID, or NUM")

    def handle_var_call_prime_rule(self):
        if self.current_token[2] == "(":
            self.match("(")
            self.apply_rule("Args", self.handle_args_rule)
            self.match(")")
        else:
            self.apply_rule("Var-prime", self.handle_var_prime_rule)

    def handle_var_prime_rule(self):
        if self.current_token[2] == "[":
            self.match("[")
            self.apply_rule("Expression", self.handle_expression_rule)
            self.match("]")
        else:
            self.add_epsilon()

    def handle_factor_prime_rule(self):
        if self.current_token[2] == "(":
            self.match("(")
            self.apply_rule("Args", self.handle_args_rule)
            self.match(")")
        else:
            self.add_epsilon()

    def handle_factor_zegond_rule(self):
        if self.current_token[2] == "(":
            self.match("(")
            self.apply_rule("Expression", self.handle_expression_rule)
            self.match(")")
        elif self.current_token[1] == "NUM":
            self.match(self.current_token[2])
        else:
            self.record_syntax_error("Expected '(' or NUM")

    def handle_args_rule(self):
        if self.current_token[1] in ["ID", "NUM"] or self.current_token[2] == "(":
            self.apply_rule("Arg-list", self.handle_arg_list_rule)
        else:
            self.add_epsilon()

    def handle_arg_list_rule(self):
        self.apply_rule("Expression", self.handle_expression_rule)
        self.apply_rule("Arg-list-prime", self.handle_arg_list_prime_rule)

    def handle_arg_list_prime_rule(self):
        if self.current_token[2] == ",":
            self.match(",")
            self.apply_rule("Expression", self.handle_expression_rule)
            self.apply_rule("Arg-list-prime", self.handle_arg_list_prime_rule)
        else:
            self.add_epsilon()

    def write_outputs(self):
        # Write parse_tree.txt
        with open("parse_tree.txt", "w") as f:
            for line in self.parse_tree:
                f.write(line + "\n")

        # Write syntax_errors.txt
        with open("syntax_errors.txt", "w") as f:
            if not self.syntax_errors:
                f.write("There is no syntax error.\n")
            else:
                for error in self.syntax_errors:
                    f.write(error + "\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python parser.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    
    # Read tokens from input file
    tokens = []
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                # Parse the token line
                match = re.match(r'(\d+)\s+(\w+)\s+(.+)', line)
                if match:
                    line_num, token_type, lexeme = match.groups()
                    tokens.append((int(line_num), token_type, lexeme))

    # Add EOF token
    if tokens:
        last_line = tokens[-1][0]
        tokens.append((last_line + 1, "EOF", "$"))
    else:
        tokens.append((0, "EOF", "$"))

    # Create parser and parse the tokens
    parser = Parser(tokens)
    parser.parse_program()
    parser.write_outputs()

if __name__ == "__main__":
    main()
