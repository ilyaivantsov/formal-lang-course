## Examples
``` haskell
g1 := load "wine"; // Загрузить граф

l2 := l1 | l2;   // Объединение языков

l2 := ("a" | l1)*;  // Замыкание

s := starts of g1; // Множество стартовых состояний

// Вывод
print s;
print g1;

// Lambda
res := map s by v => v;
res := map s by (a,b,c) => c;
```
