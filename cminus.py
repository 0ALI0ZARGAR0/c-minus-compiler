#!/usr/bin/env python3

import argparse
import os
import sys


def main():
    parser_arg = argparse.ArgumentParser(
        description="C-minus Compiler with robust parsing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.txt                    # Compile input.txt
  %(prog)s input.txt --verbose          # Compile with detailed output
  %(prog)s --help                       # Show this help message
        """
    )
    
    parser_arg.add_argument(
        'input_file',
        help='C-minus source file to compile'
    )
    
    parser_arg.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed compilation output'
    )
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser_arg.print_help()
        return 1
        
    args = parser_arg.parse_args()
    
    # Validate input file
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        return 1
    
    # Create input.txt for the old project (it expects this specific filename)
    import shutil
    shutil.copy2(args.input_file, "input.txt")
    
    try:
        # Now run the old project's compiler logic directly
        from old_project_wrapper import run_compiler
        success = run_compiler(args.verbose)
        
        if success:
            print(f"✓ Compilation completed successfully")
            print(f"\nGenerated files in output/ directory:")
            if os.path.exists("output/tokens.txt"):
                print("  - output/tokens.txt")
            if os.path.exists("output/symbol_table.txt"):
                print("  - output/symbol_table.txt") 
            if os.path.exists("output/parse_tree.txt"):
                print("  - output/parse_tree.txt")
            if os.path.exists("output/syntax_errors.txt"):
                print("  - output/syntax_errors.txt")
            if os.path.exists("output/semantic_errors.txt"):
                print("  - output/semantic_errors.txt")
            if os.path.exists("output/output.txt"):
                print("  - output/output.txt")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"Compilation failed: {e}")
        return 1
    finally:
        # Clean up
        if os.path.exists("input.txt"):
            os.remove("input.txt")


if __name__ == "__main__":
    sys.exit(main()) 