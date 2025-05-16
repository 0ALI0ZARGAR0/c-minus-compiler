// Define this as a lexer grammar.
// Save this content in a file named "CMinus.g4"
lexer grammar CMinus;

// Keywords
// These are defined first so they take precedence over the ID rule.
IF: 'if';
ELSE: 'else';
VOID: 'void';
INT: 'int';
REPEAT: 'repeat';
BREAK: 'break';
UNTIL: 'until';
RETURN: 'return';

// Symbols
ASSIGN: '=';      // Assignment operator
EQ:     '==';     // Equality operator
LPAREN: '(';      // Left parenthesis
RPAREN: ')';      // Right parenthesis
LBRACE: '{';      // Left brace
RBRACE: '}';      // Right brace
LBRACK: '[';      // Left bracket
RBRACK: ']';      // Right bracket
SEMI:   ';';      // Semicolon
COMMA:  ',';      // Comma
PLUS:   '+';      // Plus operator
MINUS:  '-';      // Minus operator
TIMES:  '*';      // Multiplication operator
DIV:    '/';      // Division operator
LESS:   '<';      // Less than operator

// Identifiers
// An identifier starts with a letter, followed by zero or more letters or digits.
ID: [a-zA-Z] [a-zA-Z0-9]*;

// Numbers
// A number is a sequence of one or more digits.
NUM: [0-9]+;

// Comments
// C-style block comments.
// The '-> skip' action tells ANTLR to find these tokens but not pass them on to the parser (or the token stream you'll inspect).
// This matches the project requirement that comments are not stored or reported in tokens.txt.
COMMENT: '/*' .*? '*/' -> skip;

// Whitespace
// Includes space, tab, carriage return, newline, vertical tab, and form feed.
// The '-> skip' action also applies here, as whitespace is generally ignored after tokenization.
WS: [ \t\r\n\u000B\u000C]+ -> skip; // \u000B is Vertical Tab, \u000C is Form Feed

// Note on Error Handling:
// ANTLR's default behavior for characters that do not match any rule is to create an error token.
// The specific error types mentioned in your project document, such as "Unmatched comment" for a standalone '*/'
// or "Invalid number" for a sequence like '123a', have a more nuanced handling in your custom scanner.
// For example, this ANTLR grammar would tokenize '123a' as NUM (123) followed by ID (a), and '*/' as TIMES (*) followed by DIV (/).
// Your 'Check()' function, when comparing your scanner's output to ANTLR's, should account for these differences,
// as ANTLR will primarily report a stream of validly formed tokens according to this grammar.
