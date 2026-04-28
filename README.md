# C-minus Compiler
Hand-written compiler for the C-minus teaching language with DFA-based lexical analysis, FIRST/FOLLOW-guided predictive parsing, semantic checking, and quadruple-style intermediate code generation.

## Academic Context / Methodology

- Primary pipeline is generator-independent: scanner, parser, semantic routines, and IR emission are implemented manually rather than delegated to a compiler framework.
- Lexical analysis is implemented as an explicit deterministic finite automaton over handcrafted transition tables in `DFA/` and `old_scanner.py`.
- Syntax analysis is implemented as a predictive parser: grammar productions from `Parser/grammer.txt` are converted into parser states in `Parser/grammer_to_transition.py`, and lookahead decisions are constrained by precomputed FIRST/FOLLOW sets in `Parser/first_follow.py`.
- Semantic processing is syntax-directed: action symbols embedded in the grammar dispatch routines in `SemanticLevel/SemanticRoutines.py` during parsing.
- Semantic state is managed through a scoped symbol table, auxiliary stacks, backpatching for control flow, and a quadruple-form three-address code buffer (`program_block`).
- `antlr/` and `py_antlr.py` provide a separate ANTLR-based reference path for comparison, but the maintained compiler path is the hand-built frontend.

## Technologies Used

- Standard library: `argparse`, `collections.deque`, `contextlib`, `pathlib`, `re`, `shutil`, `subprocess`
- `anytree` for parse-tree rendering
- `antlr4-python3-runtime` for the optional ANTLR reference flow
- Mermaid for architecture documentation

## Features

- Compiles C-minus source into tokens, lexical errors, parse tree, syntax errors, semantic errors, symbol table output, and three-address code.
- Supports declarations, arrays, expressions, `if/else`, `repeat-until`, `while`, `return`, function declarations, function calls, and `output`.
- Generates quadruple-style TAC and includes a local TAC interpreter in `Tools/tac_interpreter.py` for execution checks.
- Organizes the project’s phased coursework and regression assets under `cases/` and includes a repeatable verification script in `scripts/verify_cases.py`.
- Keeps an ANTLR grammar and runtime path for secondary validation without replacing the main handwritten compiler path.

## Quick Start / Reproducibility

```bash
git clone https://github.com/0ALI0ZARGAR0/compiler.git && cd compiler
python3 -m venv .venv && . .venv/bin/activate && pip install anytree antlr4-python3-runtime
python3 compiler.py cases/phase3-semantic/Test6/input.txt && python3 scripts/verify_cases.py
```

The first command clones the repository, the second installs the runtime dependencies, and the third both runs a representative semantic/code-generation case and executes the project’s phase-level verification script.

## Contributor Overview

This section is auto-generated from repository commit history by `scripts/update_contributor_overview.py`. It uses an alias map so contributor identities remain merged consistently across different commit emails.

<!-- contributor-overview:start -->
Auto-generated from current branch history.

