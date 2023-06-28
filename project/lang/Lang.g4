//antlr4  Lang.g4 -Dlanguage=Python3 -visitor -o dist
grammar Lang;

program: (statements+=statement ';')* EOF;

statement: bind | print;

bind: var ':=' expr             # BindStatement;
print: 'print' '(' expr ')'     # PrintStatement;

lambda: var '=>' body=expr;

var: IDENT;
val:
    INT               # ValInt
    | STRING          # ValStr
    | setLiteral      # ValSet
    ;

setLiteral:
	'{' '}'                            # EmptySet
	| '{' setElem (',' setElem)* '}'   # FillSet
	;

setElem: INT                           # FillSetInt
         | INT '..' INT                # FillSetRange
         ;

expr:
	'(' expr ')'                                                                 # ParenExpr
	| var                                                                        # VarExpr
	| val                                                                        # ValExpr
    | ('map'|'filter') expr 'by' lam=lambda                                      # MapOrFilterExpr
    | 'load' expr                                                                # LoadExpr
	| expr '&' expr                                                              # IntersectionExpr
	| expr '|' expr                                                              # JoinExpr
	| expr '++' expr                                                             # ConcatExpr
	| expr '*'                                                                   # ClosurExpr
	| expr ('=' | '<' | '<=' | '>=' | '>' ) expr                                 # EqExpr
	| ('starts' | 'finals' | 'labels' | 'edges') 'of' expr                       # InfoExpr
	| ('set final' | 'add final' | 'set start' | 'add start') expr 'to' expr     # ModifyExpr
    ;

COMMENT: ('//' ~[\n]* | '/*' .*? '*/') -> skip;
WS: [ \t\n\r]+ -> skip;
INT: [1-9][0-9]*|'0';
IDENT: [a-zA-Z_][a-zA-Z_0-9]*;
STRING: '"' (~["\\] | '\\' ["\\tvbn])* '"';
