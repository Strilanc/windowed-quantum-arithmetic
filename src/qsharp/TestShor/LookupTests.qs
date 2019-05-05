namespace Quantum.TestShor {
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Diagnostics;
    open FastShor;
    
    operation Lookup_vs_Multiplex_Test_Helper (lookup: ((LittleEndian, Int[], LittleEndian) => Unit)) : Unit {
        for (n in 0..5) {
            for (m in 1..3) {
                mutable table = new Int[1<<<n];
                for (i in 0..(1<<<n)-1) {
                    set table[i] = RandomInt(1<<<m);
                }

                using (qs = Qubit[(n+m)*2]) {
                    InitDual(qs);
                    let addr = LittleEndian(qs[0..n-1]);
                    let addrBE = BigEndian(qs[n-1..-1..0]);
                    let lvalue = LittleEndian(qs[n..n+m-1]);
            
                    if (n > 0) {
                        mutable ops = new (LittleEndian => Unit : Adjoint, Controlled)[1<<<n];
                        for (i in 0..(1<<<n)-1) {
                            set ops[i] = InPlaceXorLE(table[i], _);
                        }
                        MultiplexOperations(ops, addrBE, lvalue);
                    } else {
                        XorEqualConst(lvalue, table[0]);
                    }
            
                    lookup(lvalue, table, addr);

                    UncomputeDual(qs);
                }
            }
        }
    }

    operation XorEqualLookup_Test () : Unit {
        Lookup_vs_Multiplex_Test_Helper(XorEqualLookup);
    }

    operation LetEqualLookup_Test () : Unit {
        Lookup_vs_Multiplex_Test_Helper(LetLookup);
    }

    operation DelLookup_Test () : Unit {
        for (n in 0..5) {
            for (m in 3..5) {
                mutable table = new Int[1 <<< n];
                for (i in 0..(1<<<n)-1) {
                    set table[i] = RandomInt(1<<<m);
                }

                using (qs = Qubit[n*2]) {
                    InitDual(qs);
                    let addr = LittleEndian(qs[0..n-1]);
                    using (zs = Qubit[m]) {
                        let target = LittleEndian(zs);
                        LetLookup(target, table, addr);
                        DelLookup(target, table, addr);
                    }
                    UncomputeDual(qs);
                }
            }
        }
    }
}
