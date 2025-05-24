# C-minus Compiler

A Python implementation of a lexical analyzer (scanner) for the C-minus programming language, with optional ANTLR integration for validation.

## Features

- Lexical analysis of C-minus source code
- Comprehensive error detection and reporting
- Symbol table generation
- Optional ANTLR integration for validation
- Built-in test functionality
- Detailed token and error output

## Project Structure

```
.
├── cminus.py          # Main entry point script
├── scanner.py         # Lexical analyzer implementation
├── py_antlr.py        # ANTLR integration module
└── antlr/            # Directory for ANTLR-generated files
```

## Requirements

- Python 3.6+
- For ANTLR integration (optional):
  - Java Runtime Environment (JRE)
  - ANTLR4 JAR file
  - Python ANTLR4 runtime (`pip install antlr4-python3-runtime`)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/c-minus-compiler.git
cd c-minus-compiler
```

2. Install Python dependencies:

```bash
pip install loguru antlr4-python3-runtime
```

3. Make the scripts executable:

```bash
chmod +x cminus.py
```

## Usage

### Basic Usage

```bash
# Run the scanner on input.txt (default input file)
./cminus.py

# Run the scanner on a specific input file
./cminus.py my_program.txt

# Run with built-in test code
./cminus.py --test

# Run with verbose output (displays all tokens)
./cminus.py input.txt --verbose
```

### ANTLR Integration

```bash
# Run scanner and ANTLR comparison
./cminus.py input.txt --antlr

# Clean output files before processing
./cminus.py --clean
```

## Output Files

The scanner generates the following output files:

- `tokens.txt` - List of tokens identified in the input file
- `lexical_errors.txt` - List of lexical errors found
- `symbol_table.txt` - Table of identifiers found

When using ANTLR comparison, additional files will be generated in the `antlr/` directory.

## C-minus Language

C-minus is a simplified subset of C with the following features:

### Lexical Structure

- **Keywords**: `if`, `else`, `void`, `int`, `repeat`, `break`, `until`, `return`
- **Identifiers**: Start with a letter, followed by any number of letters or digits
- **Numbers**: Sequences of digits
- **Symbols**: `;`, `,`, `[`, `]`, `(`, `)`, `{`, `}`, `+`, `-`, `*`, `/`, `<`, `<=`, `>`, `>=`, `==`, `!=`, `=`
- **Comments**: Block comments between `/*` and `*/` and line comments starting with `//`

### Error Handling

The scanner detects the following types of errors:

- Invalid numbers (e.g., `123abc`)
- Unclosed comments
- Invalid input characters
- Invalid symbol sequences

## Scanner Implementation

The scanner uses a state machine approach to tokenize input:

1. It reads the input file character by character
2. Based on the current state and character, it transitions to appropriate states
3. When a complete token is identified, it's added to the token list
4. Detected errors are recorded separately
5. The scanner outputs tokens, errors, and the symbol table to separate files

## ANTLR Integration

The project includes optional ANTLR integration for validation:

1. Generates an ANTLR grammar file based on the C-minus language specification
2. Runs the ANTLR tokenizer on the input file
3. Compares the scanner output with ANTLR output
4. Reports similarity percentage between the two implementations

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
