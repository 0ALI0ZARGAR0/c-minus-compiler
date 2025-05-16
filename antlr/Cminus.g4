grammar Cminus;

// Parser Rules
program : declaration+ ;

declaration
    : var_declaration
    | fun_declaration
    ;

var_declaration
    : type_specifier ID ';'
    | type_specifier ID '[' NUM ']' ';'
    ;

type_specifier
    : 'int'
    | 'void'
    ;

fun_declaration
    : type_specifier ID '(' params ')' compound_stmt ;

params
    : param_list
    | 'void'
    ;

param_list
    : param (',' param)* ;

param
    : type_specifier ID
    | type_specifier ID '[' ']'
    ;

compound_stmt
    : '{' local_declarations statement_list '}' ;

local_declarations
    : var_declaration*
    ;

statement_list
    : statement* ;

statement
    : expression_stmt
    | compound_stmt
    | selection_stmt
    | iteration_stmt
    | return_stmt
    | break_stmt
    ;

expression_stmt
    : expression ';'
    | ';'
    ;

selection_stmt
    : 'if' '(' expression ')' statement ('else' statement)? ;

iteration_stmt
    : 'repeat' statement 'until' '(' expression ')' ';' ;

return_stmt
    : 'return' ';'
    | 'return' expression ';'
    ;

break_stmt
    : 'break' ';' ;

expression
    : var '=' expression
    | simple_expression
    ;

var
    : ID
    | ID '[' expression ']'
    ;

simple_expression
    : additive_expression relop additive_expression
    | additive_expression
    ;

relop
    : '<'
    | '<='
    | '>'
    | '>='
    | '=='
    | '!='
    ;

additive_expression
    : additive_expression addop term
    | term
    ;

addop
    : '+'
    | '-'
    ;

term
    : term mulop factor
    | factor
    ;

mulop
    : '*'
    ;

factor
    : '(' expression ')'
    | var
    | call
    | NUM
    ;

call
    : ID '(' args ')' ;

args
    : arg_list
    |
    ;

arg_list
    : expression (',' expression)* ;

// Lexer Rules
ID  : [a-zA-Z]+ [a-zA-Z0-9]* ;
NUM : [0-9]+ ;

KEYWORD : 'if' | 'else' | 'void' | 'int' | 'repeat' | 'break' | 'until' | 'return' ;

SYMBOL : ';' | ',' | '[' | ']' | '(' | ')' | '{' | '}' | '+' | '-' | '*' | '/' | '<' | '<=' | '>' | '>=' | '==' | '!=' | '=' ;

COMMENT : '/*' .*? '*/' -> skip ;
LINE_COMMENT : '//' .*? ('\r'? '\n' | EOF) -> skip ;

WS : [ \t\r\n\f]+ -> skip ;

ERROR : . ;
