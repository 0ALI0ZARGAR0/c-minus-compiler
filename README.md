# C-minus Compiler

Full front end for the **C-minus** teaching language: a deterministic scanner, a FIRST/FOLLOW–guided predictive parser with explicit parse-tree construction, scoped semantic analysis and diagnostics, quadruple-style three-address code (`SemanticRoutines` / `program_block`), and an optional ANTLR4 reference pipeline. This branch also contains a **parallel, in-progress refactor** toward centralized codegen (`SemanticLevel/CodeGen.py`, `Assembler.py`, `Parser/parser_v2.py`, `SymbolTableV2.py`) and archived experiments under `old_project/`.

## Methodology

- **Lexical analysis:** Table-driven scanner over explicit scanner states (`DFA/states_trans.py`, `DFA/DFA.py`); tokenization is a deterministic finite automaton walk, not a third-party lexer, for the core pipeline.
- **Grammar → parser states:** Productions from `Parser/grammer.txt` are expanded into a network of parser `State` objects (`Parser/grammer_to_transition.py`); each state carries terminal and nonterminal transitions.
- **Predictive (LL(1)-style) parsing:** Nonterminal expansion is gated by **FIRST** / **FOLLOW** sets (`Parser/first_follow.py`) against the current lookahead; a **deque** holds active parser states (`Parser/DFA.py`), with **anytree** used to materialize the concrete syntax tree for inspection.
- **Syntax-directed translation (default driver):** The grammar embeds **action symbols** (`#…`); `Parser/parser.py` drives `Semantic.run`, which dispatches to `func_<name>` in `SemanticLevel/SemanticRoutines.py` during the same pass as parsing. `compiler.py` imports this path and serializes `program_block` to `output/output.txt` and root `output.txt`.
- **Semantic analysis:** Scoped **symbol table** (`SemanticLevel/SymbolTable.py`), explicit error taxonomy (`SemanticLevel/ErrorType.py`), and auxiliary stacks for control flow, calls, and temporaries (`SemanticLevel/stacks.py`).
- **Intermediate code (production):** Quadruple-style **TAC** accumulated in `program_block`; **TempManager** (`Semantic.py`) allocates word-aligned temporaries; call sequences use snapshot/restore of live variables and critical temporaries (`SemanticRoutines` + `stacks.py`).
- **Centralized codegen (scaffold, not wired to `compiler.py`):** `SemanticLevel/CodeGen.py` maps a subset of `#` actions to routines backed by `SemanticLevel/Assembler.py` (`OPCode`, formatted quadruples). `Parser/parser_v2.py` sketches action dispatch over symbol streams. `SemanticLevel/SymbolTableV2.py` is a parallel symbol-table design surface. `old_project/` holds legacy/experimental codegen and runtime material retained for reference.
- **External cross-check (optional):** ANTLR4 grammar and generated lexer/parser under `antlr/`, orchestrated by `py_antlr.py`, for token/tree comparison against the hand-built front end.

The codebase is intentionally **large and tightly coupled** on the production path (scanner tokens, grammar layout, action placement, and semantic routines must stay consistent). The refactor files add a second axis of change until they replace or merge with the default pipeline.

### Pipeline (conceptual dataflow)

```mermaid
flowchart LR
  subgraph src [Source]
    IN["C-minus source"]
  end
  subgraph lex [Lexical]
    SCN["DFA scanner\nold_scanner.py + DFA/"]
  end
  subgraph syn [Syntax]
    PSR["State-stack parser\nParser/DFA.py"]
    G2S["Grammar → states\ngrammer_to_transition.py"]
    FF["FIRST / FOLLOW\nfirst_follow.py"]
  end
  subgraph sem [Semantics + IR]
    ACT["Semantic.run →\nSemanticRoutines"]
    ST["Symbol table\nSymbolTable"]
    TAC["TAC quadruples\nprogram_block"]
  end
  subgraph opt [Optional validation]
    ANL["ANTLR4\npy_antlr.py + antlr/"]
  end
  IN --> SCN --> PSR
  G2S -.-> PSR
  FF -.-> PSR
  PSR --> ACT --> ST
  ACT --> TAC
  IN -.-> ANL
```

