{% include "overview.md" %}

For example, consider this program:

```
in left: 32;
in right: 32;
out res: 32;
res = or[32](left, 32d0);
```

To optimize this program, we could recognize that the `or` operation is
redundant because the second argument is all zeroes. So we could write this
equivalent, cheaper program instead:

```
in left: 32;
in right: 32;
out res: 32;
res = left;
```

{% include "opt_overview.md" %}

Your goal is to write a cheaper version of the above program that produces
identical outputs on every input. Please write your optimized version:
