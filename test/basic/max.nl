# ARGS: x=12 y=100 z=91
in x: 32;
in y: 32;
in z: 32;
out max: 32;
max = if[32](gt[32](x, y),
    if[32](gt[32](x, z), x, z),
    if[32](gt[32](y, z), y, z),
);
