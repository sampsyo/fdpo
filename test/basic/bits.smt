(let ((.def_0 (bvashr #b10000000 #b00000001))) (let ((.def_1 (= arith .def_0))) (let ((.def_2 (bvlshr #b10000000 #b00000001))) (let ((.def_3 (= logic .def_2))) (let ((.def_4 (bvlshr x #b00000001))) (let ((.def_5 (= right .def_4))) (let ((.def_6 (bvshl x #b00000001))) (let ((.def_7 (= left .def_6))) (let ((.def_8 (bvxor x y))) (let ((.def_9 (= xo .def_8))) (let ((.def_10 (bvor x y))) (let ((.def_11 (= o .def_10))) (let ((.def_12 (bvand x y))) (let ((.def_13 (= a .def_12))) (let ((.def_14 (and .def_13 .def_11 .def_9 .def_7 .def_5 .def_3 .def_1))) .def_14)))))))))))))))