### Default driver vs centralized codegen scaffold

`compiler.py` only exercises the left branch today. The right branch is present for incremental migration, not as the shipped driver.

```mermaid
flowchart TB
  CMP["compiler.py compile_file"]
  CMP --> SCAN["old_scanner.scanner"]
  SCAN --> P1["Parser.parser\nget_next_token loop"]
  P1 --> SEM["Semantic + SemanticRoutines"]
  SEM --> PB["program_block → output/output.txt"]
  subgraph exp [Scaffold not invoked by compiler.py]
    PV2["Parser/parser_v2.py"]
    CG["SemanticLevel/CodeGen.py"]
    ASM["SemanticLevel/Assembler.py"]
    ST2["SymbolTableV2.py"]
    PV2 --> CG --> ASM
    CG -.-> ST2
  end
```

### Driver, loop, and output artifacts

`compiler.py` copies the CLI path to `input.txt` (expected by `Parser/parser.py` initialization), runs the scanner/parser loop, then serializes results.

```mermaid
flowchart TB
  CLI["compiler.py main"] --> CP["input.txt"]
  CP --> SCN["scanner.get_next_token"]
  SCN --> LOOP["parser.get_next_token per token + $"]
  LOOP --> W1["output/tokens.txt"]
  LOOP --> W2["output/parse_tree.txt"]
  LOOP --> W3["output/syntax_errors.txt"]
  LOOP --> W4["output/symbol_table.txt"]
  LOOP --> W5["output/semantic_errors.txt"]
  LOOP --> W6["output/output.txt + output.txt"]
```

### Grammar file to parser automaton (import-time build)

Productions are read once at interpreter import; each rule becomes a chain of `State` instances wired by `grammer_to_transition.py`.

```mermaid
flowchart TD
  GT["Parser/grammer.txt"] --> SPL["split @ productions"]
  SPL --> FID["fill_nterminal_id_dict"]
  SPL --> RTS["rule_to_states for each rule"]
  RTS --> NET["terminal_trans maps"]
  RTS --> NNT["nterminal_trans sets"]
  NET --> IDM["id_state_dict global"]
  NNT --> IDM
  FID --> NF["nterminal_first_state map"]
  IDM --> PGO["Parser ready: deque + FIRST/FOLLOW"]
  NF --> PGO
```

### Parse step: terminal read vs nonterminal expansion

Simplified from `State.next_state` in `Parser/DFA.py`: either consume a terminal edge, or push the sub-automaton for a nonterminal whose FIRST/FOLLOW predicates match the lookahead.

```mermaid
flowchart TD
  S["current State"] --> Q{"terminal_trans\nhas token?"}
  Q -->|yes| T["move to next state_id\nappend token node"]
  Q -->|no| N["scan nterminal_trans"]
  N --> P{"FIRST U epsilon-in-FOLLOW\nmatches lookahead?"}
  P -->|yes| E["pop; push NT end;\npush NT start state"]
  P -->|no| ERR["syntax error path"]
  T --> STK["deque states_stack"]
  E --> STK
```

### Syntax-directed translation dispatch

When the grammar embeds an action symbol, the parser invokes `Semantic.run`; routines live as `func_<name>` in `SemanticRoutines` and mutate `program_block`, the symbol table, and auxiliary stacks.

```mermaid
sequenceDiagram
  participant D as Parser DFA
  participant M as Semantic.run
  participant R as SemanticRoutines
  participant T as program_block
  D->>M: assign + lookahead token
  Note over M: strips leading hash, func name
  M->>R: getattr func_assign
  R->>T: append quadruple
  R-->>D: return
```

### Repository layout (major Python surfaces)

