namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    
    /// # Summary
    /// Measures the remainder 'a % N' without measuring the quotient 'a // N', where 'a'
    /// is a little endian quantum register and 'N' is a classical constant modulus.
    ///
    /// Note:
    /// This operation is not used in the efficient period finding algorithm.
    /// It has not been optimized.
    ///
    /// # Input
    /// ## target
    /// The 'a' in 'measure a % N'.
    /// ## modulus
    /// The 'N' in 'measure a % N'.
    operation MeasureRemainder (target: LittleEndian, modulus: Int) : Int {
        let n = CeilLg2(modulus);
        mutable res = 0;
        using (t_reg = Qubit[n]) {
            let t = LittleEndian(t_reg);

            // Perform 't += (target % N)'.
            for (i in 0..Length(target!)-1) {
                Controlled ModularIncrementLE([target![i]], ((1 <<< i) % modulus, modulus, t));
            }

            set res = MeasureInteger(t);
        }
        return res;
    }
}
