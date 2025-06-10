# C-minus Compiler

A complete C-minus language compiler with lexical analysis, syntax parsing, and semantic analysis.

## Usage

```bash
python compiler.py input_file.c [--verbose]
```

**Examples:**

```bash
# Basic compilation
python compiler.py Testcases1/T01/input.txt

# Verbose output with detailed analysis
python compiler.py Testcases2-pr/T1/input.txt --verbose
```

## Output Files

The compiler generates organized output in `output/` directory:

- `tokens.txt` - Tokenization results
- `symbol_table.txt` - Symbol table
- `parse_tree.txt` - Parse tree structure
- `syntax_errors.txt` - Syntax error report
- `semantic_errors.txt` - Semantic error report
- `output.txt` - Generated intermediate code

## Project Structure

**Core Files:**

- `compiler.py` - Main compiler (single file)
- `old_scanner.py` - DFA-based scanner implementation

**Engine Components:**

- `Parser/` - DFA-based parser implementation
- `SemanticLevel/` - Semantic analysis and code generation
- `DFA/` - Deterministic Finite Automaton components
- `Tools/` - Utility functions and development tools

**Test Cases:**

- `Testcases1/` - Original test cases
- `Testcases2/` - Additional test cases
- `Testcases2-pr/` - Project test cases

## Features

✅ Complete lexical analysis with DFA-based tokenization  
✅ Robust LL(1) syntax parsing with error recovery  
✅ Comprehensive semantic analysis  
✅ Type checking and scope management  
✅ Intermediate code generation  
✅ Detailed error reporting with line numbers  
✅ Clean, organized output files

## C-minus Language Support

The compiler supports the complete C-minus language specification including:

- Variable declarations (`int`, `void`)
- Array declarations and access
- Function declarations and calls
- Control structures (`if`, `else`, `while`, `return`) - **Standard C syntax, no `endif` required!**
- Arithmetic and comparison operations
- Proper scoping and type checking
