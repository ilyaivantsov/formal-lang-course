//antlr4  Expr.g4 -Dlanguage=Python3 -visitor -o dist
grammar Lang;

program: (statements+=statement ';')* EOF;

statement: bind | print;

bind: pattern '<-' expr;
print: 'print' expr;

lambda: pattern '=>' expr | '(' lambda ')';
pattern: var | '(' pattern (',' pattern)* ')';

var: IDENT;
val: INT | STRING | setLiteral;
setLiteral:
	'{' '}' // Empty Set
	| '{' setElem (',' setElem)* '}'; // Set
setElem: INT | INT '..' INT;

expr:
	'(' expr ')'                                                        # ParenExpr
	| var                                                               # VarExpr
	| val                                                               # ValExpr
    | ('map'|'filter') expr ':' lambda                                  # MapOrFilterExpr
    | 'load' expr                                                       # LoadExpr
	| expr '&' expr                                                     # IntersectionExpr
	| expr '|' expr                                                     # JoinExpr
	| expr '++' expr                                                    # ConcatExpr
	| ('starts'| 'finals' | 'labels' | 'edges') 'of' expr               # InfoExpr
    ;

COMMENT: ('//' ~[\n]* | '/*' .*? '*/') -> skip;
WS: [ \t\n\r]+ -> skip;
INT: [1-9][0-9]*|'0';
IDENT: [a-zA-Z_][a-zA-Z_0-9]*;
STRING: '"' (~["\\] | '\\' ["\\tvbn])* '"';