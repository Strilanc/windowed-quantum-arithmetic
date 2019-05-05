namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Math;
    open Microsoft.Quantum.Extensions.Convert;
        
    /// # Summary
    /// Performs 'a += b*k (mod N)' where 'a' and 'b' are quantum coset registers,
    /// 'k' is a classical constant, and 'N' is a classical constant modulus.
    ///
    /// Increases the deviation in the lvalue register by at most O(m / lg(m)) where m = Length(offset).
    ///
    /// # Input
    /// ## lvalue
    /// The target of the addition. The 'a' in 'a += b*k (mod N)'.
    /// ## offset
    /// The quantum part of the product being added into the target. The 'b' in 'a += b*k (mod N)'.
    /// ## constFactor
    /// The classical part of the product being added into the target. The 'k' in 'a += b*k (mod N)'.
    /// ## modulus
    /// Arithmetic is being done modulo this value. The 'N' in 'a += b*k (mod N)'.
    operation PlusEqualTimesConst_Coset (lvalue: CosetLittleEndian,
                                         offset: CosetLittleEndian, 
                                         constFactor: Int, 
                                         modulus: Int) : Unit {
        body (...) {
            Controlled PlusEqualTimesConst_Coset(new Qubit[0], (lvalue, offset, constFactor, modulus));
        }
        adjoint auto;
        controlled (cs, ...) {
            let g = PlusEqualTimesConst_Coset_GroupSize(Length(lvalue!!));
            let m = Length(offset!!);

            for (i in 0..g..m-1) {
                let chunk = LittleEndian(offset!![i..Min(m-1, i+g-1)]);

                // Classically precompute a small multiplication table for this chunk.
                let table = ModularMultiplicationTable(constFactor <<< i, modulus, g);

                // Quantum lookup and add chunk result from table.
                Controlled PlusEqualLookup(cs, (lvalue!, table, chunk));
            }
        }
        controlled adjoint auto;
    }
    
    /// # Summary
    /// Performs 'a -= b*k (mod N)' where 'a' and 'b' are quantum coset registers,
    /// 'k' is a classical constant, and 'N' is a classical constant modulus.
    ///
    /// Increases the deviation in the lvalue register by at most O(m / lg(m)) where m = Length(offset).
    ///
    /// # Input
    /// ## lvalue
    /// The target of the subtraction.
    /// The 'a' in 'a -= b*k (mod N)'.
    /// ## offset
    /// The quantum part of the product being subtracted from the target.
    /// The 'b' in 'a -= b*k (mod N)'.
    /// ## constFactor
    /// The classical part of the product being subtracted from the target.
    /// The 'k' in 'a -= b*k (mod N)'.
    /// ## modulus
    /// Arithmetic is being done modulo this value.
    /// The 'N' in 'a -= b*k (mod N)'.
    operation MinusEqualTimesConst_Coset (lvalue: CosetLittleEndian,
                                          offset: CosetLittleEndian, 
                                          constFactor: Int, 
                                          modulus: Int) : Unit {
        body (...) {
            Adjoint PlusEqualTimesConst_Coset(lvalue, offset, constFactor, modulus);
        }
        adjoint auto;
        controlled auto;
        controlled adjoint auto;
    }

    /// # Summary
    /// Returns [factor * k % modulus for k in range(group_size)]
    function ModularMultiplicationTable(factor: Int, modulus: Int, group_size: Int) : Int[] {
        mutable table = new Int[1 <<< group_size];
        for (j in 0..Length(table) - 1) {
            set table[j] = ProperMod(j * factor, modulus);
        }
        return table;
    }
}
