Error when parsing command:

> {{error}}

Remember, commands must be fenced in triple-backtick Markdown code blocks.
The first line is operation to perform, and the remaining lines are a program.
For example, use this:

```
check
in foo: 4;
out bar: 4;
bar = shr[4](4, 4d1);
```

to check whether that short program is equivalent to our original program.
