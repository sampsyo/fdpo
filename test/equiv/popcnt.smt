(let ((.def_0 (= prog1_c prog2_c))) (let ((.def_1 (not .def_0))) (let ((.def_2 (= prog1_x prog2_x))) (let ((.def_3 ((_ extract 3 0) prog2_t3))) (let ((.def_4 (= prog2_c .def_3))) (let ((.def_5 (bvlshr prog2_t2 #b00000100))) (let ((.def_6 (bvand .def_5 prog2_m3))) (let ((.def_7 (bvand prog2_t2 prog2_m3))) (let ((.def_8 (bvadd .def_7 .def_6))) (let ((.def_9 (= prog2_t3 .def_8))) (let ((.def_10 (= prog2_m3 #b00001111))) (let ((.def_11 (bvlshr prog2_t1 #b00000010))) (let ((.def_12 (bvand .def_11 prog2_m2))) (let ((.def_13 (bvand prog2_t1 prog2_m2))) (let ((.def_14 (bvadd .def_13 .def_12))) (let ((.def_15 (= prog2_t2 .def_14))) (let ((.def_16 (= prog2_m2 #b00110011))) (let ((.def_17 (bvlshr prog2_x #b00000001))) (let ((.def_18 (bvand .def_17 prog2_m1))) (let ((.def_19 (bvand prog2_x prog2_m1))) (let ((.def_20 (bvadd .def_19 .def_18))) (let ((.def_21 (= prog2_t1 .def_20))) (let ((.def_22 (= prog2_m1 #b01010101))) (let ((.def_23 (and .def_22 .def_21 .def_16 .def_15 .def_10 .def_9 .def_4))) (let ((.def_24 (bvadd prog1_b7 prog1_b8))) (let ((.def_25 (bvadd prog1_b6 .def_24))) (let ((.def_26 (bvadd prog1_b5 .def_25))) (let ((.def_27 (bvadd prog1_b4 .def_26))) (let ((.def_28 (bvadd prog1_b3 .def_27))) (let ((.def_29 (bvadd prog1_b2 .def_28))) (let ((.def_30 (bvadd prog1_b1 .def_29))) (let ((.def_31 (= prog1_c .def_30))) (let ((.def_32 ((_ extract 7 7) prog1_x))) (let ((.def_33 ((_ zero_extend 3) .def_32))) (let ((.def_34 (= prog1_b8 .def_33))) (let ((.def_35 ((_ extract 6 6) prog1_x))) (let ((.def_36 ((_ zero_extend 3) .def_35))) (let ((.def_37 (= prog1_b7 .def_36))) (let ((.def_38 ((_ extract 5 5) prog1_x))) (let ((.def_39 ((_ zero_extend 3) .def_38))) (let ((.def_40 (= prog1_b6 .def_39))) (let ((.def_41 ((_ extract 4 4) prog1_x))) (let ((.def_42 ((_ zero_extend 3) .def_41))) (let ((.def_43 (= prog1_b5 .def_42))) (let ((.def_44 ((_ extract 3 3) prog1_x))) (let ((.def_45 ((_ zero_extend 3) .def_44))) (let ((.def_46 (= prog1_b4 .def_45))) (let ((.def_47 ((_ extract 2 2) prog1_x))) (let ((.def_48 ((_ zero_extend 3) .def_47))) (let ((.def_49 (= prog1_b3 .def_48))) (let ((.def_50 ((_ extract 1 1) prog1_x))) (let ((.def_51 ((_ zero_extend 3) .def_50))) (let ((.def_52 (= prog1_b2 .def_51))) (let ((.def_53 ((_ extract 0 0) prog1_x))) (let ((.def_54 ((_ zero_extend 3) .def_53))) (let ((.def_55 (= prog1_b1 .def_54))) (let ((.def_56 (and .def_55 .def_52 .def_49 .def_46 .def_43 .def_40 .def_37 .def_34 .def_31))) (let ((.def_57 (and .def_56 .def_23 .def_2 .def_1))) .def_57))))))))))))))))))))))))))))))))))))))))))))))))))))))))))