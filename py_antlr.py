import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from difflib import SequenceMatcher

ANTLR_DIR = "antlr"

# Updated grammar with both lexer and parser rules (no endif required!)
    GRAMMAR_TEMPLATE = r"""
grammar CMinus;

// Parser rules
program: declaration_list;

declaration_list: declaration declaration_list | ;

declaration: declaration_initial declaration_prime;

declaration_initial: type_specifier ID;

declaration_prime: fun_declaration_prime | var_declaration_prime;

var_declaration_prime: ';' | '[' NUM ']' ';';

fun_declaration_prime: '(' params ')' compound_stmt;

type_specifier: INT | VOID;

params: INT ID param_prime param_list | VOID;

param_list: ',' param param_list | ;

param: declaration_initial param_prime;

param_prime: '[' ']' | ;

compound_stmt: '{' declaration_list statement_list '}';

statement_list: statement statement_list | ;

statement: expression_stmt | compound_stmt | selection_stmt | iteration_stmt | return_stmt;

expression_stmt: expression ';' | BREAK ';' | ';';

// Standard C-style if-else (no endif!)
selection_stmt: IF '(' expression ')' statement else_stmt;

else_stmt: | ELSE statement;

iteration_stmt: REPEAT statement UNTIL '(' expression ')' | WHILE '(' expression ')' statement;

return_stmt: RETURN return_stmt_prime;

return_stmt_prime: ';' | expression ';';

expression: simple_expression_zegond | ID b;

b: '=' expression | '[' expression ']' h | simple_expression_prime;

h: '=' expression | g d c;

simple_expression_zegond: additive_expression_zegond c;

simple_expression_prime: additive_expression_prime c;

c: relop additive_expression | ;

relop: '<' | '==';

additive_expression: term d;

additive_expression_prime: term_prime d;

additive_expression_zegond: term_zegond d;

d: addop term d | ;

addop: '+' | '-';

term: factor g;

term_prime: factor_prime g;

term_zegond: factor_zegond g;

g: '*' factor g | ;

factor: '(' expression ')' | ID var_call_prime | NUM;

var_call_prime: '(' args ')' | var_prime;

var_prime: '[' expression ']' | ;

factor_prime: '(' args ')' | ;

factor_zegond: '(' expression ')' | NUM;

args: arg_list | ;

arg_list: expression arg_list_prime;

arg_list_prime: ',' expression arg_list_prime | ;

// Lexer rules
IF: 'if';
ELSE: 'else';
VOID: 'void';
INT: 'int';
REPEAT: 'repeat';
WHILE: 'while';
BREAK: 'break';
UNTIL: 'until';
RETURN: 'return';

ASSIGN: '=';      // Assignment operator
EQ:     '==';     // Equality operator
LPAREN: '(';      // Left parenthesis
RPAREN: ')';      // Right parenthesis
LBRACE: '{';      // Left brace
RBRACE: '}';      // Right brace
LBRACK: '[';      // Left bracket
RBRACK: ']';      // Right bracket
SEMI:   ';';      // Semicolon
COMMA:  ',';      // Comma
PLUS:   '+';      // Plus operator
MINUS:  '-';      // Minus operator
TIMES:  '*';      // Multiplication operator
DIV:    '/';      // Division operator
LESS:   '<';      // Less than operator

ID: [a-zA-Z] [a-zA-Z0-9]*;

NUM: [0-9]+;

COMMENT: '/*' .*? '*/' -> skip;

WS: [ \t\r\n\u000B\u000C]+ -> skip;
"""

def ensure_antlr_dir():
    """Ensure the ANTLR directory exists."""
    if not os.path.exists(ANTLR_DIR):
        os.makedirs(ANTLR_DIR)
        print(f"Created directory: {ANTLR_DIR}")

def generate_antlr_grammar():
    """Generate ANTLR grammar file for C-minus language."""
    ensure_antlr_dir()
    grammar_file = os.path.join(ANTLR_DIR, "CMinus.g4")
    
    normalized_grammar = GRAMMAR_TEMPLATE.replace('\r\n', '\n').replace('\r', '\n')
    with open(grammar_file, "w", encoding='utf-8', newline='\n') as f:
        f.write(normalized_grammar)
    
    return grammar_file

