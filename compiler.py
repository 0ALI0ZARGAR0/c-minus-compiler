#!/usr/bin/env python3

"""
C-minus Compiler
A complete C-minus language compiler with lexical analysis, syntax parsing, and semantic analysis.
Consolidated single-file implementation.
"""

import os
import shutil
import sys


def file2str(filepath):
    """Read file content as string"""
    with open(filepath, "r") as f:
        return f.read()


def save_tuple2file_based_on_1element(file_name, tl):
    """Save tokens to file grouped by line number"""
    os.makedirs("output", exist_ok=True)
    with open(os.path.join("output", file_name), mode="w") as f:
        this_el = -1
        for t in tl:
            # resolve \n error
            if "\n" in t[1]:
                t = (t[0] - 1, t[1].replace("\n", ""), t[2])
            if t[0] == this_el:
                f.write("(" + t[1] + ", " + t[2] + ") ")
            else:
                if this_el != -1:
                    f.write("\n")
                this_el = t[0]
                f.write(str(this_el) + "." + "\t")
                f.write(("(" + t[1] + ", " + t[2] + ") "))


def save_list2file(file_name, l):
    """Save list to file with line numbers"""
    os.makedirs("output", exist_ok=True)
    with open(os.path.join("output", file_name), mode="w") as f:
        for i, t in enumerate(l):
            f.write("{0:4}".format(str(i + 1) + "."))
            f.write(t + "\n")


def save_symbol_table(addr):
    """Save the symbol table into output/symbol_table.txt in a readable form."""
    from SemanticLevel.SymbolTable import SymbolTableClass
    st = SymbolTableClass.get_instance()
    os.makedirs("output", exist_ok=True)
    lines = []
    for row in st.pars_table:
        parts = [
            f"addr={row.address}",
            f"lexeme={row.lexeme}",
            f"type={row.type}",
            f"scope={row.scope}",
            f"category={row.category}",
        ]
        if getattr(row, "is_arr", False):
            parts.append(f"len={row.args_cells}")
        lines.append(" ".join(parts))
    with open(os.path.join("output", addr), "w", encoding="utf-8") as f:
        for i, line in enumerate(lines):
            f.write("{0:4}".format(str(i + 1) + "."))
            f.write(line + "\n")


def save_tree(addr):
    """Save parse tree to file"""
    from Parser import parser
    tree = parser.draw_tree()
    os.makedirs("output", exist_ok=True)
    with open(os.path.join("output", addr), "w", encoding="utf-8") as f:
        f.write(tree)


def save_syntax_errors(addr):
    """Save syntax errors to file"""
    from Parser import parser
    errors = parser.get_pars_errors()
    os.makedirs("output", exist_ok=True)
    if not errors:
        with open(os.path.join("output", addr), "w", encoding="utf-8") as f:
            f.write("There is no syntax error.")
    else:
        with open(os.path.join("output", addr), "w", encoding="utf-8") as f:
            for e in errors:
                f.write(e + "\n")


def save_semantic_errors(addr):
    """Save semantic errors to file"""
    from SemanticLevel import ErrorType
    errors = ErrorType.semantic_errors
    os.makedirs("output", exist_ok=True)
    if not errors:
        with open(os.path.join("output", addr), "w", encoding="utf-8") as f:
            f.write("The input program is semantically correct.")
    else:
        with open(os.path.join("output", addr), "w", encoding="utf-8") as f:
            for e in errors:
                f.write(e + "\n")


def pp_list_of_tuples(lsot):
    """Pretty print intermediate code"""
    from SemanticLevel import ErrorType
    os.makedirs("output", exist_ok=True)
    s = ""
    if ErrorType.semantic_errors:
        s = "The output code has not been generated"
    else:
        for idx, t in enumerate(lsot):
            s += f"{idx}\t{t}\n"

    # Write where the Tester expects and also in our organized folder
    with open("output.txt", "w") as f_root:
        f_root.write(s)
    with open(os.path.join("output", "output.txt"), "w") as f_dir:
        f_dir.write(s)


