#!/usr/bin/env python3
# ANTLR integration for C-minus Scanner

import importlib.util  # Added for dynamic module loading
import os
import re
import shutil
import subprocess
import sys  # Added for sys.path manipulation and sys.executable
import tempfile
from difflib import SequenceMatcher

# Define ANTLR directory
ANTLR_DIR = "antlr"

# ANTLR grammar template for C-minus lexer
# (Corrected version)
GRAMMAR_TEMPLATE = r"""// Define this as a lexer grammar.
// Save this content in a file named "CMinus.g4"
lexer grammar CMinus;

// Comments
COMMENT : '/*' .*? '*/' -> skip;

INVALID_TOKEN: [0-9]+[a-zA-Z] -> skip;

// Numbers
NUM : [0-9]+;

// Keywords
KEYWORD : 'void' | 'int' | 'if' | 'else' | 'repeat' | 'break' | 'until' | 'return';

// Identifiers
INVALID_ID : [A-Za-z][A-Za-z0-9]*~([A-Za-z0-9 \n\r\t\f] | '(' | ')' | '{' | '}' | '[' | ']' | '+' | '-' | '*' | '/' | '=' | '<' | ';' | ',') -> skip;
ID : [A-Za-z][A-Za-z0-9]*;

MULTILINE_COMMENT_OPEN : '/*'  -> skip, pushMode(COMMENT_OPEN);
MULTILINE_COMMENT_CLOSE : '*/'  -> skip;
SINGLELINE_COMMENT : '/' '/' -> skip;
SLASH_DIGIT : '/' [0-9] -> skip;

// Symbols
INVALID_SYMBOL : (SYMBOL_START)~([A-Za-z0-9 \n\r\t\f] | '(' | ')' | '{' | '}' | '[' | ']' | '+' | '-' | '*' | '/' | '=' | '<' | ';' | ',' | '!') -> skip;
SYMBOL : SYMBOL_START;

fragment
SYMBOL_START : '==' | '(' | ')' | '{' | '}' | '[' | ']' | '+' | '-' | '*' | '/' | '=' | '<' | ';' | ',';

// Whitespace
WHITESPACE : [ \n\r\t\f]+ -> skip;

mode COMMENT_OPEN;
COMMENT_OPEN_SKIP : . -> skip;
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
    
    # Normalize line endings to LF before writing to prevent potential \r issues with ANTLR tool
    # although ANTLR should typically handle CRLF. This is an extra precaution.
    normalized_grammar = GRAMMAR_TEMPLATE.replace('\r\n', '\n').replace('\r', '\n')
    with open(grammar_file, "w", encoding='utf-8', newline='\n') as f:
        f.write(normalized_grammar)
    
    return grammar_file

def run_antlr(grammar_file):
    """Run ANTLR to generate lexer from grammar file."""
    try:
        original_dir = os.getcwd()
        # ANTLR tool is generally run from the directory containing the grammar file.
        # The grammar_file path is absolute or relative to the original_dir.
        # We change to ANTLR_DIR where CMinus.g4 is located.
        os.chdir(ANTLR_DIR)
        grammar_basename = os.path.basename(grammar_file) # Should be CMinus.g4
        
        try:
            # Check for the specific jar path found in error log first
            goldsmith_jar_path = '/Users/goldsmith/antlr-4.9.2-complete.jar'
            # Try to locate antlr jar
            # Option 1: In parent directory (project root relative to ANTLR_DIR)
            antlr_jar_project_root = os.path.join('..', 'antlr-4.9.2-complete.jar')
            # Option 2: In ANTLR_DIR itself
            antlr_jar_antlr_dir = 'antlr-4.9.2-complete.jar'
            
            antlr_cmd_base = ['java', '-jar']
            antlr_tool_options = ['-Dlanguage=Python3', grammar_basename] # Use just the basename

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
                    # Before falling back to 'antlr4' command, check if the jar path is valid
                    if '/Users/goldsmith/antlr-4.9.2-complete.jar' in ' '.join(antlr_cmd_base):
                        jar_path = '/Users/goldsmith/antlr-4.9.2-complete.jar'
                        if not os.path.exists(jar_path):
                            print(f"Error: ANTLR jar not found at {jar_path}")
                            print("Falling back to antlr4 command...")
                    
                    # Fallback to 'antlr4' command if ANTLR_JAR is not found or specified
                    print("ANTLR jar not found, trying the antlr4 command...")
                    try:
                        # First check if antlr4 is available and get its version
                        antlr4_version_cmd = ['antlr4', '-version']
                        version_process = subprocess.run(antlr4_version_cmd, check=False, capture_output=True, text=True)
                        if version_process.returncode == 0:
                            print(f"Using antlr4 command: {version_process.stdout.strip()}")
                            antlr_cmd = ['antlr4'] + antlr_tool_options
                        else:
                            # Try python -m antlr4 as a fallback
                            print("antlr4 command not found, trying python -m antlr4...")
                            antlr_cmd = [sys.executable, '-m', 'antlr4'] + antlr_tool_options
                    except Exception as e:
                        print(f"Error checking antlr4 command: {e}")
                        antlr_cmd = ['antlr4'] + antlr_tool_options  # Try anyway as last resort
            
            print(f"Running ANTLR command: {' '.join(antlr_cmd)} in directory {os.getcwd()}")
            process = subprocess.run(antlr_cmd, check=False, capture_output=True, text=True, encoding='utf-8')
            
            # Always print ANTLR output
            if process.stdout:
                print(f"ANTLR stdout:\n{process.stdout}")
            if process.stderr:
                print(f"ANTLR stderr:\n{process.stderr}")
            
            # Check return code manually
            if process.returncode != 0:
                print(f"ANTLR command failed with exit code {process.returncode}")
                return False

            # List all files in the current directory to see what ANTLR generated
            print("Files in ANTLR directory after running command:")
            for file in os.listdir('.'):
                print(f"  {file}")

            expected_lexer_file = grammar_basename.replace('.g4', '') + "Lexer.py"
            alternative_lexer_file = grammar_basename.replace('.g4', '') + ".py"
            
            if os.path.exists(expected_lexer_file):
                print(f"Found expected lexer file: {expected_lexer_file}")
                with open('__init__.py', 'w', encoding='utf-8') as f:
                    f.write("# ANTLR-generated package\n")
                return True
            elif os.path.exists(alternative_lexer_file):
                print(f"Found alternative lexer file: {alternative_lexer_file}")
                # Rename file to match expected pattern if needed
                if alternative_lexer_file != expected_lexer_file:
                    print(f"Renaming {alternative_lexer_file} to {expected_lexer_file}")
                    os.rename(alternative_lexer_file, expected_lexer_file)
                with open('__init__.py', 'w', encoding='utf-8') as f:
                    f.write("# ANTLR-generated package\n")
                return True
            else:
                print(f"Error: ANTLR did not generate the lexer file ({expected_lexer_file}).")
                print(f"Please check ANTLR_DIR ('{os.getcwd()}') for generated files and ANTLR output above.")
                return False
        finally:
            os.chdir(original_dir)
    except subprocess.CalledProcessError as e:
        # This block catches errors if check=True and the process returns a non-zero exit code.
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
    
    try:
        from antlr4 import FileStream, Token
    except ImportError:
        print("Error: antlr4-python3-runtime package is not installed.")
        print("Please install it with: pip install antlr4-python3-runtime")
        return None

    grammar_name_from_file = "CMinus" # Assumes the grammar is named CMinus
    lexer_class_name = grammar_name_from_file + "Lexer"
    lexer_py_filename = lexer_class_name + ".py"
    lexer_py_file_path = os.path.join(ANTLR_DIR, lexer_py_filename)

    if not os.path.exists(lexer_py_file_path):
        print(f"Error: Lexer file '{lexer_py_file_path}' not found.")
        print("Ensure ANTLR has generated the lexer successfully by calling run_antlr() first.")
        return None

    # Check the content of the lexer file to determine actual class name
    with open(lexer_py_file_path, 'r', encoding='utf-8') as f:
        lexer_content = f.read()
        
    # Try to find the actual class name from the file (assumes format "class SomeName(...)")
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
        # Import using the filename without .py to get the module
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
        
        # Try to get the class using the actual class name detected
        try:
            ActualCMinusClass = getattr(CMinusModule, actual_class_name)
            print(f"Successfully loaded {actual_class_name} class from module.")
        except AttributeError:
            print(f"Class {actual_class_name} not found in module. Available attributes:")
            for attr in dir(CMinusModule):
                if not attr.startswith('__'):
                    print(f"  - {attr}")
            
            # Try to find any class in the module that might be the lexer
            for attr in dir(CMinusModule):
                if not attr.startswith('__') and attr.endswith('Lexer'):
                    ActualCMinusClass = getattr(CMinusModule, attr)
                    print(f"Found alternative lexer class: {attr}")
                    break

    except Exception as e:
        print(f"ANTLR dynamic lexer loading failed: {e}")
        import traceback
        traceback.print_exc()
        # Restore sys.path and clean sys.modules even on failure here
        sys.path = original_sys_path
        if dynamic_module_name in sys.modules:
             del sys.modules[dynamic_module_name]
        return None 
    # No finally block for sys.path restoration here; do it after successful tokenization or error in that phase

    if ActualCMinusClass is None:
        print(f"Failed to get {lexer_class_name} class after attempting to load module.")
        sys.path = original_sys_path # Restore path
        if dynamic_module_name in sys.modules: # Clean sys.modules
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
                if token.channel == Token.HIDDEN_CHANNEL: # Filter skipped tokens
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

                token_text = token.text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t') # Escape control chars in output
                
                line_tokens.append(f"({token_type_name}, {token_text})")
            
            if line_tokens:
                f.write(f"{current_line}.\t{' '.join(line_tokens)} \n")
        
        return antlr_output_filepath
    except Exception as e:
        print(f"ANTLR tokenization processing failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally: # Ensure sys.path and sys.modules are cleaned up regardless of tokenization success/failure
        sys.path = original_sys_path
        if dynamic_module_name in sys.modules:
             del sys.modules[dynamic_module_name]


def check(tokens_file, antlr_file):
    """Compare the tokens from our scanner with ANTLR's output."""
    try:
        # Check if antlr_file is a relative path within the ANTLR directory
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
            # Using a unique name for temp files to avoid collision if run multiple times quickly
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
    
    # Also clean up any copied files in the current directory
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