def run_antlr(grammar_file):
    """Run ANTLR to generate lexer and parser from grammar file."""
    try:
        original_dir = os.getcwd()
        
        os.chdir(ANTLR_DIR)
        grammar_basename = os.path.basename(grammar_file) 
        
        try:
            goldsmith_jar_path = '/Users/goldsmith/antlr-4.9.2-complete.jar'
            antlr_jar_project_root = os.path.join('..', 'antlr-4.9.2-complete.jar')
            antlr_jar_antlr_dir = 'antlr-4.9.2-complete.jar'
            
            antlr_cmd_base = ['java', '-jar']
            antlr_tool_options = ['-Dlanguage=Python3', grammar_basename] 

            if os.path.exists(goldsmith_jar_path):
                antlr_cmd = antlr_cmd_base + [goldsmith_jar_path] + antlr_tool_options
                print(f"Using ANTLR jar from goldsmith path: {goldsmith_jar_path}")
            elif os.path.exists(antlr_jar_project_root):
                antlr_cmd = antlr_cmd_base + [antlr_jar_project_root] + antlr_tool_options
                print(f"Using ANTLR jar from project root: {os.path.abspath(antlr_jar_project_root)}")
            elif os.path.exists(antlr_jar_antlr_dir):
                antlr_cmd = antlr_cmd_base + [antlr_jar_antlr_dir] + antlr_tool_options
                print(f"Using ANTLR jar from ANTLR directory: {os.path.abspath(antlr_jar_antlr_dir)}")
            else:
                antlr_jar_env = os.environ.get('ANTLR_JAR', '')
                if antlr_jar_env and os.path.exists(antlr_jar_env):
                    antlr_cmd = antlr_cmd_base + [antlr_jar_env] + antlr_tool_options
                    print(f"Using ANTLR jar from environment variable: {antlr_jar_env}")
                else:
                    print("ANTLR jar not found, trying the antlr4 command...")
                    try:
                        antlr4_version_cmd = ['antlr4', '-version']
                        version_process = subprocess.run(antlr4_version_cmd, check=False, capture_output=True, text=True)
                        if version_process.returncode == 0:
                            print(f"Using antlr4 command: {version_process.stdout.strip()}")
                            antlr_cmd = ['antlr4'] + antlr_tool_options
                        else:
                            print("antlr4 command not found, trying python -m antlr4...")
                            antlr_cmd = [sys.executable, '-m', 'antlr4'] + antlr_tool_options
                    except Exception as e:
                        print(f"Error checking antlr4 command: {e}")
                        antlr_cmd = ['antlr4'] + antlr_tool_options  
            
            print(f"Running ANTLR command: {' '.join(antlr_cmd)} in directory {os.getcwd()}")
            process = subprocess.run(antlr_cmd, check=False, capture_output=True, text=True, encoding='utf-8')
            
            if process.stdout:
                print(f"ANTLR stdout:\n{process.stdout}")
            if process.stderr:
                print(f"ANTLR stderr:\n{process.stderr}")
            
            if process.returncode != 0:
                print(f"ANTLR command failed with exit code {process.returncode}")
                return False

            print("Files in ANTLR directory after running command:")
            for file in os.listdir('.'):
                print(f"  {file}")

            expected_lexer_file = grammar_basename.replace('.g4', '') + "Lexer.py"
            expected_parser_file = grammar_basename.replace('.g4', '') + "Parser.py"
            
            if os.path.exists(expected_lexer_file) and os.path.exists(expected_parser_file):
                print(f"Found lexer and parser files: {expected_lexer_file}, {expected_parser_file}")
                with open('__init__.py', 'w', encoding='utf-8') as f:
                    f.write("# ANTLR-generated package\n")
                return True
            else:
                print(f"Error: ANTLR did not generate expected files.")
                print(f"Expected: {expected_lexer_file}, {expected_parser_file}")
                return False
        finally:
            os.chdir(original_dir)
    except Exception as e:
        print(f"ANTLR processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def tokenize_with_antlr(input_file):
    """Use ANTLR to tokenize an input file."""
    ensure_antlr_dir()
    antlr_output_filepath = os.path.join(ANTLR_DIR, "ANTLR_p1")
    current_dir_output = "ANTLR_p1"
    
    try:
        from antlr4 import FileStream, Token
    except ImportError:
        print("Error: antlr4-python3-runtime package is not installed.")
        print("Please install it with: pip install antlr4-python3-runtime")
        return None

    # Import generated classes
    sys.path.insert(0, os.path.abspath(ANTLR_DIR))
    try:
        from CMinusLexer import CMinusLexer
        
        input_stream = FileStream(input_file, encoding='utf-8')
        lexer = CMinusLexer(input_stream)
        
        tokens = lexer.getAllTokens()

        with open(antlr_output_filepath, 'w', encoding='utf-8') as f:
            current_line = 1
            line_tokens = []
            
            for token in tokens:
                if token.channel == Token.HIDDEN_CHANNEL: 
                    continue
                if token.type == Token.EOF:
                    continue
                    
                token_line = token.line
                
                if token_line > current_line:
                    if line_tokens:
                        f.write(f"{current_line}.\t{' '.join(line_tokens)} \n")
                        line_tokens = []
                    
                    while current_line < token_line - 1: 
                        current_line += 1
                        f.write(f"{current_line}.\t\n")
                    
                    current_line = token_line
                
                if token.type >= 0 and token.type < len(lexer.symbolicNames):
                    token_type_name = lexer.symbolicNames[token.type]
                else:
                    token_type_name = f"TYPE_{token.type}" 

                token_text = token.text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                line_tokens.append(f"({token_type_name}, {token_text})")
            
            if line_tokens:
                f.write(f"{current_line}.\t{' '.join(line_tokens)} \n")
        
        shutil.copy(antlr_output_filepath, current_dir_output)
        print(f"Copied ANTLR tokens to: {current_dir_output}")
        
        return antlr_output_filepath
    except Exception as e:
        print(f"ANTLR tokenization failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        sys.path.remove(os.path.abspath(ANTLR_DIR))

def parse_with_antlr(input_file, output_tree_file="antlr_parse_tree.txt"):
    """Use ANTLR to parse an input file and generate parse tree."""
    ensure_antlr_dir()
    
    try:
        from antlr4 import CommonTokenStream, FileStream
        from antlr4.tree.Trees import Trees
    except ImportError:
        print("Error: antlr4-python3-runtime package is not installed.")
        print("Please install it with: pip install antlr4-python3-runtime")
        return None

    # Import generated classes
    sys.path.insert(0, os.path.abspath(ANTLR_DIR))
    try:
        from CMinusLexer import CMinusLexer
        from CMinusParser import CMinusParser
        
        input_stream = FileStream(input_file, encoding='utf-8')
        lexer = CMinusLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = CMinusParser(stream)
        
        # Parse starting from program rule
        tree = parser.program()
        
        # Generate string representation of parse tree
        tree_str = Trees.toStringTree(tree, None, parser)
        
        # Create a more readable tree format
        formatted_tree = format_parse_tree(tree_str)
        
        # Save to file
        tree_output_path = os.path.join(ANTLR_DIR, output_tree_file)
        with open(tree_output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_tree)
        
        # Copy to current directory
        current_dir_output = output_tree_file
        shutil.copy(tree_output_path, current_dir_output)
        print(f"Generated ANTLR parse tree: {current_dir_output}")
        
        return tree_output_path
    except Exception as e:
        print(f"ANTLR parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        sys.path.remove(os.path.abspath(ANTLR_DIR))

def format_parse_tree(tree_str):
    """Format the parse tree string for better readability."""
    # Add indentation based on nesting level
    formatted = ""
    indent_level = 0
    i = 0
    
    while i < len(tree_str):
        char = tree_str[i]
        
        if char == '(':
            formatted += "\n" + "  " * indent_level + char
            indent_level += 1
        elif char == ')':
            indent_level -= 1
            formatted += char
        elif char == ' ' and i > 0 and tree_str[i-1] == ')':
            # Space after closing paren - start new line
            formatted += "\n" + "  " * indent_level
        else:
            formatted += char
        
        i += 1
    
    return formatted.strip()

def run_full_antlr_analysis(input_file):
    """Run complete ANTLR analysis: generate grammar, compile, tokenize, and parse."""
    print("🔧 ANTLR ANALYSIS")
    print("-" * 40)
    
    # Generate grammar
    print("📝 Generating ANTLR grammar...")
    grammar_file = generate_antlr_grammar()
    
    # Compile grammar
    print("⚙️  Compiling ANTLR grammar...")
    if not run_antlr(grammar_file):
        print("❌ Failed to compile ANTLR grammar")
        return False
    
    # Tokenize
    print("🔍 Tokenizing with ANTLR...")
    token_output = tokenize_with_antlr(input_file)
    if not token_output:
        print("❌ Failed to tokenize with ANTLR")
        return False
    
    # Parse and generate tree
    print("🌳 Generating parse tree with ANTLR...")
    tree_output = parse_with_antlr(input_file)
    if not tree_output:
        print("❌ Failed to generate parse tree with ANTLR")
        return False
    
    print("\n✅ ANTLR analysis completed successfully!")
    print(f"📄 Tokens: ANTLR_p1")
    print(f"🌳 Parse tree: antlr_parse_tree.txt")
    
    return True

def compare_with_our_compiler(input_file):
    """Compare ANTLR output with our compiler output."""
    print("\n🔍 COMPARISON WITH OUR COMPILER")
    print("-" * 40)
    
    # Run our compiler first
    print("Running our compiler...")
    import subprocess
    result = subprocess.run([sys.executable, "compiler.py", input_file], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Our compiler failed")
        return
    
    # Compare tokens
    our_tokens_file = "output/tokens.txt"
    antlr_tokens_file = "ANTLR_p1"
    
    if os.path.exists(our_tokens_file) and os.path.exists(antlr_tokens_file):
        similarity = check(our_tokens_file, antlr_tokens_file)
        print(f"Token similarity: {similarity:.1f}%")
        if similarity > 95:
            print("✅ Tokenization matches very well!")
        elif similarity > 80:
            print("⚠️  Tokenization mostly matches")
        else:
            print("❌ Significant differences in tokenization")
    
    # Display parse trees
    our_tree_file = "output/parse_tree.txt"
    antlr_tree_file = "antlr_parse_tree.txt"
    
    if os.path.exists(our_tree_file) and os.path.exists(antlr_tree_file):
        print("\n📊 Parse tree comparison available:")
        print(f"   Our tree: {our_tree_file}")
        print(f"   ANTLR tree: {antlr_tree_file}")

# Keep the existing functions for backward compatibility
def check(tokens_file, antlr_file):
    """Compare the tokens from our scanner with ANTLR's output."""
    try:
        if not os.path.isabs(antlr_file) and not os.path.exists(antlr_file):
            antlr_file_in_dir = os.path.join(ANTLR_DIR, antlr_file)
            if os.path.exists(antlr_file_in_dir):
                antlr_file = antlr_file_in_dir
                print(f"Using ANTLR file at: {antlr_file}")
            
        with open(tokens_file, 'r', encoding='utf-8') as f:
            our_tokens = f.read()
        
        with open(antlr_file, 'r', encoding='utf-8') as f:
            antlr_tokens = f.read()
        
        our_tokens_normalized = normalize_tokens(our_tokens)
        antlr_tokens_normalized = normalize_tokens(antlr_tokens)
        
        similarity = SequenceMatcher(None, our_tokens_normalized, antlr_tokens_normalized).ratio() * 100
        
        return similarity
    except Exception as e:
        print(f"Error comparing token files: {e}")
        return 0.0

def normalize_tokens(token_text):
    """Normalize token formats to make them comparable."""
    normalized = re.sub(r'^\d+\.\s*\t?', '', token_text, flags=re.MULTILINE)
    
    symbol_types = [
        'SEMI', 'COMMA', 'LBRACK', 'RBRACK', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'PLUS', 'MINUS', 'TIMES', 'DIV', 'ASSIGN', 'LESS', 'EQ'
    ]
    
    keyword_types = [
        'IF', 'ELSE', 'VOID', 'INT', 'REPEAT', 'BREAK', 'UNTIL', 'RETURN'
    ]
    
    for sym_type in symbol_types:
        normalized = re.sub(r'\(' + sym_type + r',\s*([^)]+)\)', r'(SYMBOL, \1)', normalized)
    
    for key_type in keyword_types:
        normalized = re.sub(r'\(' + key_type + r',\s*([^)]+)\)', r'(KEYWORD, \1)', normalized)
    
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized

def clean_antlr_output():
    """Clean up ANTLR-generated files."""
    if os.path.exists(ANTLR_DIR):
        try:
            shutil.rmtree(ANTLR_DIR)
            print(f"Removed ANTLR directory: {ANTLR_DIR}")
        except OSError as e: 
            print(f"Failed to remove directory {ANTLR_DIR}: {e}")
    
    # Clean up output files in current directory
    output_files = ["ANTLR_p1", "antlr_parse_tree.txt"]
    for file in output_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed {file}")
            except Exception as e:
                print(f"Failed to remove {file}: {e}")

# Main execution for command line usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python py_antlr.py <input_file> [options]")
        print("Options:")
        print("  --tokens-only    Only generate tokens")
        print("  --tree-only      Only generate parse tree") 
        print("  --compare        Compare with our compiler")
        print("  --clean          Clean ANTLR files")
        sys.exit(1)
    
    if "--clean" in sys.argv:
        clean_antlr_output()
        sys.exit(0)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    if "--tokens-only" in sys.argv:
        grammar_file = generate_antlr_grammar()
        if run_antlr(grammar_file):
            tokenize_with_antlr(input_file)
    elif "--tree-only" in sys.argv:
        grammar_file = generate_antlr_grammar()
        if run_antlr(grammar_file):
            parse_with_antlr(input_file)
    else:
        # Full analysis
        run_full_antlr_analysis(input_file)
        
        if "--compare" in sys.argv:
            compare_with_our_compiler(input_file)
