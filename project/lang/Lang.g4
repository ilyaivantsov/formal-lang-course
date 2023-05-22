//antlr4  Lang.g4 -Dlanguage=Python3 -visitor -o dist
grammar Lang;

program: (statements+=statement ';')* EOF;

statement: bind | print;

bind: pattern ':=' expr # BindStatement;
print: 'print' expr     # PrintStatement;

lambda: pat=pattern '=>' body=expr;
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
    | ('map'|'filter') expr 'by' lam=lambda                             # MapOrFilterExpr
    | 'load' expr                                                       # LoadExpr
	| expr '&' expr                                                     # IntersectionExpr
	| expr '|' expr                                                     # JoinExpr
	| expr '++' expr                                                    # ConcatExpr
	| expr '*'                                                          # ClosurExpr
	| ('starts'| 'finals' | 'labels' | 'edges') 'of' expr               # InfoExpr
    ;

COMMENT: ('//' ~[\n]* | '/*' .*? '*/') -> skip;
WS: [ \t\n\r]+ -> skip;
INT: [1-9][0-9]*|'0';
IDENT: [a-zA-Z_][a-zA-Z_0-9]*;
STRING: '"' (~["\\] | '\\' ["\\tvbn])* '"';
