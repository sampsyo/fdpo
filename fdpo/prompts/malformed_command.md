Error when parsing command:

> {{error}}

In a valid command, the first line is operation to perform, and the remaining
lines are a program. For example, use this:

```
eval foo=2
in foo: 4;
out bar: 4;
bar = shr[4](foo, 4d1);
```

to run the above program with the input value 2.

Enter a new command:
