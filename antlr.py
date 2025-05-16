import re


def normalize_tokens(token_text):
    """Normalize token formats to make them comparable."""
    # Removing line numbers 
    normalized = re.sub(r'^\d+\.\s*\t?', '', token_text, flags=re.MULTILINE)
    
    # Map ANTLR's tokens
    symbol_types = [
        'SEMI', 'COMMA', 'LBRACK', 'RBRACK', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'PLUS', 'MINUS', 'TIMES', 'DIV', 'ASSIGN', 'LESS', 'EQ'
    ]
    
    keyword_types = [
        'IF', 'ELSE', 'VOID', 'INT', 'REPEAT', 'BREAK', 'UNTIL', 'RETURN'
    ]
    
    # SYMBOL for all symbols
    for sym_type in symbol_types:
        normalized = re.sub(r'\(' + sym_type + r',\s*([^)]+)\)', r'(SYMBOL, \1)', normalized)
    
    # KEYWORD for all symbols
    for key_type in keyword_types:
        normalized = re.sub(r'\(' + key_type + r',\s*([^)]+)\)', r'(KEYWORD, \1)', normalized)
    
    # Normalizing whitespaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized 
