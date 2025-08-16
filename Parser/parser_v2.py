from SemanticLevel.CodeGen import CodeGen


class ParserV2:
    def __init__(self, codegen: CodeGen):
        self.codegen = codegen
        self.action_symbols = codegen.routines  # Direct mapping

    def is_action_symbol(self, symbol):
        return symbol in self.action_symbols

    def parse(self, grammar_rule, token_stream):
        # Example skeleton: grammar_rule is a list of symbols (terminals, non-terminals, or action symbols)
        for symbol in grammar_rule:
            if self.is_action_symbol(symbol):
                # Call the corresponding CodeGen routine
                self.action_symbols[symbol](self.current_token())
            else:
                # Handle terminal/non-terminal (to be implemented)
                pass

    def current_token(self):
        # Stub: return the current token (to be implemented)
        return None

# Usage example (integration):
# codegen = CodeGen()
# parser = ParserV2(codegen)
# parser.parse(['ID', '#assign', ';'], token_stream)
