# ARGS: x=13
in x: 8;
out c: 4;
c =
add[4](zext[1, 4](slice[8, 0, 0](x)),
add[4](zext[1, 4](slice[8, 1, 1](x)),
add[4](zext[1, 4](slice[8, 2, 2](x)),
add[4](zext[1, 4](slice[8, 3, 3](x)),
add[4](zext[1, 4](slice[8, 4, 4](x)),
add[4](zext[1, 4](slice[8, 5, 5](x)),
add[4](zext[1, 4](slice[8, 6, 6](x)),
       zext[1, 4](slice[8, 7, 7](x)))))))));