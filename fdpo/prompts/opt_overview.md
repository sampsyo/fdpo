Our goal is to start with a given program and obtain an equivalent but
"smaller" program, i.e., one that uses fewer or smaller function calls.
I have a cost model that assigns a numeric score to each function call,
and the goal is to minimize the total score of the program. But the most
important thing is that the new program behaves identically to the old program
on all inputs.

Here is the program we want to optimize:

```
{{ prog.pretty() }}
```

The cost of this program, according to my cost model, is {{ prog | score }}.
