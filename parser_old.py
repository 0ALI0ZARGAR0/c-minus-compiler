import re
import sys


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
        
        # First and Follow sets (based on reference implementation)
        self.first_sets = {
            "Program": {"$", "void", "int"},
            "Declaration-list": {"", "void", "int"},
            "Declaration": {"void", "int"},
            "Declaration-initial": {"void", "int"},
            "Declaration-prime": {"(", ";", "["},
            "Var-declaration-prime": {";", "["},
            "Fun-declaration-prime": {"("},
            "Type-specifier": {"void", "int"},
            "Params": {"int", "void"},
            "Param-list": {"", ","},
            "Param": {"void", "int"},
            "Param-prime": {"[", ""},
            "Compound-stmt": {"{"},
            "Statement-list": {"", "{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM"},
            "Statement": {"{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM"},
            "Expression-stmt": {";", "break", "ID", "(", "NUM"},
            "Selection-stmt": {"if"},
            "Iteration-stmt": {"repeat"},
            "Return-stmt": {"return"},
            "Return-stmt-prime": {";", "ID", "(", "NUM"},
            "Expression": {"ID", "(", "NUM"},
            "B": {"[", "=", "(", "*", "+", "-", "<", "<=", "==", ""},
            "H": {"=", "*", "", "+", "-", "<", "<=", "=="},
            "Simple-expression-zegond": {"(", "NUM"},
            "Simple-expression-prime": {"(", "*", "+", "-", "<", "<=", "==", ""},
            "C": {"", "<", "<=", "=="},
            "Relop": {"<", "==", "<="},
            "Additive-expression": {"(", "ID", "NUM"},
            "Additive-expression-prime": {"(", "*", "+", "-", ""},
            "Additive-expression-zegond": {"(", "NUM"},
            "D": {"", "+", "-"},
            "Addop": {"+", "-"},
            "Term": {"(", "ID", "NUM"},
            "Term-prime": {"(", "*", ""},
            "Term-zegond": {"(", "NUM"},
            "G": {"*", ""},
            "Factor": {"(", "ID", "NUM"},
            "Var-call-prime": {"(", "[", ""},
            "Var-prime": {"[", ""},
            "Factor-prime": {"(", ""},
            "Factor-zegond": {"(", "NUM"},
            "Args": {"", "ID", "(", "NUM"},
            "Arg-list": {"ID", "(", "NUM"},
            "Arg-list-prime": {"", ","},
        }
        
        self.follow_sets = {
            "Program": {""},
            "Declaration-list": {"$", "{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}"},
            "Declaration": {"void", "int", "$", "{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}"},
            "Declaration-initial": {"(", ";", "[", ",", ")"},
            "Declaration-prime": {"void", "int", "$", "{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}"},
            "Var-declaration-prime": {"void", "int", "$", "{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}"},
            "Fun-declaration-prime": {"void", "int", "$", "{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}"},
            "Type-specifier": {"ID"},
            "Params": {")"},
            "Param-list": {")"},
            "Param": {",", ")"},
            "Param-prime": {",", ")"},
            "Compound-stmt": {"void", "int", "$", "{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}", "else", "endif", "until"},
            "Statement-list": {"}"},
            "Statement": {"{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}", "else", "endif", "until"},
            "Expression-stmt": {"{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}", "else", "endif", "until"},
            "Selection-stmt": {"{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}", "else", "endif", "until"},
            "Iteration-stmt": {"{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}", "else", "endif", "until"},
            "Return-stmt": {"{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}", "else", "endif", "until"},
            "Return-stmt-prime": {"{", ";", "break", "if", "repeat", "return", "ID", "(", "NUM", "}", "else", "endif", "until"},
            "Expression": {";", ")", "]", ","},
            "B": {";", ")", "]", ","},
            "H": {";", ")", "]", ","},
            "Simple-expression-zegond": {";", ")", "]", ","},
            "Simple-expression-prime": {";", ")", "]", ","},
            "C": {";", ")", "]", ","},
            "Relop": {"(", "ID", "NUM"},
            "Additive-expression": {";", ")", "]", ","},
            "Additive-expression-prime": {"<", "<=", "==", ";", ")", "]", ","},
            "Additive-expression-zegond": {"<", "<=", "==", ";", ")", "]", ","},
            "D": {"<", "<=", "==", ";", ")", "]", ","},
            "Addop": {"(", "ID", "NUM"},
            "Term": {"+", "-", ";", ")", "<", "<=", "==", "]", ","},
            "Term-prime": {"+", "-", "<", "<=", "==", ";", ")", "]", ","},
            "Term-zegond": {"+", "-", "<", "<=", "==", ";", ")", "]", ","},
            "G": {"+", "-", "<", "<=", "==", ";", ")", "]", ","},
            "Factor": {"*", "+", "-", ";", ")", "<", "<=", "==", "]", ","},
            "Var-call-prime": {"*", "+", "-", ";", ")", "<", "<=", "==", "]", ","},
            "Var-prime": {"*", "+", "-", ";", ")", "<", "<=", "==", "]", ","},
            "Factor-prime": {"*", "+", "-", "<", "<=", "==", ";", ")", "]", ","},
            "Factor-zegond": {"*", "+", "-", "<", "<=", "==", ";", ")", "]", ","},
            "Args": {")"},
            "Arg-list": {")"},
            "Arg-list-prime": {")"},
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
            self.record_syntax_error(f"missing {expected_lexeme}")
            return False

    def can_derive_epsilon(self, non_terminal):
        """Check if a non-terminal can derive epsilon using first sets"""
        return "" in self.first_sets.get(non_terminal, set())

    def should_apply_rule(self, non_terminal, token):
        """Determine if we should apply a rule based on first/follow sets"""
        first_set = self.first_sets.get(non_terminal, set())
        follow_set = self.follow_sets.get(non_terminal, set())
        
        # Direct match in first set
        if token in first_set:
            return True
        
        # Epsilon production: check if token is in follow set
        if self.can_derive_epsilon(non_terminal) and token in follow_set:
            return True
            
        return False

    def record_syntax_error(self, message):
        """Improved error handling based on reference implementation"""
        if not self.error_encountered or self.error_line != self.current_token[0]:
            self.error_line = self.current_token[0]
            
            # More specific error messages based on reference
            if self.current_token[2] == "$":
                error_msg = f"#{self.current_token[0]} : syntax error, Unexpected EOF"
            elif message.startswith("missing"):
                missing_token = message.replace("missing ", "")
                error_msg = f"#{self.current_token[0]} : syntax error, missing {missing_token}"
            elif "illegal" in message:
                error_msg = f"#{self.current_token[0]} : syntax error, illegal {self.current_token[2]}"
            else:
                error_msg = f"#{self.current_token[0]} : syntax error, {message}"
                
            self.syntax_errors.append(error_msg)
            self.error_encountered = True
            
            # Skip token for certain error types
            if any(word in message for word in ["illegal", "unexpected"]):
                self.get_next_token()
                return True
            else:
                self.panic_mode()
                return False

    def panic_mode(self):
        """Enhanced panic mode recovery"""
        synchronization_tokens = [
            ";", "{", "}", "if", "repeat", "return", "int", "void",
            "$", "else", "until", "endif"
        ]
        
        while (self.current_token[2] not in synchronization_tokens and 
               self.current_token[2] != "$"):
            self.get_next_token()
            
        # Skip semicolons and closing braces to continue parsing
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

    def match_id_or_error(self, error_msg):
        if self.current_token[1] == "ID":
            self.add_to_parse_tree(f"(ID, {self.current_token[2]})", is_terminal=True)
            self.get_next_token()
        else:
            self.record_syntax_error(error_msg)

    def match_num_or_error(self, error_msg):
        if self.current_token[1] == "NUM":
            self.add_to_parse_tree(f"(NUM, {self.current_token[2]})", is_terminal=True)
            self.get_next_token()
        else:
            self.record_syntax_error(error_msg)

    def parse_program(self):
        self.apply_rule("Program", self.handle_program)

    def handle_program(self):
        self.apply_rule("Declaration-list", self.handle_declaration_list_rule)

    def handle_declaration_list_rule(self):
        if self.should_apply_rule("Declaration", self.current_token[2]):
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
            self.record_syntax_error(f"illegal {self.current_token[2]}")

    def handle_var_declaration_prime_rule(self):
        if self.current_token[2] == "[":
            self.match("[")
            self.match_num_or_error("missing NUM")
            self.match("]")
            self.match(";")
        elif self.current_token[2] == ";":
            self.match(";")
        else:
            self.record_syntax_error("Expected '[' or ';'")

    def handle_fun_declaration_prime_rule(self):
        self.match("(")
        self.apply_rule("Params", self.handle_params_rule)
        self.match(")")
        self.apply_rule("Compound-stmt", self.handle_compound_stmt_rule)

    def handle_type_specifier_rule(self):
        if self.current_token[2] == "int":
            self.match("int")
        elif self.current_token[2] == "void":
            self.match("void")
        else:
            self.record_syntax_error("illegal type specifier")

    def handle_params_rule(self):
        if self.current_token[2] == "void":
            # Check if this is a void parameter list (void followed by ))
            if self.current_index + 1 < len(self.tokens) and self.tokens[self.current_index + 1][2] == ")":
                self.match("void")
            else:
                # This is a void type parameter
                self.match("void")
                self.match_id_or_error("missing ID")
                self.apply_rule("Param-prime", self.handle_param_prime_rule)
                self.apply_rule("Param-list", self.handle_param_list_rule)
        elif self.current_token[2] == "int":
            self.match("int")
            self.match_id_or_error("missing ID")
            self.apply_rule("Param-prime", self.handle_param_prime_rule)
            self.apply_rule("Param-list", self.handle_param_list_rule)
        else:
            # Empty parameter list is handled by epsilon production
            self.add_epsilon()

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
        # Check if current token can start a statement
        current_token = self.current_token[2]
        current_type = self.current_token[1]
        
        if (current_token in ["{", "if", "repeat", "return", "break", ";"] or 
            current_type in ["ID", "NUM"] or current_token == "("):
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
            # H -> G D C (handle arithmetic operations after array access)
            self.apply_rule("G", self.handle_g_rule)
            self.apply_rule("D", self.handle_d_rule)
            self.apply_rule("C", self.handle_c_rule)

    def handle_simple_expression_zegond_rule(self):
        self.apply_rule("Additive-expression-zegond", self.handle_additive_expression_zegond_rule)
        self.apply_rule("C", self.handle_c_rule)

    def handle_simple_expression_prime_rule(self):
        self.apply_rule("Additive-expression-prime", self.handle_additive_expression_prime_rule)
        self.apply_rule("C", self.handle_c_rule)

    def handle_c_rule(self):
        if self.current_token[2] in ["<", "<=", "=="]:
            self.apply_rule("Relop", self.handle_relop_rule)
            self.apply_rule("Additive-expression", self.handle_additive_expression_rule)
        else:
            self.add_epsilon()

    def handle_relop_rule(self):
        if self.current_token[2] in ["<", "<=", "=="]:
            self.match(self.current_token[2])
        else:
            self.record_syntax_error("Expected relational operator")

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
        if self.current_token[2] in ["+", "-"]:
            self.match(self.current_token[2])
        else:
            self.record_syntax_error("Expected '+' or '-'")

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
            self.match_num_or_error("missing NUM")
        else:
            self.record_syntax_error(f"illegal {self.current_token[2]}")

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
            self.match_num_or_error("missing NUM")
        else:
            self.record_syntax_error(f"illegal {self.current_token[2]}")

    def handle_args_rule(self):
        if self.should_apply_rule("Arg-list", self.current_token[2]):
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
                # Parse the token line - improved regex to handle edge cases
                match = re.match(r'(\d+)\s+(\w+)\s+(.+)', line)
                if match:
                    line_num, token_type, lexeme = match.groups()
                    tokens.append((int(line_num), token_type, lexeme))

    # Add EOF token
    if tokens:
        last_line = tokens[-1][0]
        tokens.append((last_line + 1, "EOF", "$"))
    else:
        tokens.append((1, "EOF", "$"))

    # Create parser and parse the tokens
    parser = Parser(tokens)
    parser.parse_program()
    parser.write_outputs()

if __name__ == "__main__":
    main()
