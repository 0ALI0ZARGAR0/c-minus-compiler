import re


def normalize_tokens(token_text):
    """Normalize token formats to make them comparable."""
    # First remove line numbers 
    normalized = re.sub(r'^\d+\.\s*\t?', '', token_text, flags=re.MULTILINE)
    
    # Map ANTLR's specific token types to more generic types to match the scanner output
    symbol_types = [
        'SEMI', 'COMMA', 'LBRACK', 'RBRACK', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'PLUS', 'MINUS', 'TIMES', 'DIV', 'ASSIGN', 'LESS', 'EQ'
    ]
    
    keyword_types = [
        'IF', 'ELSE', 'VOID', 'INT', 'REPEAT', 'BREAK', 'UNTIL', 'RETURN'
    ]
    
    # Replace all symbol types with SYMBOL
    for sym_type in symbol_types:
        normalized = re.sub(r'\(' + sym_type + r',\s*([^)]+)\)', r'(SYMBOL, \1)', normalized)
    
    # Replace all keyword types with KEYWORD
    for key_type in keyword_types:
        normalized = re.sub(r'\(' + key_type + r',\s*([^)]+)\)', r'(KEYWORD, \1)', normalized)
    
    # Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized 