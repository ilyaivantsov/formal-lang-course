## Examples
``` haskell
g1 <- load "wine";
s <- starts of g1;
g2 <- filter (map g1 : (u, v, d) => v) : v => v | s;
print finals of g2;
```
