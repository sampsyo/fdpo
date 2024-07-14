{% include "overview.md" %}

Our goal is to start with a given program and obtain an equivalent but
"smaller" program, i.e., one that uses fewer or smaller function calls.
I have a cost model that assigns a numeric score to each function call,
and the goal is to minimize the total score of the program. But the most
important thing is that the new program behaves identically to the old program
on all inputs.

To search for a good optimized program, you can explore several options by
issuing *commands*. The commands available to you are:

* `check`: Check if a proposed program is equivalent to the original program.
  If it is not, this command will report a concrete counter-example that
  reveals the difference.
* `eval [VAR=VALUE ...]`: Evaluate a specified program with the given values
  for the input ports, and print the values of the output ports. You can use
  this command to test the behavior of a program.
* `cost`: Compute the cost of a proposed program according to my cost model.
* `commit`: Propose the given program as the new optimized program. This
  command will fail if the program is not equivalent to the original program,
  or if the cost is not smaller than the original.

To run a command, format it like this:

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
{{ prog.pretty() }}
```

The cost of this program, according to my cost model, is {{ prog | score }}.

From here on, you are a programmer interacting with a terminal that interprets
commands as illustrated above. You will enter commands, and I will respond
with the outputs of those commands.

Enter your first command:
