namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    
    /// # Summary
    /// A little endian register storing a superposition of the form
    ///
    ///     sum_m |k + (m+d)N>
    ///
    /// where k is the stored modular integer, N is the modulus, d is the 'deviation' of the
    /// representation, and the sum is over enough terms that the deviations that will be
    /// accumulated during a computation are negligible (i.e. adding multiples of N is
    /// approximately a no-op).
    ///
    /// The coset representation allows modular arithmetic to be performed (approximately)
    /// by integer arithmetic circuits, as long as care is taken to avoid accumulating
    /// too much deviation.
    ///
    /// Operations that act on coset registers will also work on little endian registers, i.e.
    /// they will typically produce values with the correct remainder (mod N). However, the
    /// result will be offset by multiples of the modulus and the exact multiple will be
    /// entangled with other involved registers. The result will be correct unless the offset
    /// causes the register to overflow or underflow.
    newtype CosetLittleEndian = LittleEndian;

    /// # Summary
    /// Performs 'a := k (mod N)' where 'a' is a quantum coset register,
    /// 'k' is a classical constant, and 'N' is a classical constant modulus.
    ///
    /// Initializes 'a' into the state 'sum_m |k + mN>'.
    ///
    /// # Input
    /// ## lvalue
    /// The qubits to initialize into a coset register. The 'a' in 'a := k (mod N)'.
    /// ## remainder
    /// The initial value to assign to the register. The 'k' in 'a := k (mod N)'.
    /// ## modulus
    /// Arithmetic is being done modulo this value. The 'N' in 'a := k (mod N)'.
    operation CosetInit (dst: Qubit[], val: Int, modulus: Int) : CosetLittleEndian {
        let n = CeilLg2(modulus);
        if (Length(dst) < n) {
            fail "Length(dst) < CeilLg2(modulus)";
        }

        // Initialize to desired remainder.
        let d = LittleEndian(dst);
        ResetAll(dst);
        XorEqualConst(d, val);

        // Add in a coherent superposition of multiples of N.
        for (i in n..Length(dst)-1) {
            using (q = Qubit()) {
                LetPlus(q);
                let c = modulus <<< (i - n);
                let relevant = LittleEndian(dst[0..i]);
                Controlled PlusEqualConst([q], (relevant, c));
                if (DelMeasurePlus(q)) {
                    PhaseNegateLessThanConst(relevant, c);
                }
            }
        }

        return CosetLittleEndian(d);
    }
}
