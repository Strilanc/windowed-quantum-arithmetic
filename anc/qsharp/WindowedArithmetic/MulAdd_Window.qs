namespace WindowedArithmetic {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Extensions.Convert;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;

    function MultiplicationTable(factor: BigInt, length: Int) : BigInt[] {
        mutable table = new BigInt[length];
        for (i in 0..Length(table)-1) {
            set table[i] = ToBigInt(i)*factor;
        }
        return table;
    }

    operation PlusEqualConstTimesLEWindowed (lvalue: LittleEndian,
                                             classical_factor: BigInt,
                                             quantum_factor: LittleEndian,
                                             window: Int) : Unit {
        body (...) {
            let table = MultiplicationTable(classical_factor, 1 <<< window);
            for (i in 0..window..Length(quantum_factor!)-1) {
                let w = SliceLE(quantum_factor, i, i+window);
                let t = SkipLE(lvalue, i);
                PlusEqualLookup(t, table, w);
            }
        }
        adjoint auto;
    }
}
