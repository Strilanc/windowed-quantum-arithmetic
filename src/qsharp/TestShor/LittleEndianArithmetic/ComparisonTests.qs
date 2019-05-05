namespace Quantum.TestShor {
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Diagnostics;
    open FastShor;
    
    operation XorEqualsLessThan_Test () : Unit {
        let n = 3;
        using (qs = Qubit[n*4]) {
            InitDual(qs);
            let rhs = LittleEndian(qs[0..n-1]);
            let lhs = LittleEndian(qs[n..2*n-1]);
            using (t = Qubit()) {
                XorEqualsLessThan(t, lhs, rhs);

                // Brute force uncompute.
                for (c in 0..(1<<<n)-1) {
                    for (d in 0..(1<<<n)-1) {
                        if (c < d) {
                            XorEqualConst(lhs, ~~~c);
                            XorEqualConst(rhs, ~~~d);
                            Controlled X(lhs! + rhs!, t);
                            XorEqualConst(rhs, ~~~d);
                            XorEqualConst(lhs, ~~~c);
                        }
                    }
                }
            }
            UncomputeDual(qs);
        }
    }
    
    operation XorEqualsLessThanConst_Test () : Unit {
        let n = 3;
        for (rhs in -3..(1<<<n)+2) {
            using (qs = Qubit[n*2]) {
                InitDual(qs);
                let lhs = LittleEndian(qs[0..n-1]);
                using (t = Qubit()) {
                    XorEqualsLessThanConst(t, lhs, rhs);

                    // Brute force uncompute.
                    for (c in 0..(1<<<n)-1) {
                        if (c < rhs) {
                            XorEqualConst(lhs, ~~~c);
                            Controlled X(lhs!, t);
                            XorEqualConst(lhs, ~~~c);
                        }
                    }
                }
                UncomputeDual(qs);
            }
        }
    }
    
    operation PhaseNegateLessThanConst_Test () : Unit {
        for (c in 0..15) {
            using (qs = Qubit[4*2]) {
                InitDual(qs);
                let r = LittleEndian(qs[0..3]);
                PhaseNegateLessThanConst(r, c);
                for (d in 0..c-1) {
                    XorEqualConst(r, ~~~d);
                    Controlled PhaseNegate(r!, ());
                    XorEqualConst(r, ~~~d);
                }
                UncomputeDual(qs);
            }
        }
    }
}
