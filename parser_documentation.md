Parser Documentation

The `Parser` class implements a recursive descent parser for a custom programming language, based on a manually defined context-free grammar. It accepts a list of lexical tokens and attempts to construct a parse tree while handling syntax errors.

---

Constructor
```python
Parser(tokens)
```
- **tokens**: A list of tokens (tuples of the form `(line_number, token_type, lexeme)`), typically produced by a lexical analyzer.

---

Attributes
- `tokens`: The list of tokens.
- `current_index`: Index of the current token being processed.
- `current_token`: The current token.
- `parse_tree`: A list representing the formatted parse tree.
- `syntax_errors`: A list collecting all syntax error messages.
- `tree_depth`: Tracks current depth for formatting the tree.
- `error_encountered`: Boolean flag to prevent multiple errors from same line.
- `error_line`: Line number of last recorded error.
- `grammar_rules`: Maps rule names to corresponding handler methods.

---

Core Parsing Methods
- `parse_program()`: Entry point for parsing. Starts parsing from the `Program` non-terminal.

---

Token Handling
- `get_next_token()`: Moves to the next token.
- `match(expected_lexeme)`: Matches current token with `expected_lexeme`, or logs a syntax error.

---

Error Handling
- `record_syntax_error(message)`: Logs a syntax error based on a message.
- `panic_mode()`: Skips tokens until a known synchronization token is found.

---

Parse Tree Construction
- `add_to_parse_tree(node_name, is_terminal=False)`: Adds a node to the parse tree.
- `remove_from_parse_tree()`: Moves back one level in the parse tree.
- `add_epsilon()`: Adds an epsilon node.

---

Grammar Rule Handling
Each grammar rule corresponds to a method prefixed by `handle_`. These methods implement specific productions of the grammar. Here are some key examples:

Declarations
- `handle_program()`
- `handle_declaration_list_rule()`
- `handle_declaration_rule()`
- `handle_declaration_initial_rule()`
- `handle_declaration_prime_rule()`

Types & Parameters
- `handle_type_specifier_rule()`
- `handle_params_rule()`
- `handle_param_list_rule()`
- `handle_param_rule()`
- `handle_param_prime_rule()`

Compound & Statements
- `handle_compound_stmt_rule()`
- `handle_statement_list_rule()`
- `handle_statement_rule()`
- `handle_expression_stmt_rule()`
- `handle_selection_stmt_rule()`
- `handle_iteration_stmt_rule()`
- `handle_return_stmt_rule()`
- `handle_return_stmt_prime_rule()`

Expressions
- `handle_expression_rule()`
- `handle_b_rule()`
- `handle_h_rule()`
- `handle_simple_expression_zegond_rule()`
- `handle_simple_expression_prime_rule()`
- `handle_c_rule()`
- `handle_relop_rule()`
- `handle_additive_expression_rule()`
- `handle_additive_expression_prime_rule()`
- `handle_additive_expression_zegond_rule()`
- `handle_d_rule()`
- `handle_addop_rule()`
- `handle_term_rule()`
- `handle_term_prime_rule()`
- `handle_term_zegond_rule()`
- `handle_g_rule()`
- `handle_factor_rule()`
- `handle_var_call_prime_rule()`
- `handle_var_prime_rule()`
- `handle_factor_prime_rule()`
- `handle_factor_zegond_rule()`
- `handle_args_rule()`
- `handle_arg_list_rule()`
- `handle_arg_list_prime_rule()`

---

Utility Methods
- `apply_rule(rule_name, rule_logic_method)`: Wraps parsing logic with tree formatting.
- `match_or_error(expected_lexemes, error_msg)`: Matches one of a set of lexemes or logs an error.
- `match_id_or_error(error_msg)`: Matches an ID or logs an error.

---

Output
- The class builds a structured `parse_tree` and a list of `syntax_errors`, which can be accessed or printed for analysis.

---

Notes
- This parser supports both predictive parsing and error recovery.
- Error recovery is handled through `panic_mode`, allowing parsing to continue after an error.
