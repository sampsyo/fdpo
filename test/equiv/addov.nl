in left: 16;
in right: 16;
out sum: 16;
out carry: 1;
sum = add[16](left, right);
carry = or[1](lt[16](sum, left), lt[16](sum, right));
---
fullsum: 17 = add[17](zext[16, 17](left), zext[16, 17](right));
sum = slice[17, 0, 15](fullsum);
carry = slice[17, 16, 16](fullsum);
