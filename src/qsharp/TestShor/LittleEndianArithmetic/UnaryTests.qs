namespace Quantum.TestShor {
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Diagnostics;
    open FastShor;
    
    operation LetUnary_Test () : Unit {
        using (qs = Qubit[3*2]) {
            let binary = LittleEndian(qs[0..2]);
            InitDual(qs);
            using (unary = Qubit[8]) {
                LetUnary(LittleEndian(unary), binary);

                // Uncompute with full control.
                for (i in 0..Length(unary)-1) {
                    XorEqualConst(binary, ~~~i);
                    Controlled X(binary!, unary[i]);
                    XorEqualConst(binary, ~~~i);
                }
            }
            UncomputeDual(qs);
        }
    }

    operation DelUnary_Test () : Unit {
        using (qs = Qubit[3*2]) {
            let binary = LittleEndian(qs[0..2]);
            InitDual(qs);
            using (unary_reg = Qubit[8]) {
                let unary = LittleEndian(unary_reg);
                LetUnary(unary, binary);
                DelUnary(unary, binary);
            }
            UncomputeDual(qs);
        }
    }
}
