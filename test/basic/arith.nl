# ARGS: left=42 right=5
in left: 32;
in right: 32;
out a: 32;
out s: 32;
out m: 32;
out d: 32;
out r: 32;
a = add[32](left, right);
s = sub[32](left, right);
m = mul[32](left, right);
d = div[32](left, right);
r = mod[32](left, right);
