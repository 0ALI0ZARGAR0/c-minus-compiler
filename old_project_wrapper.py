"""
Wrapper module for the old project's compiler logic
This integrates the old project's robust parsing into our new framework
"""

import os
import sys


def file2str(filepath):
    """Read file content as string"""
    with open(filepath, "r") as f:
        return f.read()


def save_tuple2file_based_on_1element(file_name, tl):
    """Save tokens grouped by line number"""
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
    with open(os.path.join("output", "output.txt"), "w") as f:
        s = ""
        if ErrorType.semantic_errors:
            s = "The output code has not been generated"
        else:
            for idx, t in enumerate(lsot):
                s += f"{idx}\t{t}\n"
        f.write(s)


def run_compiler(verbose=False):
    """
    Main compiler function that integrates the old project's logic
    """
    try:
        # Import the old project components
        from old_scanner import scanner
        from Parser import parser
        from SemanticLevel import ErrorType
        from SemanticLevel.SemanticRoutines import program_block
        from Tools import Development

        # Temporarily disable develop_mode to reduce clutter in console
        original_develop_mode = Development.develop_mode
        Development.develop_mode = False  # Disable console semantic trace for cleaner display
        
        # Also need to disable it in the Semantic module
        from SemanticLevel import Semantic

        # Patch the Semantic class to not print traces
        original_semantic_init = Semantic.Semantic.__init__
        original_semantic_run = Semantic.Semantic.run
        
        def clean_semantic_init(self, pars_table):
            # Initialize without printing the header
            self.parse_table = pars_table
            self.temp_manager = Semantic.TempManager(1500, 4)
            Semantic.semantic_instance = self
        
        def clean_semantic_run(self, func_name, input_token):
            # Run without printing traces
            from SemanticLevel import SemanticRoutines
            func_name = func_name[1:len(func_name)]
            getattr(SemanticRoutines, "func_" +
                    func_name)(self.temp_manager.get_temp, input_token)
        
        # Apply patches for clean output
        if not verbose:
            Semantic.Semantic.__init__ = clean_semantic_init
            Semantic.Semantic.run = clean_semantic_run

        # Read the input file (old project expects input.txt)
        addr = "input.txt"
        s = file2str(addr)
        
        # Initialize scanner
        scnr = scanner(s=s)
        
        # Process tokens through parser
        while True:
            line, next_token_type, next_token = scnr.get_next_token()
            ErrorType.gl_line_number = line
            if next_token_type is None:
                parser.get_next_token("$", line)
                break
            else:
                parser.get_next_token(
                    (str(next_token_type), str(next_token)), line)

        # Generate output files (always generate for better debugging)
        save_tuple2file_based_on_1element("tokens.txt", scnr.tokens)
        save_list2file("symbol_table.txt", scnr.lexemes)
        save_tree("parse_tree.txt")
            
        save_syntax_errors("syntax_errors.txt")
        save_semantic_errors("semantic_errors.txt")
        pp_list_of_tuples(program_block)

        # Show results if verbose
        if verbose:
            print("\n" + "="*60)
            print("                    COMPILATION RESULTS")
            print("="*60)
            
            # Show syntax errors
            syntax_errors = parser.get_pars_errors()
            print("\n🔍 SYNTAX ANALYSIS:")
            print("-" * 40)
            if syntax_errors:
                print(f"❌ Found {len(syntax_errors)} syntax error(s):")
                for error in syntax_errors:
                    print(f"   • {error}")
            else:
                print("✅ No syntax errors found")
                
            # Show parse tree
            print("\n🌳 PARSE TREE:")
            print("-" * 40)
            try:
                tree = parser.draw_tree()
                if tree and len(tree.strip()) > 0:
                    # Show first few lines of parse tree
                    tree_lines = tree.split('\n')
                    if len(tree_lines) > 20:
                        for line in tree_lines[:15]:
                            print(f"   {line}")
                        print(f"   ... ({len(tree_lines)-15} more lines)")
                        print(f"   📄 Full parse tree saved to: output/parse_tree.txt")
                    else:
                        for line in tree_lines:
                            if line.strip():
                                print(f"   {line}")
                else:
                    print("   ⚠️  Parse tree generation failed")
            except Exception as e:
                print(f"   ❌ Error generating parse tree: {e}")
                
            # Show semantic errors  
            print("\n🧠 SEMANTIC ANALYSIS:")
            print("-" * 40)
            if ErrorType.semantic_errors:
                print(f"❌ Found {len(ErrorType.semantic_errors)} semantic error(s):")
                for error in ErrorType.semantic_errors:
                    print(f"   • {error}")
            else:
                print("✅ No semantic errors found")
                
            print("\n" + "="*60)
        
        # Restore original develop_mode and semantic methods
        Development.develop_mode = original_develop_mode
        if not verbose:
            Semantic.Semantic.__init__ = original_semantic_init
            Semantic.Semantic.run = original_semantic_run
        
        return True
        
    except Exception as e:
        print(f"Compiler error: {e}")
        import traceback
        traceback.print_exc()
        return False 