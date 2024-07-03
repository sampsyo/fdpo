We are working in  a simple language for specifying combinational hardware
logic. Here is an example of a program in this language, just to demonstrate
the language (this is not the program we want to analyze here):

```
in left: 4;
in right: 4;
out sum: 4;
out diff: 4;
sum = add[4](left, right);
diff = sub[4](left, right);
```

In this language, the `in` and `out` lines define the input/output *ports*
along with their bit widths. So the line `in left: 4` means that there is an
input named `left` consisting of 4 bits. The assignments below these lines
describe bit-vector operations. For example, this line:

```
sum = add[4](left, right);
```

expresses the 4-bit addition of 4-bit signals `left` and `right`. For this
assignment to be valid, `left` and `right` must already be declared as `in`
ports, `sum` must be declared as an `out` port, and all of them must be
declared to have 4 bits. The order of assignments does not matter.
