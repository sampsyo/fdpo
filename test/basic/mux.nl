# ARGS: sel=1 left=4 right=10
in sel: 1;
in left: 32;
in right: 32;
out res: 32;
res = if[32](sel, left, right);
