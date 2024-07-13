{% include "overview.md" %}

Our goal is to start with a given program and obtain an equivalent but
"smaller" program, i.e., one that uses fewer or smaller function calls, or one
with shallower chains of functions. But the most important thing is that the
new program behaves identically to the old program on all inputs.

To search for a good optimized program, you can explore several options by
issuing *commands*. The commands available to you are:

* `check`: Check if a proposed program is equivalent to the original program.
  If it is equivalent, we have reached the goal and we are done. If it is not,
  this command will report a concrete counter-example that reveals the
  difference.
* `eval [VAR=VALUE ...]`: Evaluate a specified program with the given values
  for the input ports, and print the values of the output ports. You can use
  this command to test the behavior of a program.

To run a command, format it like this (including the backticks):

```
commmand
program
```

So, for example, to evaluate a simple program with input values 1 and 2, you
would write:

```
eval x=1 y=2
in x: 4;
in y: 4;
out res: 4;
res = or[4](x, y);
```

Here is the program we want to optimize:

```
{{prog}}
```

Please type your first command. Do not include any other code; just write the
command (`check` or `eval`) you want to run and the program you want to run it
on.