```mermaid
flowchart TB
  subgraph entry [Entry]
    CMP["compiler.py"]
    PA["py_antlr.py"]
  end
  subgraph lex2 [Lexical]
    OS["old_scanner.py"]
    DFA["DFA/"]
  end
  subgraph parse [Syntax]
    PR["Parser/\nparser.py DFA.py\nfirst_follow.py\ngrammer_to_transition.py\nparser_v2.py"]
    GR["Parser/grammer.txt"]
  end
  subgraph sem2 [Semantics]
    SM["SemanticLevel/\nSemantic SemanticRoutines\nSymbolTable stacks ErrorType"]
    CG["CodeGen.py Assembler.py\nSymbolTableV2.py"]
  end
  subgraph legacy [Archive / experiments]
    OP["old_project/"]
  end
  subgraph tools [Tools]
    TI["tac_interpreter.py"]
    DV["Development.py"]
  end
  subgraph antlr_pkg [ANTLR reference]
    AG["antlr/ lexer+parser"]
  end
  CMP --> OS
  CMP --> PR
  CMP --> SM
  CMP -.->|not wired in driver| CG
  OS --> DFA
  PR --> GR
  PR --> SM
  PA --> AG
```

### Optional ANTLR cross-check

```mermaid
flowchart LR
  SRC["same source file"]
  SRC --> HAND["Hand pipeline\nscanner + Parser"]
  SRC --> ANT["py_antlr.py"]
  ANT --> LEX["CMinusLexer"]
  ANT --> PAR["CMinusParser"]
  HAND --> OUT1["output/* + diff hooks"]
  LEX --> OUT2["tokens / tree dumps"]
  PAR --> OUT2
  OUT1 -.-> CMP2["SequenceMatcher /\nmanual compare in py_antlr"]
  OUT2 -.-> CMP2
```

## Technologies Used

- **Language:** Python 3 (project historically targets 3.7+; use a current 3.x release).
- **Core libraries:** `anytree` (parse tree rendering); standard library (`argparse`, `collections.deque`, `enum`, `re`, `subprocess`, …).
- **Reference tooling:** `antlr4-python3-runtime`; **Java** + ANTLR tooling when regenerating or deeply exercising `py_antlr.py`.
- **Engineering:** `pre-commit` hooks — **Ruff** (lint/format), **darglint**, **detect-secrets**, **Commitizen** (commit-msg).

## Features

- Tokenizes C-minus with a hand-specified scanner DFA; writes `output/tokens.txt`.
- Parses with grammar-derived automata and FIRST/FOLLOW–guided transitions; writes `output/parse_tree.txt` and `output/syntax_errors.txt`.
- Semantic pass covers scopes, declarations, arrays, calls, and control flow; writes `output/semantic_errors.txt` and `output/symbol_table.txt`.
- On success, emits quadruple-style TAC to `output/output.txt` and root `output.txt`; `Tools/tac_interpreter.py` executes TAC for validation.
- CLI flags: `--verbose`, `--phase3-mandatory` (subset enforced in `Tools/Development.py`), `--antlr` (reference pipeline via `py_antlr.py`).
- Additional directories for coursework and regression: `testcases/`, `Testcases1/`, `Testcases2/`, `Testcases2-pr/`, `Testcases3/`.

## Quick Start

```bash
git clone https://github.com/0ALI0ZARGAR0/compiler.git && cd compiler
pip install anytree antlr4-python3-runtime
python compiler.py testcases/T1/input.txt
```

Optional: `python Tools/tac_interpreter.py output/output.txt` to execute generated TAC when compilation is semantically clean. For ANTLR-heavy workflows, install a JDK and ensure ANTLR is available as expected by `py_antlr.py`.

*Branch topology (local):* `origin/main` is at `7b8a375`; local `main` is one commit ahead at `640a62e` (codegen scaffold + parser/semantic edits). A detached README-only chain ending at `72dd038` was preserved as `readme-detached-archive` for comparison. Treat **`main` @ `640a62e`** plus this file as the codebase–README pair you want on disk.
