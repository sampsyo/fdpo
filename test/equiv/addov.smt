(let ((.def_0 (= prog1_carry prog2_carry))) (let ((.def_1 (not .def_0))) (let ((.def_2 (= prog1_sum prog2_sum))) (let ((.def_3 (not .def_2))) (let ((.def_4 (or .def_3 .def_1))) (let ((.def_5 (= prog1_right prog2_right))) (let ((.def_6 (= prog1_left prog2_left))) (let ((.def_7 (and .def_6 .def_5))) (let ((.def_8 ((_ extract 16 16) prog2_fullsum))) (let ((.def_9 (= prog2_carry .def_8))) (let ((.def_10 ((_ extract 15 0) prog2_fullsum))) (let ((.def_11 (= prog2_sum .def_10))) (let ((.def_12 ((_ zero_extend 1) prog2_right))) (let ((.def_13 ((_ zero_extend 1) prog2_left))) (let ((.def_14 (bvadd .def_13 .def_12))) (let ((.def_15 (= prog2_fullsum .def_14))) (let ((.def_16 (and .def_15 .def_11 .def_9))) (let ((.def_17 (bvult prog1_sum prog1_right))) (let ((.def_18 (ite .def_17 #b1 #b0))) (let ((.def_19 (bvult prog1_sum prog1_left))) (let ((.def_20 (ite .def_19 #b1 #b0))) (let ((.def_21 (bvor .def_20 .def_18))) (let ((.def_22 (= prog1_carry .def_21))) (let ((.def_23 (bvadd prog1_left prog1_right))) (let ((.def_24 (= prog1_sum .def_23))) (let ((.def_25 (and .def_24 .def_22))) (let ((.def_26 (and .def_25 .def_16 .def_7 .def_4))) .def_26)))))))))))))))))))))))))))
