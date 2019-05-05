namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    
    /// # Summary
    /// Performs 'a *= k**b (mod N)' where 'a' is a quantum coset register,
    /// 'b' is a quantum little endian register,
    /// 'k' is a classical constant, and 'N' is a classical constant modulus.
    ///
    /// Increases the magnitude of the deviation in 'lvalue' and 'workspace' by
    /// O(len(b)*n/log(n)) where n = lg(N).
    ///
    /// # Input
    /// ## lvalue
    /// The target of the multiplication. The 'a' in 'a *= k**b (mod N)'.
    /// ## generator
    /// The constant factor being raised to a power and then multiplied into the target.
    /// The 'k' in 'a *= k**b (mod N)'.
    /// ## exponent
    /// The power to raise the constant factor to before multiplying into the target.
    /// The 'b' in 'a *= k**b (mod N)'.
    /// ## modulus
    /// Arithmetic is being done modulo this value. The 'N' in 'a *= k**b (mod N)'.
    /// ## workspace
    /// A coset register initialized to 0.
    operation TimesEqualConstRaisedToExponentMod_Coset (lvalue: CosetLittleEndian,
                                                        generator: Int, 
                                                        exponent: LittleEndian, 
                                                        modulus: Int,
                                                        workspace: CosetLittleEndian) : Unit {
        body (...) {
            for (i in 0..Length(exponent!)-1) {
                let factor = SquarePow(generator, i, modulus);
                Controlled TimesEqualConst_Coset([exponent![i]], (lvalue, factor, modulus, workspace));
            }
        }
        adjoint auto;
    }
}
