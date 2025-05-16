
lexer grammar CMinus;

IF: 'if';
ELSE: 'else';
VOID: 'void';
INT: 'int';
REPEAT: 'repeat';
BREAK: 'break';
UNTIL: 'until';
RETURN: 'return';

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

ID: [a-zA-Z] [a-zA-Z0-9]*;

NUM: [0-9]+;

COMMENT: '/*' .*? '*/' -> skip;

WS: [ \t\r\n\u000B\u000C]+ -> skip; // \u000B is Vertical Tab, \u000C is Form Feed
