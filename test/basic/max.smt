(let ((.def_0 (bvult z y))) (let ((.def_1 (ite .def_0 #b1 #b0))) (let ((.def_2 (= .def_1 #b0))) (let ((.def_3 (not .def_2))) (let ((.def_4 (ite .def_3 y z))) (let ((.def_5 (bvult z x))) (let ((.def_6 (ite .def_5 #b1 #b0))) (let ((.def_7 (= .def_6 #b0))) (let ((.def_8 (not .def_7))) (let ((.def_9 (ite .def_8 x z))) (let ((.def_10 (bvult y x))) (let ((.def_11 (ite .def_10 #b1 #b0))) (let ((.def_12 (= .def_11 #b0))) (let ((.def_13 (not .def_12))) (let ((.def_14 (ite .def_13 .def_9 .def_4))) (let ((.def_15 (= max .def_14))) .def_15))))))))))))))))
