namespace WindowedArithmetic {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Extensions.Convert;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;

    operation PlusEqualConstTimesLE (lvalue: LittleEndian,
                                     classical_factor: BigInt,
                                     quantum_factor: LittleEndian) : Unit {
        body (...) {
            let bs = BigIntToBools(classical_factor);
            for (i in 0..Min(Length(lvalue!), Length(bs))-1) {
                if (bs[i]) {
                    PlusEqual(SkipLE(lvalue, i), quantum_factor);
                }
            }
        }
        adjoint auto;
    }
}
