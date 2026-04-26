# C-minus Compiler

Hand-built compiler for the C-minus teaching language. The maintained pipeline in this repository is:

`old_scanner.py` -> `Parser/parser.py` -> `SemanticLevel/*` -> `output/`

The repository also includes an optional ANTLR reference path in `py_antlr.py` and `antlr/` for comparison work.

## Requirements

- Python 3
- `anytree`
- `antlr4-python3-runtime` for the ANTLR comparison flow

Example setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install anytree antlr4-python3-runtime
```

## Usage

Compile a source file:

```bash
python compiler.py path/to/input.c
```

Verbose mode:

```bash
python compiler.py cases/phase3-semantic/Test6/input.txt --verbose
```

Run the optional ANTLR comparison:

```bash
python compiler.py cases/phase3-semantic/Test6/input.txt --antlr
```

The CLI copies the selected input into `input.txt` because some legacy parser modules expect that filename during import.

## Generated Output

Each run writes compiler artifacts to `output/`:

- `tokens.txt`
- `symbol_table.txt`
- `parse_tree.txt`
- `syntax_errors.txt`
- `semantic_errors.txt`
- `output.txt`

The root-level `output.txt` is also generated for compatibility with the existing TAC tooling.

## Repository Layout

- `compiler.py`: main entrypoint
- `old_scanner.py`: DFA-based scanner
- `DFA/`: scanner state machine helpers
- `Parser/`: grammar, FIRST/FOLLOW tables, parser automaton
- `SemanticLevel/`: semantic routines, symbol table, TAC generation
- `Tools/`: small runtime/config helpers, including `tac_interpreter.py`
- `antlr/`, `py_antlr.py`: optional ANTLR reference implementation

## Test Assets

The repository keeps the local coursework/regression inputs that were already being used with this compiler:

- `cases/samples/`: general input samples
- `cases/phase1-lexical/`: scanner-oriented cases
- `cases/phase2-parser/`: parser input samples
- `cases/phase2-parser-expected/`: parser expected-output cases
- `cases/phase3-semantic/`: semantic/code-generation cases

`test_runs/` is treated as generated local output and is not part of the tracked project.

## Notes

- The coherent compiler baseline is the `origin/main` code line (`7b8a375`), not the later local experimental scaffold.
- Generated output files are intentionally ignored so the repository stays clean after runs.
