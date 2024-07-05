We are working in  a simple language for specifying combinational hardware
logic. Here is an example of a program in this language, just to demonstrate
the language (this is not the program we want to analyze here):

```
in left: 4;
in right: 4;
out sum: 4;
out decr: 4;
sum = add[4](left, right);
decr = sub[4](left, 4d1);
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

Integer literals in this language are written like `4d1`, where `4` is the
bit width, `d` is the base (decimal), and `1` is the value. The language
supports binary (`d`), decimal (`d`), and hexadecimal (`x`) literals. So, for
example, `32x1B` is the 32-bit value 27.

The language does not have infix operators like `+`. The only thing you can
do in expressions is call functions, like `add[4]`. Functions like this are
parameterized by the bit widths they operate on, written in square brackets.
