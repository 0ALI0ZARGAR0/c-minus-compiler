#!/usr/bin/env python3
# C-minus Compiler Entry Point

import argparse
import os
import shutil
import sys

from py_antlr import check as antlr_check
from py_antlr import generate_antlr_grammar, run_antlr, tokenize_with_antlr
from scanner import clean_output_files, scan_file


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def clean_antlr_output():
    """Clean up ANTLR output files."""
    files_to_clean = ["antlr/ANTLR_p1"]
    
    for file in files_to_clean:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed {file}")
            except Exception as e:
                print(f"Failed to remove {file}: {e}")


def main():
    """Main entry point for the C-minus compiler."""
    parser = argparse.ArgumentParser(
        description='C-minus Compiler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cminus.py input.txt              # Run the scanner on input.txt
  cminus.py input.txt --antlr      # Also run ANTLR tokenization and compare
  cminus.py --test                 # Run built-in test
  cminus.py --clean                # Clean all output files
"""
    )
    
    parser.add_argument('input_file', nargs='?', default='input.txt',
                      help='Input file to process (default: input.txt)')
    
    parser.add_argument('--antlr', action='store_true',
                      help='Also run ANTLR tokenization and compare results')
    
    parser.add_argument('--test', action='store_true',
                      help='Run with built-in test code')
    
    parser.add_argument('--clean', action='store_true',
                      help='Clean output files before processing')
    
    parser.add_argument('--verbose', action='store_true',
                      help='Show more detailed output')
    
    args = parser.parse_args()
    
    # Clean output files if requested
    if args.clean:
        print_header("CLEANING FILES")
        clean_output_files()
        clean_antlr_output()
        return 0
    
    # Create test file if requested
    if args.test:
        print_header("RUNNING TEST")
        from scanner import create_test_file
        args.input_file = create_test_file()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return 1
    
    # Run the scanner
    print_header("RUNNING SCANNER")
    print(f"Input file: {args.input_file}")
    scanner_success = scan_file(args.input_file)
    
    if not scanner_success:
        print("Scanner encountered errors.")
        return 1
    
    # Display scanner results
    print("\nScanner completed successfully.")
    print("Generated output files:")
    print("  - tokens.txt")
    print("  - lexical_errors.txt")
    print("  - symbol_table.txt")
    
    # Run ANTLR comparison if requested
    if args.antlr:
        
        print_header("RUNNING ANTLR")
        
        # Generate grammar file
        grammar_file = generate_antlr_grammar()
        print(f"Generated grammar file: {grammar_file}")
        
        # Run ANTLR
        if not run_antlr(grammar_file):
            print("ANTLR processing failed.")
            return 1
        
        # Tokenize with ANTLR
        print(f"Tokenizing {args.input_file} with ANTLR...")
        antlr_tokens = tokenize_with_antlr(args.input_file)
        
        if not antlr_tokens:
            print("ANTLR tokenization failed.")
            return 1
        
        # Compare outputs
        print_header("COMPARING OUTPUTS")
        similarity = antlr_check("tokens.txt", "antlr/ANTLR_p1")
        print(f"\nSimilarity: {similarity:.2f}%")
        if similarity > 90.0:
            print("High similarity - Scanner works correctly!")
        else:
            print("Low similarity - Scanner may need improvements.")
    
    # Clean up test file if created
    if args.test:
        try:
            os.unlink(args.input_file)
            print(f"\nDeleted temporary test file: {args.input_file}")
        except Exception as e:
            print(f"\nWarning: Failed to delete temporary test file: {e}")
    
    # Display tokens if verbose mode or test mode
    if args.verbose or args.test:
        print_header("TOKEN OUTPUT")
        try:
            with open("tokens.txt", "r") as f:
                print(f.read())
            
            print_header("LEXICAL ERRORS")
            with open("lexical_errors.txt", "r") as f:
                print(f.read())
            
            print_header("SYMBOL TABLE")
            with open("symbol_table.txt", "r") as f:
                print(f.read())
        except Exception as e:
            print(f"Error reading output files: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 