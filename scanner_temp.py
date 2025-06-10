import os
import sys
from enum import Enum


# Remove loguru dependency and use basic logging instead
class Logger:
    def debug(self, msg):
        pass  # Remove debug logging for now
    def error(self, msg, exc_info=None):
        print(f"Error: {msg}")
    def warning(self, msg):
        print(f"Warning: {msg}")

logger = Logger()

class TokenType(Enum):
    KEYWORD = "KEYWORD"
    ID = "ID"
    NUM = "NUM"
    SYMBOL = "SYMBOL"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    EOF = "EOF"
    ERROR = "ERROR"

KEYWORDS = ["if", "else", "void", "int", "repeat", "break", "until", "return"]
SYMBOLS = [";", ",", "[", "]", "(", ")", "{", "}", "+", "-", "*", "<", "=", "/"]
MULTI_CHAR_SYMBOLS = ["==", "<=", ">=", "!="]
SPLIT_MULTI_CHAR_SYMBOLS = ["+="]

class CharacterScanner:
    def __init__(self, input_text):
        logger.debug("Initializing CharacterScanner")
        self.input_text = input_text
        self.position = 0
        self.line_num = 1
        self.column = 0
        self.tokens = []
        self.symbol_table = set(KEYWORDS)
        self.symbol_order = []
        self.lexical_errors = []
        self.current_char = input_text[0] if input_text else ''

    def advance(self):
        if self.current_char == '\n':
            self.line_num += 1
            self.column = 0
        else:
            self.column += 1
        self.position += 1
        self.current_char = self.input_text[self.position] if self.position < len(self.input_text) else ''

    def peek(self, distance=1):
        peek_pos = self.position + distance
        return self.input_text[peek_pos] if peek_pos < len(self.input_text) else ''

    def scan(self):
        while self.position < len(self.input_text):
            if self.current_char.isspace():
                self.skip_whitespace()
            elif self.current_char == '/' and self.peek() == '*':
                self.handle_multi_line_comment()
            elif self.current_char.isalpha():
                self.handle_identifier()
            elif self.current_char.isdigit():
                self.handle_number()
            elif self.check_split_multi_char_symbol():
                continue
            elif self.check_multi_char_symbol():
                continue
            elif self.check_invalid_symbol_sequence():
                continue
            elif self.current_char in SYMBOLS:
                if self.current_char == '/':
                    self.add_error("Invalid input", "/")
                    self.advance()
                else:
                    self.handle_symbol()
            else:
                self.add_error("Invalid input", self.current_char)
                self.advance()

    def skip_whitespace(self):
        while self.position < len(self.input_text) and self.current_char.isspace():
            self.advance()

    def handle_multi_line_comment(self):
        comment_start_line = self.line_num
        comment_text = "/*"
        self.advance()
        self.advance()
        comment_closed = False

        while self.position < len(self.input_text):
            if self.current_char == '*' and self.peek() == '/':
                self.advance()
                self.advance()
                comment_closed = True
                break
            comment_text += self.current_char
            self.advance()

        if not comment_closed:
            display_comment = comment_text[:10] + "..." if len(comment_text) > 10 else comment_text
            self.add_error("Unclosed comment", display_comment, comment_start_line)

    def handle_identifier(self):
        identifier = ""
        while self.position < len(self.input_text) and self.current_char.isalnum():
            identifier += self.current_char
            self.advance()

        if (self.position < len(self.input_text) and not self.current_char.isalnum()
                and not self.current_char.isspace() and self.current_char not in SYMBOLS
                and not self.check_match_multi_char_symbol(self.current_char + self.peek())
                and not self.check_match_split_multi_char_symbol(self.current_char + self.peek())):
            self.add_error("Invalid input", identifier + self.current_char)
            self.advance()
        else:
            if identifier in KEYWORDS:
                self.add_token(TokenType.KEYWORD, identifier)
            else:
                self.add_token(TokenType.ID, identifier)
                self.symbol_table.add(identifier)
                if identifier not in self.symbol_order and identifier not in KEYWORDS:
                    self.symbol_order.append(identifier)

    def handle_number(self):
        number = ""
        while self.position < len(self.input_text) and self.current_char.isdigit():
            number += self.current_char
            self.advance()

        if self.position < len(self.input_text) and self.current_char.isalpha():
            invalid_number = number
            while self.position < len(self.input_text) and self.current_char.isalnum():
                invalid_number += self.current_char
                self.advance()
            self.add_error("Invalid number", invalid_number)
        elif number:
            self.add_token(TokenType.NUM, number)

    def check_invalid_symbol_sequence(self):
        if self.current_char == '=' and self.peek() == '#':
            self.add_error("Invalid input", self.current_char + self.peek())
            self.advance()
            self.advance()
            return True
        return False

    def check_match_multi_char_symbol(self, sequence):
        return next((sym for sym in MULTI_CHAR_SYMBOLS if sequence.startswith(sym)), None)

    def check_match_split_multi_char_symbol(self, sequence):
        return next((sym for sym in SPLIT_MULTI_CHAR_SYMBOLS if sequence.startswith(sym)), None)

    def check_split_multi_char_symbol(self):
        combined = self.current_char + self.peek()
        if self.check_match_split_multi_char_symbol(combined) == "+=":
            self.add_token(TokenType.SYMBOL, "+")
            self.advance()
            self.add_token(TokenType.SYMBOL, "=")
            self.advance()
            return True
        return False

    def check_multi_char_symbol(self):
        combined = self.current_char + self.peek()
        symbol = self.check_match_multi_char_symbol(combined)
        if symbol:
            self.add_token(TokenType.SYMBOL, symbol)
            for _ in symbol:
                self.advance()
            return True
        return False

    def handle_symbol(self):
        if self.current_char == '*' and self.peek() == '/':
            self.add_error("Unmatched comment", "*/")
            self.advance()
            self.advance()
        elif self.current_char in SYMBOLS and self.current_char != '/':
            self.add_token(TokenType.SYMBOL, self.current_char)
            self.advance()

    def add_token(self, token_type, lexeme):
        if token_type != TokenType.WHITESPACE:
            self.tokens.append((self.line_num, token_type.value, lexeme))

    def add_error(self, error_type, lexeme, line=None):
        error_line = line if line else self.line_num
        self.lexical_errors.append((error_line, error_type, lexeme))

    def get_tokens_by_line(self):
        lines = {}
        for line_num, token_type, lexeme in self.tokens:
            lines.setdefault(line_num, []).append((token_type, lexeme))
        return lines

    def get_errors_by_line(self):
        lines = {}
        for line_num, error_type, lexeme in self.lexical_errors:
            lines.setdefault(line_num, []).append((error_type, lexeme))
        return lines

    def write_output_files(self):
        try:
            with open("tokens.txt", "w") as f:
                for line_num in sorted(self.get_tokens_by_line()):
                    tokens = self.get_tokens_by_line()[line_num]
                    tokens_str = " ".join(f"({t}, {l})" for t, l in tokens)
                    f.write(f"{line_num}.\t{tokens_str} \n")

            with open("lexical_errors.txt", "w") as f:
                errors = self.get_errors_by_line()
                if not errors:
                    f.write("There is no lexical error.")
                else:
                    for line_num in sorted(errors):
                        errors_str = " ".join(f"({l}, {e})" for e, l in errors[line_num])
                        f.write(f"{line_num}.\t{errors_str} \n")

            with open("symbol_table.txt", "w") as f:
                keyword_order = ["break", "else", "if", "int", "repeat", "return", "until", "void"]
                all_symbols = [kw for kw in keyword_order if kw in self.symbol_table] + self.symbol_order
                for idx, symbol in enumerate(all_symbols, 1):
                    f.write(f"{idx}.\t{symbol}\n")

        except Exception as e:
            logger.error(f"Error writing output files: {e}")
            raise


def scan_file(input_file):
    try:
        with open(input_file, "r") as f:
            input_text = f.read()

        for file in ["tokens.txt", "lexical_errors.txt", "symbol_table.txt"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    logger.warning(f"Could not remove file {file}: {e}")

        scanner = CharacterScanner(input_text)
        scanner.scan()
        scanner.write_output_files()
        return True

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return False
    except Exception as e:
        print(f"Error scanning file: {e}")
        return False


def clean_output_files():
    for file in ["tokens.txt", "lexical_errors.txt", "symbol_table.txt"]:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed {file}")
            except Exception as e:
                print(f"Failed to remove {file}: {e}")


def create_test_file():
    """Create a test input file for demonstration."""
    test_content = """/* Simple test program */
int main(void) {
    int x;
    x = 5 + 3;
    return x;
}
"""
    test_file = "test_input.txt"
    with open(test_file, "w") as f:
        f.write(test_content)
    return test_file 