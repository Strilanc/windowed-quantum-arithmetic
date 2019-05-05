namespace Quantum.TestShor {
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Diagnostics;
    open FastShor;
    
    operation MeasureRemainder_Test () : Unit {
        using (qs = Qubit[8]) {
            for (q in qs) {
                H(q);
            }
            let r = MeasureRemainder(LittleEndian(qs), 8);
            for (i in 0..7) {
                mutable p = 0.5;
                if (i < 3) {
                    if (((r >>> i) &&& 1) != 0) {
                        set p = 1.0;
                    } else {
                        set p = 0.0;
                    }
                }
                AssertProb([PauliZ], [qs[i]], One, p, "", 1e-5);
            }
            let _ = MeasureInteger(LittleEndian(qs));
        }
    }
}
