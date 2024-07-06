# ARGS: x=9
in x: 4;
out s: 8;
out z: 8;
out e: 2;
s = sext[4, 8](x);
z = zext[4, 8](x);
e = slice[4, 2, 3](x);
