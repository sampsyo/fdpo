Here is a program written in a simple language for specifying combinational
hardware logic:

```
{{prog}}
```

In this language, the `in` and `out` lines define the input/output *ports*
along with their bit widths. So the line `in foo: 4` means that there is an
input named `foo` consisting of 4 bits. The assignments below these lines
describe bit-vector operations. For example, this line:

```
sum = add[4](left, right);
```

expresses the 4-bit addition of 4-bit signals `left` and `right`. For this
assignment to be valid, `left` and `right` must already be declared as `in`
ports, `sum` must be declared as an `out` port, and all of them must be
declared to have 4 bits. The order of assignments does not matter.

We want to determine the correct values for all the output ports, given values
for the input ports. Here are the input port values, written as decimal
integers:

```
{{invals}}
```

Please write the corresponding values of the output ports. Write each port
on its own line, using the format `portname = value`. Do not write any other
text; just list the values.
