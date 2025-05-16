#!/usr/bin/env python3
# C-minus Scanner Implementation - Rewritten

import os
import sys
from enum import Enum

from loguru import logger


# Token types
class TokenType(Enum):
    KEYWORD = "KEYWORD"
    ID = "ID"
    NUM = "NUM"
    SYMBOL = "SYMBOL"
    COMMENT = "COMMENT" # Although comments are skipped, defining it can be useful
    WHITESPACE = "WHITESPACE" # Although whitespace is skipped
    EOF = "EOF"
    ERROR = "ERROR"

# Keywords in C-minus
KEYWORDS = [
    "if", "else", "void", "int", "repeat",
    "break", "until", "return"
]

# Symbols in C-minus
# Note: Multi-character symbols are handled specifically
SYMBOLS = [
    ";", ",", "[", "]", "(", ")", "{", "}", "+",
    "-", "*", "<", "=", "/", # Note: '/' is technically a symbol but treated as error in this scanner
    # Multi-character symbols are handled separately
]

# Multi-character symbols (handled as single tokens if matched)
MULTI_CHAR_SYMBOLS = ["==", "<=", ">=", "!="]

# Special case multi-character sequence that is split into two symbols
SPLIT_MULTI_CHAR_SYMBOLS = ["+="]


class CharacterScanner:
    def __init__(self, input_text):
        logger.debug("Initializing CharacterScanner")
        self.input_text = input_text
        self.position = 0
        self.line_num = 1
        self.column = 0
        self.tokens = []
        # Add keywords to symbol table initially
        self.symbol_table = set(KEYWORDS)
        self.lexical_errors = []
        self.current_char = self.input_text[0] if len(self.input_text) > 0 else ''
        logger.debug(f"Scanner initialized: input_text length={len(input_text)}, initial char='{self.current_char}'")

    def advance(self):
        """Move to the next character in the input text."""
        old_pos = self.position
        old_line = self.line_num
        old_col = self.column
        consumed_char = self.current_char

        if self.current_char == '\n':
            self.line_num += 1
            self.column = 0
            logger.debug(f"ADVANCE: Consumed newline at pos {old_pos} (line {old_line}, col {old_col}) -> New line {self.line_num}, col {self.column}")
        else:
            self.column += 1
            logger.debug(f"ADVANCE: Consumed '{consumed_char}' at pos {old_pos} (line {old_line}, col {old_col}) -> New col {self.column}")

        self.position += 1
        if self.position < len(self.input_text):
            self.current_char = self.input_text[self.position]
            logger.debug(f"ADVANCE: Moved to pos {self.position}, new char='{self.current_char}'")
        else:
            self.current_char = ''
            logger.debug(f"ADVANCE: Reached EOF at pos {self.position}")

    def peek(self, distance=1):
        """Look ahead without consuming characters."""
        peek_pos = self.position + distance
        if peek_pos < len(self.input_text):
            peek_char = self.input_text[peek_pos]
            logger.debug(f"PEEK: Looking ahead {distance} steps from pos {self.position}, at pos {peek_pos}. Found '{peek_char}'")
            return peek_char
        logger.debug(f"PEEK: Looking ahead {distance} steps from pos {self.position}. Reached end of input.")
        return ''

    def scan(self):
        """Scan the input text and generate tokens."""
        logger.debug("Starting scanning process.")
        while self.position < len(self.input_text):
            logger.debug(f"SCAN loop: Current pos {self.position}, char='{self.current_char}', line {self.line_num}, col {self.column}")
            # Skip whitespace
            if self.current_char.isspace():
                logger.debug("SCAN: Found whitespace, skipping.")
                self.skip_whitespace()
                continue

            # Handle comments
            if self.current_char == '/' and self.peek() == '*':
                logger.debug("SCAN: Found start of multi-line comment '/*'.")
                self.handle_multi_line_comment()
                continue

            # Check for identifiers and keywords
            if self.current_char.isalpha():
                logger.debug("SCAN: Found start of identifier/keyword.")
                self.handle_identifier()
                continue

            # Check for numbers
            if self.current_char.isdigit():
                logger.debug("SCAN: Found start of number.")
                self.handle_number()
                continue

            # Check for special split multi-character symbols (like +=)
            if self.check_split_multi_char_symbol():
                continue

            # Check for regular multi-character symbols (like ==, <=, >=, !=)
            if self.check_multi_char_symbol():
                continue

            # Check for invalid multi-character sequences that need special reporting
            if self.check_invalid_symbol_sequence():
                continue

            # Check for single-character symbols
            if self.current_char in SYMBOLS: # Use SYMBOLS list for single chars
                 # Special handling for '/' as per the original code's behavior
                 if self.current_char == '/':
                     logger.debug(f"SCAN: Found '/', treating as invalid input.")
                     self.add_error("Invalid input", "/")
                     self.advance()
                 else:
                     logger.debug(f"SCAN: Found single-character symbol '{self.current_char}'.")
                     self.handle_symbol()
                 continue


            # If we get here, we have an invalid character
            logger.debug(f"SCAN: Found invalid character '{self.current_char}'.")
            self.add_error("Invalid input", self.current_char)
            self.advance()

        logger.debug("Scanning process finished.")
        # Add EOF token at the very end (optional, but good practice for parsers)
        # self.add_token(TokenType.EOF, "EOF") # Add EOF token if needed later

    def skip_whitespace(self):
        """Skip whitespace characters."""
        logger.debug("SKIP_WHITESPACE: Starting.")
        start_pos = self.position
        while self.position < len(self.input_text) and self.current_char.isspace():
            self.advance()
        logger.debug(f"SKIP_WHITESPACE: Finished, skipped from pos {start_pos} to {self.position}.")


    def handle_multi_line_comment(self):
        """Handle a /* ... */ comment."""
        logger.debug("HANDLE_MULTI_LINE_COMMENT: Starting.")
        comment_start_line = self.line_num
        comment_text = "/*"

        # Skip the opening /*
        self.advance()  # Skip /
        self.advance()  # Skip *

        # Search for the closing */
        comment_closed = False
        while self.position < len(self.input_text):
            if self.current_char == '*' and self.peek() == '/':
                self.advance()  # Skip *
                self.advance()  # Skip /
                comment_closed = True
                logger.debug("HANDLE_MULTI_LINE_COMMENT: Found closing '*/'.")
                break

            comment_text += self.current_char
            self.advance()

        if not comment_closed:
            # Unclosed comment error
            display_comment = comment_text[:10] + "..." if len(comment_text) > 10 else comment_text
            logger.debug(f"HANDLE_MULTI_LINE_COMMENT: Unclosed comment starting at line {comment_start_line}. Text: '{display_comment}'")
            self.add_error("Unclosed comment", display_comment, comment_start_line)
        else:
            logger.debug("HANDLE_MULTI_LINE_COMMENT: Successfully handled closed comment.")


    def handle_identifier(self):
        """Handle identifiers and keywords."""
        logger.debug("HANDLE_IDENTIFIER: Starting.")
        identifier_start_pos = self.position
        identifier = ""

        while (self.position < len(self.input_text) and
               self.current_char.isalnum()): # Allow digits in identifiers after the first char
            identifier += self.current_char
            self.advance()

        logger.debug(f"HANDLE_IDENTIFIER: Raw identifier collected: '{identifier}'")

        # Check if there's an invalid character immediately following a valid identifier
        # and it's not a symbol or whitespace that would terminate the identifier correctly.
        if (self.position < len(self.input_text) and
            not self.current_char.isalnum() and
            not self.current_char.isspace() and
            self.current_char not in SYMBOLS and
            self.check_match_multi_char_symbol(self.current_char + self.peek()) is None and # Check if it's the start of a multi-char symbol
            not self.check_match_split_multi_char_symbol(self.current_char + self.peek())): # Check if it's the start of a split multi-char symbol


            # Invalid input like "re%peat"
            invalid_input = identifier + self.current_char
            logger.debug(f"HANDLE_IDENTIFIER: Found invalid character immediately after identifier. Invalid input: '{invalid_input}'")
            self.add_error("Invalid input", invalid_input)
            self.advance() # Consume the invalid character
            # Note: The rest of the invalid sequence will be handled by the main scan loop or subsequent checks

        else:
            # Add token based on whether it's a keyword or identifier
            if identifier in KEYWORDS:
                logger.debug(f"HANDLE_IDENTIFIER: Identified as KEYWORD: '{identifier}'")
                self.add_token(TokenType.KEYWORD, identifier)
            elif identifier: # Ensure identifier is not empty (shouldn't happen with initial check)
                logger.debug(f"HANDLE_IDENTIFIER: Identified as ID: '{identifier}'")
                self.add_token(TokenType.ID, identifier)
                self.symbol_table.add(identifier)
            else:
                 logger.debug(f"HANDLE_IDENTIFIER: Identifier started but no characters were collected. Current char: '{self.current_char}'")


    def handle_number(self):
        """Handle numeric literals."""
        logger.debug("HANDLE_NUMBER: Starting.")
        number_start_pos = self.position
        number = ""

        # Collect all digits
        while self.position < len(self.input_text) and self.current_char.isdigit():
            number += self.current_char
            self.advance()

        logger.debug(f"HANDLE_NUMBER: Raw number collected: '{number}'")

        # Check for invalid number (with letters immediately after)
        if self.position < len(self.input_text) and self.current_char.isalpha():
            # Only report number + first letter as error
            invalid_number = number + self.current_char
            logger.debug(f"HANDLE_NUMBER: Found invalid character (letter) immediately after number. Invalid number: '{invalid_number}'")
            self.add_error("Invalid number", invalid_number)
            self.advance() # Consume the first letter

            # Extract the remaining part as a potential identifier
            remaining_id = ""
            while (self.position < len(self.input_text) and 
                  self.current_char.isalnum()):
                remaining_id += self.current_char
                self.advance()
            
            # If we extracted a valid identifier, add it to symbols
            if remaining_id:
                logger.debug(f"HANDLE_NUMBER: Extracted remaining identifier '{remaining_id}' after invalid number")
                # Add the remaining part as an identifier to symbol table
                self.add_token(TokenType.ID, remaining_id)
                self.symbol_table.add(remaining_id)
            
            logger.debug("HANDLE_NUMBER: Finished handling invalid number sequence.")
            return

        # Valid number
        if number: # Ensure number is not empty (shouldn't happen with initial check)
            logger.debug(f"HANDLE_NUMBER: Identified as NUM: '{number}'")
            self.add_token(TokenType.NUM, number)
        else:
            logger.debug(f"HANDLE_NUMBER: Number started but no digits were collected. Current char: '{self.current_char}'")


    def check_invalid_symbol_sequence(self):
        """Check for invalid sequences of symbols that should be reported together."""
        logger.debug("CHECK_INVALID_SYMBOL_SEQUENCE: Starting.")
        # Special case: =# as one error
        if self.current_char == '=' and self.peek() == '#':
            invalid_seq = self.current_char + self.peek()
            logger.debug(f"CHECK_INVALID_SYMBOL_SEQUENCE: Found invalid sequence '{invalid_seq}'.")
            self.add_error("Invalid input", invalid_seq)
            self.advance()  # consume '='
            self.advance()  # consume '#'
            logger.debug("CHECK_INVALID_SYMBOL_SEQUENCE: Consumed invalid sequence.")
            return True

        # Add more cases if needed for other specific symbol combinations
        # Example: handling "**" if it's invalid and needs specific reporting
        # if self.current_char == '*' and self.peek() == '*':
        #     invalid_seq = self.current_char + self.peek()
        #     logger.debug(f"CHECK_INVALID_SYMBOL_SEQUENCE: Found invalid sequence '{invalid_seq}'.")
        #     self.add_error("Invalid input", invalid_seq)
        #     self.advance() # consume first '*'
        #     self.advance() # consume second '*'
        #     logger.debug("CHECK_INVALID_SYMBOL_SEQUENCE: Consumed invalid sequence.")
        #     return True

        logger.debug("CHECK_INVALID_SYMBOL_SEQUENCE: No invalid sequences found at current position.")
        return False

    def check_match_multi_char_symbol(self, sequence):
        """Helper to check if a given sequence matches any multi-character symbol."""
        for symbol in MULTI_CHAR_SYMBOLS:
            if sequence.startswith(symbol):
                return symbol
        return None

    def check_match_split_multi_char_symbol(self, sequence):
        """Helper to check if a given sequence matches any split multi-character symbol."""
        for symbol in SPLIT_MULTI_CHAR_SYMBOLS:
            if sequence.startswith(symbol):
                return symbol
        return None


    def check_split_multi_char_symbol(self):
        """Check and handle multi-character symbols that should be split."""
        logger.debug("CHECK_SPLIT_MULTI_CHAR_SYMBOL: Starting.")
        current_and_next = self.current_char + self.peek()
        matched_symbol = self.check_match_split_multi_char_symbol(current_and_next)

        if matched_symbol:
            logger.debug(f"CHECK_SPLIT_MULTI_CHAR_SYMBOL: Matched split multi-character symbol '{matched_symbol}'.")
            # Handle += as two separate symbols
            # This assumes the split is always into the constituent parts
            if matched_symbol == "+=":
                self.add_token(TokenType.SYMBOL, "+")
                self.advance()
                self.add_token(TokenType.SYMBOL, "=")
                self.advance()
                logger.debug("CHECK_SPLIT_MULTI_CHAR_SYMBOL: Handled '+=' as two symbols.")
                return True

            # Add more split multi-char symbol cases here if needed
            # elif matched_symbol == "...":
            #     pass # handle similarly

        logger.debug("CHECK_SPLIT_MULTI_CHAR_SYMBOL: No split multi-character symbols found at current position.")
        return False


    def check_multi_char_symbol(self):
        """Check and handle multi-character symbols."""
        logger.debug("CHECK_MULTI_CHAR_SYMBOL: Starting.")
        current_and_next = self.current_char + self.peek()
        matched_symbol = self.check_match_multi_char_symbol(current_and_next)

        if matched_symbol:
            logger.debug(f"CHECK_MULTI_CHAR_SYMBOL: Matched multi-character symbol '{matched_symbol}'.")
            # Add the multi-character symbol as a single token
            self.add_token(TokenType.SYMBOL, matched_symbol)
            for _ in range(len(matched_symbol)):
                self.advance()
            logger.debug(f"CHECK_MULTI_CHAR_SYMBOL: Handled multi-character symbol '{matched_symbol}'.")
            return True

        logger.debug("CHECK_MULTI_CHAR_SYMBOL: No multi-character symbols found at current position.")
        return False


    def handle_symbol(self):
        """Handle single-character symbols from the SYMBOLS list."""
        logger.debug("HANDLE_SYMBOL: Starting.")

        # This check for */ might be redundant if handle_multi_line_comment is called first,
        # but keeping it as per original code's logic. It signifies an unmatched closing comment.
        if self.current_char == '*' and self.peek() == '/':
            logger.debug("HANDLE_SYMBOL: Found unmatched comment ending '*/'.")
            self.add_error("Unmatched comment", "*/")
            self.advance()  # Skip *
            self.advance()  # Skip /
            logger.debug("HANDLE_SYMBOL: Consumed unmatched comment ending.")
            return

        # Handling of '/' is explicitly done in the main scan loop
        # as per the original code's behavior of treating it as invalid.
        # If '/' should be a valid symbol, it would be handled here.
        # The current logic treats it as an "Invalid input" error in the main scan loop.

        # Handle other valid single symbol from the SYMBOLS list
        if self.current_char in SYMBOLS:
             # Exclude '/' since it's handled as error in scan loop
             if self.current_char != '/':
                logger.debug(f"HANDLE_SYMBOL: Found valid single-character symbol '{self.current_char}'.")
                self.add_token(TokenType.SYMBOL, self.current_char)
                self.advance()
                logger.debug(f"HANDLE_SYMBOL: Handled single-character symbol '{self.current_char}'.")
                return

        # If we reach here, it means a character was passed to handle_symbol
        # but it wasn't a recognised single symbol or the special */ case.
        # This indicates a potential logic error or an unexpected character
        # reached this point. The main scan loop should ideally catch this.
        # However, adding a debug log here for robustness.
        logger.debug(f"HANDLE_SYMBOL: Reached with character '{self.current_char}' not explicitly handled as a single symbol.")


    def add_token(self, token_type, lexeme):
        """Add a token to the tokens list."""
        logger.debug(f"ADD_TOKEN: Adding token (type={token_type.value}, lexeme='{lexeme}') at line {self.line_num}.")
        # The original code skips whitespace tokens, adhering to that.
        if token_type != TokenType.WHITESPACE:
            self.tokens.append((self.line_num, token_type.value, lexeme))
            logger.debug(f"ADD_TOKEN: Token added: ({self.line_num}, {token_type.value}, '{lexeme}')")

    def add_error(self, error_type, lexeme, line=None):
        """Add a lexical error to the errors list."""
        error_line = line if line is not None else self.line_num
        logger.debug(f"ADD_ERROR: Adding error (type='{error_type}', lexeme='{lexeme}') at line {error_line}.")
        self.lexical_errors.append((error_line, error_type, lexeme))
        logger.debug(f"ADD_ERROR: Error added: ({error_line}, '{error_type}', '{lexeme}')")

    def get_tokens_by_line(self):
        """Get tokens organized by line number."""
        logger.debug("GET_TOKENS_BY_LINE: Organizing tokens by line number.")
        tokens_by_line = {}
        for line_num, token_type, lexeme in self.tokens:
            if line_num not in tokens_by_line:
                tokens_by_line[line_num] = []
            tokens_by_line[line_num].append((token_type, lexeme))
        logger.debug(f"GET_TOKENS_BY_LINE: Organized {len(self.tokens)} tokens into {len(tokens_by_line)} lines.")
        return tokens_by_line

    def get_errors_by_line(self):
        """Get lexical errors organized by line number."""
        logger.debug("GET_ERRORS_BY_LINE: Organizing errors by line number.")
        errors_by_line = {}
        for line_num, error_type, lexeme in self.lexical_errors:
            if line_num not in errors_by_line:
                errors_by_line[line_num] = []
            errors_by_line[line_num].append((error_type, lexeme))
        logger.debug(f"GET_ERRORS_BY_LINE: Organized {len(self.lexical_errors)} errors into {len(errors_by_line)} lines.")
        return errors_by_line

    def write_output_files(self):
        """Write tokens, lexical errors, and symbol table to output files."""
        logger.debug("WRITE_OUTPUT_FILES: Starting.")
        try:
            # Write tokens to file
            logger.debug("WRITE_OUTPUT_FILES: Writing tokens.txt.")
            with open("tokens.txt", "w") as f:
                tokens_by_line = self.get_tokens_by_line()
                for line_num in sorted(tokens_by_line.keys()):
                    tokens_str = " ".join(f"({token_type}, {lexeme})" for token_type, lexeme in tokens_by_line[line_num])
                    f.write(f"{line_num}.\t{tokens_str} \n")
            logger.debug("WRITE_OUTPUT_FILES: Finished writing tokens.txt.")

            # Write lexical errors to file
            logger.debug("WRITE_OUTPUT_FILES: Writing lexical_errors.txt.")
            with open("lexical_errors.txt", "w") as f:
                errors_by_line = self.get_errors_by_line()
                if not errors_by_line:
                    f.write("There is no lexical error.")
                    logger.debug("WRITE_OUTPUT_FILES: No lexical errors found, writing default message.")
                else:
                    for line_num in sorted(errors_by_line.keys()):
                        errors_str = " ".join(f"({lexeme}, {error_type})" for error_type, lexeme in errors_by_line[line_num])
                        f.write(f"{line_num}.\t{errors_str} \n")
                    logger.debug(f"WRITE_OUTPUT_FILES: Finished writing {len(self.lexical_errors)} errors to lexical_errors.txt.")


            # Write symbol table to file
            logger.debug("WRITE_OUTPUT_FILES: Writing symbol_table.txt.")
            with open("symbol_table.txt", "w") as f:
                # Sort keywords first, then identifiers
                all_symbols = []

                # Add keywords in fixed order as specified
                keyword_list_order = ["break", "else", "if", "int", "repeat", "return", "until", "void"]
                all_symbols.extend([kw for kw in keyword_list_order if kw in self.symbol_table])

                # Add other identifiers in alphabetical order
                non_keywords = sorted(symbol for symbol in self.symbol_table if symbol not in keyword_list_order)
                all_symbols.extend(non_keywords)

                # Output all symbols
                for i, symbol in enumerate(all_symbols, 1):
                    f.write(f"{i}.\t{symbol}\n")
                logger.debug(f"WRITE_OUTPUT_FILES: Finished writing {len(all_symbols)} symbols to symbol_table.txt.")

        except Exception as e:
            logger.error(f"WRITE_OUTPUT_FILES: Error writing output files: {e}", exc_info=True)
            raise # Re-raise the exception after logging


def scan_file(input_file):
    """Scan a file and generate tokens, errors, and symbol table."""
    logger.debug(f"SCAN_FILE: Starting scan for file '{input_file}'.")
    try:
        with open(input_file, "r") as f:
            input_text = f.read()
        logger.debug(f"SCAN_FILE: Successfully read input file '{input_file}'. Content length: {len(input_text)}")

        # Clear previous results
        files_to_clean = ["tokens.txt", "lexical_errors.txt", "symbol_table.txt"]
        logger.debug(f"SCAN_FILE: Cleaning up previous output files: {files_to_clean}")
        for file in files_to_clean:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    logger.debug(f"SCAN_FILE: Removed existing file '{file}'.")
                except Exception as e:
                     logger.warning(f"SCAN_FILE: Could not remove existing file '{file}': {e}")


        scanner = CharacterScanner(input_text)
        scanner.scan()
        scanner.write_output_files()

        logger.debug(f"SCAN_FILE: Scanning and writing output complete for '{input_file}'.")
        return True
    except FileNotFoundError:
        logger.error(f"SCAN_FILE: Input file '{input_file}' not found.")
        print(f"Error: Input file '{input_file}' not found.")
        return False
    except Exception as e:
        logger.error(f"SCAN_FILE: Error during scanning of file '{input_file}': {e}", exc_info=True)
        print(f"Error scanning file: {e}")
        # import traceback # Already imported if needed for print_exc
        # traceback.print_exc() # Loguru's exc_info=True handles this
        return False

def clean_output_files():
    """Clean up output files from previous runs."""
    logger.debug("CLEAN_OUTPUT_FILES: Starting cleanup.")
    files_to_clean = ["tokens.txt", "lexical_errors.txt", "symbol_table.txt"]

    for file in files_to_clean:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed {file}")
                logger.debug(f"CLEAN_OUTPUT_FILES: Removed {file}.")
            except Exception as e:
                print(f"Failed to remove {file}: {e}")
                logger.error(f"CLEAN_OUTPUT_FILES: Failed to remove {file}: {e}", exc_info=True)
        else:
            logger.debug(f"CLEAN_OUTPUT_FILES: File {file} does not exist, skipping removal.")
    logger.debug("CLEAN_OUTPUT_FILES: Cleanup finished.")
