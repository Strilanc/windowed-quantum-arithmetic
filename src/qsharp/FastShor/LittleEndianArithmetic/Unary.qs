namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;

    /// # Summary
    /// Performs 'a := 1 <<< b' where 'a' and 'b' are little-endian quantum registers.
    ///
    /// # Input
    /// ## lvalue
    /// The target of the initialization. The 'a' in 'a := 1 <<< b'.
    /// ## binary
    /// The 'b' in 'a := 1 <<< b'.
    operation LetUnary (lvalue: LittleEndian, binary: LittleEndian) : Unit {
        body (...) {
            Controlled LetUnary(new Qubit[0], (lvalue, binary));
        }
        adjoint auto;
        controlled (cs, ...) {
            if (Length(lvalue!) != 1 <<< Length(binary!)) {
                fail "Length(lvalue!) != 1 <<< Length(binary!)";
            }
    
            Controlled Toggle(cs, lvalue![0]);
            for (i in 0..Length(binary!)-1) {
                let q = binary![i];
                let s = 1 <<< i;
                for (j in 0..s-1) {
                    let a = lvalue![j];
                    let b = lvalue![j + s];
                    Controlled InitToggle([q, a], b);
                    CNOT(b, a);
                }
            }
        }
        controlled adjoint auto;
    }

    /// # Summary
    /// Uncomputes a register initialized using 'a := 1 <<< b',
    /// where 'a' and 'b' are little-endian quantum registers.
    ///
    /// # Input
    /// ## lvalue
    /// The target of the initialization. The 'a' from 'a := 1 <<< b'.
    /// ## binary
    /// The 'b' from 'a := 1 <<< b'.
    operation DelUnary (lvalue: LittleEndian, binary: LittleEndian) : Unit {
        body (...) {
            Adjoint LetUnary(lvalue, binary);
        }
        adjoint auto;
        controlled auto;
        controlled adjoint auto;
    }
}
