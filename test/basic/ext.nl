# ARGS: x=9
in x: 4;
out s: 8;
out z: 8;
s = sext[4, 8](x);
z = zext[4, 8](x);