if __name__ == '__main__':
    print("Starting C-minus ANTLR integration process...")

    print("\n--- Cleaning up previous ANTLR output ---")
    clean_antlr_output() 

    print("\n--- Generating ANTLR grammar file ---")
    grammar_file_path = generate_antlr_grammar()
    if not grammar_file_path or not os.path.exists(grammar_file_path):
        print("Failed to generate grammar file. Exiting.")
        sys.exit(1)
    print(f"Grammar file generated: {grammar_file_path}")

    print("\n--- Running ANTLR to generate Python lexer ---")
    if not run_antlr(grammar_file_path): 
        print("ANTLR lexer generation failed. Exiting.")
        sys.exit(1)
    print("ANTLR lexer generation successful.")

    # Using the test input provided by the user
    test_cminus_code = """
int min(voi){
	repeat {
		x = 23apple;
		mk3 = x + 1;
		if (mk3 == 52) {
			b =# 32;
			return;
		}
		break;}
	} until (arr[2milk])
	#this = 2;
	return;;!
}
// end of the code
/* end of end of the code
// hmmmmmm
@#$#%%$*/
"""
    temp_dir = tempfile.mkdtemp()
    # Ensure the temp_dir path is robust
    cminus_input_file_path = os.path.join(temp_dir, "test_input.cm")

    with open(cminus_input_file_path, "w", encoding='utf-8') as f:
        f.write(test_cminus_code)
    print(f"\n--- Created dummy C-minus input file: {cminus_input_file_path} ---")
    
    print("\n--- Tokenizing input file with ANTLR-generated lexer ---")
    antlr_token_output_file = tokenize_with_antlr(cminus_input_file_path)
    if not antlr_token_output_file:
        print("ANTLR tokenization failed. Exiting.")
        shutil.rmtree(temp_dir) 
        sys.exit(1)
    print(f"ANTLR tokenization successful. Output: {antlr_token_output_file}")

    if os.path.exists(antlr_token_output_file):
        print("\n--- ANTLR Tokens (from ANTLR_p1, HIDDEN_CHANNEL tokens are skipped) ---")
        with open(antlr_token_output_file, 'r', encoding='utf-8') as f:
            print(f.read())
            
    # Create a dummy file for "your_scanner_output" to allow comparison
    # In a real scenario, your_scanner_output_file would be generated by your scanner.
    your_scanner_output_file_path = os.path.join(temp_dir, "your_scanner_output.txt")
    if antlr_token_output_file and os.path.exists(antlr_token_output_file):
       shutil.copy(antlr_token_output_file, your_scanner_output_file_path)
       print(f"\n--- Assuming 'your_scanner_output.txt' is a copy of ANTLR's output for this test: {your_scanner_output_file_path} ---")
    
       print("\n--- Comparing outputs ---")
       similarity_percentage = check(your_scanner_output_file_path, antlr_token_output_file)
       print(f"\nSimilarity (for this test, should be 100%): {similarity_percentage:.2f}%")

    print("\n--- Final Cleanup ---")
    # clean_antlr_output() # Optional: clean ANTLR dir after run
    shutil.rmtree(temp_dir) 
    print("Process completed.") 