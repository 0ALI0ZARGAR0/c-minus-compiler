
grammar CMinus;

// Parser rules
program: declaration_list;

declaration_list: declaration declaration_list | ;

declaration: declaration_initial declaration_prime;

declaration_initial: type_specifier ID;

declaration_prime: fun_declaration_prime | var_declaration_prime;

var_declaration_prime: ';' | '[' NUM ']' ';';

fun_declaration_prime: '(' params ')' compound_stmt;

type_specifier: INT | VOID;

params: INT ID param_prime param_list | VOID;

param_list: ',' param param_list | ;

param: declaration_initial param_prime;

param_prime: '[' ']' | ;

compound_stmt: '{' declaration_list statement_list '}';

statement_list: statement statement_list | ;

statement: expression_stmt | compound_stmt | selection_stmt | iteration_stmt | return_stmt;

expression_stmt: expression ';' | BREAK ';' | ';';

// Standard C-style if-else (no endif!)
selection_stmt: IF '(' expression ')' statement else_stmt;

else_stmt: | ELSE statement;

iteration_stmt: REPEAT statement UNTIL '(' expression ')' | WHILE '(' expression ')' statement;

return_stmt: RETURN return_stmt_prime;

return_stmt_prime: ';' | expression ';';

expression: simple_expression_zegond | ID b;

b: '=' expression | '[' expression ']' h | simple_expression_prime;

h: '=' expression | g d c;

simple_expression_zegond: additive_expression_zegond c;

simple_expression_prime: additive_expression_prime c;

c: relop additive_expression | ;

relop: '<' | '==';

additive_expression: term d;

additive_expression_prime: term_prime d;

additive_expression_zegond: term_zegond d;

d: addop term d | ;

addop: '+' | '-';

term: factor g;

term_prime: factor_prime g;

term_zegond: factor_zegond g;

g: '*' factor g | ;

factor: '(' expression ')' | ID var_call_prime | NUM;

var_call_prime: '(' args ')' | var_prime;

var_prime: '[' expression ']' | ;

factor_prime: '(' args ')' | ;

factor_zegond: '(' expression ')' | NUM;

args: arg_list | ;

arg_list: expression arg_list_prime;

arg_list_prime: ',' expression arg_list_prime | ;

// Lexer rules
IF: 'if';
ELSE: 'else';
VOID: 'void';
INT: 'int';
REPEAT: 'repeat';
WHILE: 'while';
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

WS: [ \t\r\n\u000B\u000C]+ -> skip;