def compile_file(input_file, verbose=False):
    """
    Main compiler function
    """
    try:
        # Import compiler components
        from old_scanner import scanner
        from Parser import parser
        from SemanticLevel import ErrorType
        from SemanticLevel.SemanticRoutines import program_block
        from Tools import Development

        # Clean semantic stack traces for prettier output
        if not verbose:
            # Temporarily disable develop_mode to reduce clutter
            original_develop_mode = Development.develop_mode
            Development.develop_mode = False
            
            # Patch semantic output for cleaner display
            from SemanticLevel import Semantic
            original_semantic_init = Semantic.Semantic.__init__
            original_semantic_run = Semantic.Semantic.run
            
            def clean_semantic_init(self, pars_table):
                self.parse_table = pars_table
                self.temp_manager = Semantic.TempManager(1500, 4)
                Semantic.semantic_instance = self
            
            def clean_semantic_run(self, func_name, input_token):
                from SemanticLevel import SemanticRoutines
                func_name = func_name[1:len(func_name)]
                getattr(SemanticRoutines, "func_" +
                        func_name)(self.temp_manager.get_temp, input_token)
            
            Semantic.Semantic.__init__ = clean_semantic_init
            Semantic.Semantic.run = clean_semantic_run

        if verbose:
            print("🔧 C-MINUS COMPILER")
            print("-" * 40)
            print(f"   Input file: {input_file}")
            print()

        # Read the input file
        s = file2str(input_file)
        
        # Initialize scanner
        scnr = scanner(s=s)
        
        if verbose:
            print("🔍 COMPILATION PROCESS:")
            print("-" * 40)

        token_count = 0
        # Process tokens through parser
        while True:
            line, next_token_type, next_token = scnr.get_next_token()
            ErrorType.gl_line_number = line
            
            if next_token_type is None:
                parser.get_next_token("$", line)
                break
            else:
                parser.get_next_token((str(next_token_type), str(next_token)), line)
                token_count += 1
                if verbose and token_count <= 5:
                    print(f"   Token {token_count:3}: Line {line:2} | {next_token_type:8} | '{next_token}'")
                elif verbose and token_count == 6:
                    print(f"   ... (processing {token_count}+ tokens)")

        # Generate output files
        save_tuple2file_based_on_1element("tokens.txt", scnr.tokens)
        save_symbol_table("symbol_table.txt")
        save_tree("parse_tree.txt")
        save_syntax_errors("syntax_errors.txt")
        save_semantic_errors("semantic_errors.txt")
        pp_list_of_tuples(program_block)

        # Show results
        if verbose:
            print(f"   Total tokens processed: {token_count}")
            print()

        print("📊 COMPILATION RESULTS:")
        print("-" * 40)
        
        # Show syntax errors
        syntax_errors = parser.get_pars_errors()
        if syntax_errors:
            print(f"❌ Syntax: {len(syntax_errors)} error(s) found")
            if verbose:
                for error in syntax_errors:
                    print(f"   • {error}")
        else:
            print("✅ Syntax: No errors")
            
        # Show semantic errors  
        if ErrorType.semantic_errors:
            print(f"❌ Semantic: {len(ErrorType.semantic_errors)} error(s) found")
            if verbose:
                for error in ErrorType.semantic_errors:
                    print(f"   • {error}")
        else:
            print("✅ Semantic: No errors")
            
        print(f"📁 Output: Generated in output/ directory")
        
        # Restore original settings
        if not verbose:
            Development.develop_mode = original_develop_mode
            Semantic.Semantic.__init__ = original_semantic_init
            Semantic.Semantic.run = original_semantic_run
        
        return True
        
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def run_antlr_analysis(input_file):
    """Run ANTLR analysis if py_antlr.py is available."""
    try:
        from py_antlr import compare_with_our_compiler, run_full_antlr_analysis
        print("\n🔧 RUNNING ANTLR ANALYSIS")
        print("="*60)
        success = run_full_antlr_analysis(input_file)
        if success:
            compare_with_our_compiler(input_file)
        return success
    except ImportError:
        print("⚠️  ANTLR analysis not available (py_antlr.py not found)")
        return False
    except Exception as e:
        print(f"❌ ANTLR analysis failed: {e}")
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="C-minus Compiler")
    parser.add_argument("input_file", help="Input C-minus file to compile")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--antlr", action="store_true", help="Run ANTLR comparison analysis")
    parser.add_argument("--phase3-mandatory", action="store_true", help="Enable Phase 3 mandatory subset (no function calls/returns)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' not found")
        return 1
    
    # Copy input file to input.txt (required by compiler components)
    if os.path.abspath(args.input_file) != os.path.abspath("input.txt"):
        shutil.copy2(args.input_file, "input.txt")
    
    # Configure Phase 3 mandatory behavior before compilation
    try:
        from Tools import Development as DevCfg
        DevCfg.phase3_mandatory = args.phase3_mandatory
    except Exception:
        pass

    success = compile_file("input.txt", args.verbose)
    
    # Optional ANTLR analysis
    if args.antlr:
        run_antlr_analysis(args.input_file)
    
    if success:
        print("✓ Compilation completed")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main()) 