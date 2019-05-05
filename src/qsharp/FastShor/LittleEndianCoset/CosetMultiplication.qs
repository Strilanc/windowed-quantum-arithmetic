namespace FastShor
{
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    
    /// # Summary
    /// Performs 'a *= k (mod N)' where 'a' is a quantum coset register,
    /// 'k' is a classical constant, and 'N' is a classical constant modulus.
    ///
    /// Increases the deviation in the lvalue and coset_workspace registers by at most
    /// O(m / lg(m)) where m = Length(lvalue).
    ///
    /// # Input
    /// ## lvalue
    /// The target of the multiplication. The 'a' in 'a *= k (mod N)'.
    /// ## factor
    /// The value being multiplied into the target. The 'k' in 'a *= k (mod N)'.
    /// ## modulus
    /// Arithmetic is being done modulo this value. The 'N' in 'a *= k (mod N)'.
    /// ## coset_workspace
    /// A pre-initialized coset register storing 0 used for workspace during the computation.
    operation TimesEqualConst_Coset (lvalue: CosetLittleEndian, factor: Int, modulus: Int, coset_workspace: CosetLittleEndian) : Unit {
        body (...) {
            Controlled TimesEqualConst_Coset(new Qubit[0], (lvalue, factor, modulus, coset_workspace));
        }
        adjoint auto;
        controlled (cs, ...) {
            let inverse_factor = InverseMod(factor, modulus);
            // z += a*f (mod N)
            Controlled PlusEqualTimesConst_Coset(cs, (coset_workspace, lvalue, factor, modulus));
            // a -= z*inv(f) (mod N)
            Controlled MinusEqualTimesConst_Coset(cs, (lvalue, coset_workspace, inverse_factor, modulus));
            // a, z = z, a
            XorEqual(lvalue!, coset_workspace!);
            XorEqual(coset_workspace!, lvalue!);
            XorEqual(lvalue!, coset_workspace!);
        }
        controlled adjoint auto;
    }
}