| Contributor | Share |
| --- | ---: |
| [Ali Zargar](https://github.com/0ALI0ZARGAR0) | 77.5% |
| [Eliya Kaheni](https://github.com/EliyaKaheni) | 15.0% |
| [Hamidreza Entezari](https://github.com/hamidrezaen) | 7.5% |

```mermaid
pie
    title Relative Contribution Share
    "Ali Zargar" : 77.5
    "Eliya Kaheni" : 15.0
    "Hamidreza Entezari" : 7.5
```

[Open GitHub contributors graph](https://github.com/0ALI0ZARGAR0/c-minus-compiler/graphs/contributors)
<!-- contributor-overview:end -->

## Architecture Diagrams

The source for all diagrams is kept under `docs/diagrams/`. The README currently includes Mermaid definitions directly so the project structure and compiler pipeline stay inspectable in plain text and can later be rendered to SVG from the same sources.

### End-to-End Compiler Architecture

```mermaid
flowchart LR
    subgraph Input["Source Input"]
        SRC["C-minus program"]
    end

    subgraph Lex["Lexical Analysis"]
        DFA["DFA transition tables<br/>DFA/states_trans.py"]
        SCN["Scanner runtime<br/>old_scanner.py"]
        TOK["Token stream<br/>(type, lexeme, line)"]
        SRC --> SCN --> TOK
        DFA -.drives.-> SCN
    end

    subgraph Syn["Syntax Analysis"]
        GR["Grammar rules<br/>Parser/grammer.txt"]
        FF["FIRST/FOLLOW sets<br/>Parser/first_follow.py"]
        PAR["Predictive parser DFA<br/>Parser/parser.py + Parser/DFA.py"]
        TREE["Concrete parse tree<br/>anytree nodes"]
        SYNERR["Syntax diagnostics"]
        GR -.compiled to states.-> PAR
        FF -.lookahead decisions.-> PAR
        TOK --> PAR
        PAR --> TREE
        PAR --> SYNERR
    end

    subgraph Sem["Semantic Analysis and IR"]
        ACT["Embedded action symbols<br/>#assign / #jpf / #call_*"]
        ROUT["SemanticRoutines.py"]
        ST["Scoped symbol table"]
        PB["program_block<br/>quadruple TAC"]
        SEMERR["Semantic diagnostics"]
        PAR --> ACT --> ROUT
        ROUT --> ST
        ROUT --> PB
        ROUT --> SEMERR
    end

    subgraph Out["Artifacts and Validation"]
        OUT["output/<br/>tokens, tree, symbol_table,<br/>syntax_errors, semantic_errors, output.txt"]
        TAC["Tools/tac_interpreter.py"]
        PB --> OUT
        PB --> TAC
    end

    REF["ANTLR reference path<br/>py_antlr.py + antlr/"] -.optional comparison.-> OUT
```

### Grammar-to-Parser State Construction

```mermaid
flowchart TD
    subgraph Build["Import-Time Parser Construction"]
        G["Parser/grammer.txt"]
        FID["fill_nterminal_id_dict"]
        RTS["rule_to_states"]
        IDS["id_state_dict"]
        NFS["nterminal_first_state"]
        G --> FID
        G --> RTS
        FID --> RTS
        RTS --> IDS
        RTS --> NFS
    end

    subgraph Lookahead["Predictive Tables"]
        FIRST["nterminal_first_dict"]
        FOLLOW["nterminal_follow_dict"]
    end

    subgraph Runtime["Runtime Parse Step"]
        STK["states_stack<br/>deque"]
        STEP["State.next_state(...)"]
        TERM{"terminal edge?"}
        NTERM{"nonterminal FIRST/FOLLOW match?"}
        EPS{"epsilon edge?"}
        ACTSYM{"semantic action edge?"}
        TREE["parse tree node append"]
        ERR["error recovery / diagnostics"]
        STK --> STEP
        STEP --> TERM
        TERM -->|yes| TREE
        TERM -->|no| NTERM
        NTERM -->|yes| STK
        NTERM -->|no| EPS
        EPS -->|yes| STK
        EPS -->|no| ACTSYM
        ACTSYM -->|yes| TREE
        ACTSYM -->|no| ERR
    end

    IDS --> STK
    NFS --> STK
    FIRST --> NTERM
    FOLLOW --> NTERM
    FOLLOW --> EPS
    FOLLOW --> ACTSYM
```

### Semantic Execution, Backpatching, and TAC

```mermaid
flowchart LR
    subgraph Driver["Syntax-Directed Execution"]
        ACT["parser action symbol"]
        RUN["Semantic.run(...)"]
        ROUT["SemanticRoutines"]
        ACT --> RUN --> ROUT
    end

    subgraph State["Semantic State"]
        SS["semantic_stack"]
        ST["SymbolTableClass"]
        TM["TempManager"]
        SNAP["SnapshotStack"]
        FRS["FunctionRelatedStack"]
    end

    subgraph IR["Intermediate Representation"]
        PB["program_block"]
        IFBP["if / else backpatching<br/>save, jpf_save, jp"]
        LOOPBP["repeat / while backpatching<br/>label, until, while_jpf, while_jp_back"]
        CALLS["call protocol<br/>save snapshot, push args,<br/>return address, restore state"]
        ARR["array address calculation<br/>MULT index,#4 -> ADD base,offset"]
    end

    subgraph Verify["Execution Check"]
        TAC["Tools/tac_interpreter.py"]
        PRINT["observed PRINT values"]
    end

    ROUT --> SS
    ROUT --> ST
    ROUT --> TM
    ROUT --> SNAP
    ROUT --> FRS
    ROUT --> PB
    SS --> ARR --> PB
    ST --> CALLS --> PB
    SNAP --> CALLS
    FRS --> CALLS
    PB --> IFBP
    PB --> LOOPBP
    PB --> TAC --> PRINT
```

### Repository Phases and Verification Coverage

```mermaid
flowchart TB
    ROOT["compiler/"] --> CORE["core compiler implementation"]
    ROOT --> CASES["cases/"]
    ROOT --> DOCS["docs/diagrams/"]
    ROOT --> VERIFY["scripts/verify_cases.py"]

    subgraph CaseTree["Phased Test Assets"]
        P1["phase1-lexical<br/>scanner outputs"]
        P2["phase2-parser<br/>parser input corpus"]
        P2E["phase2-parser-expected<br/>expected parse trees / syntax errors"]
        P3["phase3-semantic<br/>semantic + TAC cases"]
        SAMP["samples<br/>mixed reference programs"]
    end

    CASES --> P1
    CASES --> P2
    CASES --> P2E
    CASES --> P3
    CASES --> SAMP

    P1 --> V1["verify lexical_errors + tokens"]
    P2E --> V2["verify syntax_errors"]
    P3 --> V3["verify semantic_errors + TAC output"]

    V1 --> VERIFY
    V2 --> VERIFY
    V3 --> VERIFY

    VERIFY --> REPORT["repeatable phase smoke-check"]
```





