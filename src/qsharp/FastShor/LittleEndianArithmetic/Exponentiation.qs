namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    
    /// # Summary
    /// Measures 'k**a (mod N)' where 'a' is a quantum little endian register,
    /// 'k' is a classical constant, and 'N' is a classical constant modulus.
    ///
    /// This is the measurement performed by Shor's algorithm before it performs
    /// a QFT on the exponent (when not using adaptive phase estimation).
    ///
    /// # Input
    /// ## generator
    /// The constant factor being raised to a power.
    /// The 'k' in 'measure k**a % N'.
    /// ## exponent
    /// The power to raise the constant factor to.
    /// The 'a' in 'measure k**a % N'.
    /// ## modulus
    /// Arithmetic is being done modulo this value.
    /// The 'N' in 'measure k**a % N'.
    operation MeasureConstRaisedToExponentMod (generator: Int,
                                               exponent: LittleEndian, 
                                               modulus: Int) : Int {
        let n = CeilLg2(modulus);
        let m = CosetRegisterLengthForPeriodFinding(CeilLg2(modulus), 1000);
        let zero = (1 <<< m) / (2 * modulus) * modulus;
        mutable result = 0;
        using (a_reg = Qubit[m]) {
            let a = LittleEndian(a_reg);
            let ac = CosetLittleEndian(a);
            LetConst(a, zero + 1);
            using (b_reg = Qubit[m]) {
                let b = LittleEndian(b_reg);
                let bc = CosetLittleEndian(b);
                LetConst(b, zero);

                TimesEqualConstRaisedToExponentMod_Coset(ac, generator, exponent, modulus, bc);
                set result = MeasureRemainder(a, modulus);
                Adjoint TimesEqualConstRaisedToExponentMod_Coset(ac, generator, exponent, modulus, bc);

                DelConst(b, zero);
            }
            DelConst(a, zero + 1);
        }
        return result;
    }
}
