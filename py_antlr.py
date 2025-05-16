


import importlib.util  
import os
import re
import shutil
import subprocess
import sys  
import tempfile
from difflib import SequenceMatcher


ANTLR_DIR = "antlr"



GRAMMAR_TEMPLATE = r"""// Define this as a lexer grammar.
// Save this content in a file named "CMinus.g4"
lexer grammar CMinus;

// Keywords
// These are defined first so they take precedence over the ID rule.
IF: 'if';
ELSE: 'else';
VOID: 'void';
INT: 'int';
REPEAT: 'repeat';
BREAK: 'break';
UNTIL: 'until';
RETURN: 'return';

// Symbols
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

// Identifiers
// An identifier starts with a letter, followed by zero or more letters or digits.
ID: [a-zA-Z] [a-zA-Z0-9]*;

// Numbers
// A number is a sequence of one or more digits.
NUM: [0-9]+;

// Comments
// C-style block comments.
// The '-> skip' action tells ANTLR to find these tokens but not pass them on to the parser (or the token stream you'll inspect).
// This matches the project requirement that comments are not stored or reported in tokens.txt.
COMMENT: '/*' .*? '*/' -> skip;

// Whitespace
// Includes space, tab, carriage return, newline, vertical tab, and form feed.
// The '-> skip' action also applies here, as whitespace is generally ignored after tokenization.
WS: [ \t\r\n\u000B\u000C]+ -> skip; // \u000B is Vertical Tab, \u000C is Form Feed

// Note on Error Handling:
// ANTLR's default behavior for characters that do not match any rule is to create an error token.
// The specific error types mentioned in your project document, such as "Unmatched comment" for a standalone '*/'
// or "Invalid number" for a sequence like '123a', have a more nuanced handling in your custom scanner.
// For example, this ANTLR grammar would tokenize '123a' as NUM (123) followed by ID (a), and '*/' as TIMES (*) followed by DIV (/).
// Your 'Check()' function, when comparing your scanner's output to ANTLR's, should account for these differences,
// as ANTLR will primarily report a stream of validly formed tokens according to this grammar.
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
    """Run ANTLR to generate lexer from grammar file."""
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
                    
                    if '/Users/goldsmith/antlr-4.9.2-complete.jar' in ' '.join(antlr_cmd_base):
                        jar_path = '/Users/goldsmith/antlr-4.9.2-complete.jar'
                        if not os.path.exists(jar_path):
                            print(f"Error: ANTLR jar not found at {jar_path}")
                            print("Falling back to antlr4 command...")
                    
                    
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
            alternative_lexer_file = grammar_basename.replace('.g4', '') + ".py"
            
            if os.path.exists(expected_lexer_file):
                print(f"Found expected lexer file: {expected_lexer_file}")
                with open('__init__.py', 'w', encoding='utf-8') as f:
                    f.write("
                return True
            elif os.path.exists(alternative_lexer_file):
                print(f"Found alternative lexer file: {alternative_lexer_file}")
                if alternative_lexer_file != expected_lexer_file:
                    print(f"Renaming {alternative_lexer_file} to {expected_lexer_file}")
                    os.rename(alternative_lexer_file, expected_lexer_file)
                with open('__init__.py', 'w', encoding='utf-8') as f:
                    f.write("
                return True
            else:
                print(f"Error: ANTLR did not generate the lexer file ({expected_lexer_file}).")
                print(f"Please check ANTLR_DIR ('{os.getcwd()}') for generated files and ANTLR output above.")
                return False
        finally:
            os.chdir(original_dir)
    except subprocess.CalledProcessError as e:
        print(f"ANTLR command failed with exit code {e.returncode}.")
        print(f"Command: {' '.join(e.cmd)}")
        if e.stdout:
            print(f"Stdout:\n{e.stdout}")
        if e.stderr:
            print(f"Stderr:\n{e.stderr}")
        return False
    except Exception as e:
        print(f"ANTLR processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def tokenize_with_antlr(input_file):
    """Use ANTLR to tokenize an input file directly using the Python runtime."""
    ensure_antlr_dir()
    antlr_output_filepath = os.path.join(ANTLR_DIR, "ANTLR_p1")
    current_dir_output = "ANTLR_p1"
    
    try:
        from antlr4 import FileStream, Token
    except ImportError:
        print("Error: antlr4-python3-runtime package is not installed.")
        print("Please install it with: pip install antlr4-python3-runtime")
        return None

    grammar_name_from_file = "CMinus" 
    lexer_class_name = grammar_name_from_file + "Lexer"
    lexer_py_filename = lexer_class_name + ".py"
    lexer_py_file_path = os.path.join(ANTLR_DIR, lexer_py_filename)

    if not os.path.exists(lexer_py_file_path):
        print(f"Error: Lexer file '{lexer_py_file_path}' not found.")
        print("Ensure ANTLR has generated the lexer successfully by calling run_antlr() first.")
        return None

    with open(lexer_py_file_path, 'r', encoding='utf-8') as f:
        lexer_content = f.read()
        
    import re
    class_match = re.search(r'class\s+(\w+)', lexer_content)
    actual_class_name = class_match.group(1) if class_match else lexer_class_name
    
    print(f"Detected lexer class name: {actual_class_name} (expected: {lexer_class_name})")

    original_sys_path = list(sys.path)
    antlr_abs_dir_path = os.path.abspath(ANTLR_DIR)
    if antlr_abs_dir_path not in sys.path:
        sys.path.insert(0, antlr_abs_dir_path)

    ActualCMinusClass = None
    CMinusModule = None
    dynamic_module_name = f"dynamically_loaded_{lexer_class_name}"

    try:
        module_name = os.path.splitext(os.path.basename(lexer_py_filename))[0]
        print(f"Trying to import module: {module_name}")
        
        spec = importlib.util.spec_from_file_location(module_name, lexer_py_file_path)
        if spec is None:
            print(f"Error: Could not create spec for lexer module from {lexer_py_file_path}")
            return None
        
        CMinusModule = importlib.util.module_from_spec(spec)
        if CMinusModule is None:
            print(f"Error: Could not create module from spec for {lexer_py_file_path}")
            return None

        sys.modules[dynamic_module_name] = CMinusModule
        spec.loader.exec_module(CMinusModule)
        
        try:
            ActualCMinusClass = getattr(CMinusModule, actual_class_name)
            print(f"Successfully loaded {actual_class_name} class from module.")
        except AttributeError:
            print(f"Class {actual_class_name} not found in module. Available attributes:")
            for attr in dir(CMinusModule):
                if not attr.startswith('__'):
                    print(f"  - {attr}")
            
            for attr in dir(CMinusModule):
                if not attr.startswith('__') and attr.endswith('Lexer'):
                    ActualCMinusClass = getattr(CMinusModule, attr)
                    print(f"Found alternative lexer class: {attr}")
                    break

    except Exception as e:
        print(f"ANTLR dynamic lexer loading failed: {e}")
        import traceback
        traceback.print_exc()
        sys.path = original_sys_path
        if dynamic_module_name in sys.modules:
             del sys.modules[dynamic_module_name]
        return None 

    if ActualCMinusClass is None:
        print(f"Failed to get {lexer_class_name} class after attempting to load module.")
        sys.path = original_sys_path
        if dynamic_module_name in sys.modules: 
             del sys.modules[dynamic_module_name]
        return None

    try:
        input_stream = FileStream(input_file, encoding='utf-8')
        lexer = ActualCMinusClass(input_stream)
        
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
        print(f"Copied ANTLR output to current directory: {current_dir_output}")
        
        return antlr_output_filepath
    except Exception as e:
        print(f"ANTLR tokenization processing failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally: 
        sys.path = original_sys_path
        if dynamic_module_name in sys.modules:
             del sys.modules[dynamic_module_name]


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
        
        if similarity < 100:
            print(f"\n--- Our Tokens (Normalized) ---\n{our_tokens_normalized}")
            print(f"\n--- ANTLR Tokens (Normalized) ---\n{antlr_tokens_normalized}")

            with tempfile.NamedTemporaryFile(mode='w', delete=False, prefix=f"our_tokens_norm_{os.path.basename(tokens_file)}_", suffix=".txt", encoding='utf-8') as tf_our:
                tf_our.write(our_tokens_normalized)
                print(f"Our normalized tokens saved to: {tf_our.name}")
            with tempfile.NamedTemporaryFile(mode='w', delete=False, prefix=f"antlr_tokens_norm_{os.path.basename(antlr_file)}_", suffix=".txt", encoding='utf-8') as tf_antlr:
                tf_antlr.write(antlr_tokens_normalized)
                print(f"ANTLR normalized tokens saved to: {tf_antlr.name}")

        return similarity
    except FileNotFoundError as e:
        print(f"Error: One of the token files not found for comparison: {e}")
        return 0.0
    except Exception as e:
        print(f"Error comparing token files: {e}")
        import traceback
        traceback.print_exc()
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
    """Clean up ANTLR-generated files and the ANTLR directory if empty or fully."""
    if os.path.exists(ANTLR_DIR):
        try:
            shutil.rmtree(ANTLR_DIR)
            print(f"Removed ANTLR directory: {ANTLR_DIR}")
        except OSError as e: 
            print(f"Failed to remove directory {ANTLR_DIR}: {e}. Attempting to clean individual files.")
            clean_antlr_files() 
    
    if os.path.exists("ANTLR_p1"):
        try:
            os.remove("ANTLR_p1")
            print("Removed ANTLR_p1 from current directory")
        except Exception as e:
            print(f"Failed to remove ANTLR_p1 from current directory: {e}")

def clean_antlr_files():
    """Clean individual ANTLR-generated files from the ANTLR_DIR."""
    if not os.path.exists(ANTLR_DIR):
        return
        
    grammar_name = "CMinus" 
    files_to_remove = [
        f"{grammar_name}.g4",
        f"{grammar_name}Lexer.py",
        f"{grammar_name}Lexer.tokens",
        f"{grammar_name}.tokens",
        f"{grammar_name}.interp",
        f"{grammar_name}Lexer.interp",
        "__init__.py",
        "ANTLR_p1", 
    ]
    
    pycache_dir = os.path.join(ANTLR_DIR, "__pycache__")
    if os.path.exists(pycache_dir):
        try:
            shutil.rmtree(pycache_dir)
            print(f"Removed {pycache_dir}")
        except Exception as e:
            print(f"Failed to remove __pycache__ from {ANTLR_DIR}: {e}")

    for file_name in files_to_remove:
        file_path = os.path.join(ANTLR_DIR, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed ANTLR file: {file_path}")
            except Exception as e:
                print(f"Failed to remove {file_path}: {e}")
