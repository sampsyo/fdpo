# ARGS: x=12 y=100 z=45
in x: 32;
in y: 32;
in z: 32;
out max: 32;
max = mux[32](gt[32](x, y),
    mux[32](gt[32](x, z), x, z),
    mux[32](gt[32](y, z), y, z)
);
