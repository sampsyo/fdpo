# ARGS: x=13
in x: 8;
out c: 4;
b1: 4 = zext[1, 4](slice[8, 0, 0](x));
b2: 4 = zext[1, 4](slice[8, 1, 1](x));
b3: 4 = zext[1, 4](slice[8, 2, 2](x));
b4: 4 = zext[1, 4](slice[8, 3, 3](x));
b5: 4 = zext[1, 4](slice[8, 4, 4](x));
b6: 4 = zext[1, 4](slice[8, 5, 5](x));
b7: 4 = zext[1, 4](slice[8, 6, 6](x));
b8: 4 = zext[1, 4](slice[8, 7, 7](x));
c =
  add[4](b1,
  add[4](b2,
  add[4](b3,
  add[4](b4,
  add[4](b5,
  add[4](b6,
  add[4](b7,
         b8)))))));
