# ARGS: x=3 y=7
in x: 8;
in y: 8;
out a: 8;
out o: 8;
out xo: 8;
out left: 8;
out right: 8;
out logic: 8;
out arith: 8;
a = and[8](x, y);
o = or[8](x, y);
xo = xor[8](x, y);
left = shl[8](x, 8d1);
right = shr[8](x, 8d1);
logic = shr[8](8b10000000, 8d1);
arith = ashr[8](8b10000000, 8d1);
