namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    
    /// # Summary
    /// Performs q ^^^= (a < b) where 'q' is a qubit, and 'a' and 'b' are quantum integers.
    ///
    /// a < b evaluates to 1 for all computational basis states |a'> and |b'> such that a' < b', and 0 otherwise.
    ///
    /// # Input
    /// ## q
    /// The qubit to toggle whenever the left hand side is less than the right hand side.
    /// ## lhs
    /// The left hand side of the comparison. A quantum register.
    /// ## rhs
    /// The right hand side of the comparison. A quantum register.
    operation XorEqualsLessThan(lvalue: Qubit, lhs: LittleEndian, rhs: LittleEndian) : Unit {
        body (...) {
            Controlled XorEqualsLessThan(new Qubit[0], (lvalue, lhs, rhs));
        }
        adjoint self;
        controlled (cs, ...) {
            let lhse = LittleEndian(lhs! + [lvalue]);
            MinusEqual(lhse, rhs);
            PlusEqual(lhs, rhs);
        }
        controlled adjoint auto;
    }

    /// # Summary
    /// Performs q ^^^= (a < k) where 'q' is a qubit, 'a' is a quantum integer,
    /// and 'k' is a classical constant.
    ///
    /// 'a < k' evaluates to 1 for all computational basis states |a'> such that a' < k, and 0 otherwise.
    ///
    /// # Input
    /// ## q
    /// The qubit to toggle whenever the left hand side is less than the right hand side.
    /// ## lhs
    /// The left hand side of the comparison. A quantum register.
    /// ## rhs
    /// The right hand side of the comparison. A classical constant.
    operation XorEqualsLessThanConst (lvalue: Qubit, lhs: LittleEndian, rhs: Int) : Unit {
        body (...) {
            Controlled XorEqualsLessThanConst(new Qubit[0], (lvalue, lhs, rhs));
        }
        adjoint self;
        controlled (cs, ...) {
            if (rhs < 0) {
                return ();
            } elif (rhs >= (1 <<< Length(lhs!))) {
                Controlled X(cs, lvalue);
                return ();
            }

            let n = Max(CeilLg2(rhs), Length(lhs!));
            using (t_reg = Qubit[n]) {
                let t = LittleEndian(t_reg);
                LetConst(t, rhs);
                Controlled XorEqualsLessThan(cs, (lvalue, lhs, t));
                DelConst(t, rhs);
            }
        }
        controlled adjoint self;
    }

    /// # Summary
    /// Negates the phase of all computational basis states |a> satisfying 'a < k'.
    ///
    /// # Input
    /// ## lhs
    /// The left hand side of the comparison. A quantum register.
    /// ## rhs
    /// The right hand side of the comparison. A classical constant.
    operation PhaseNegateLessThanConst (lhs: LittleEndian, rhs: Int) : Unit {
        body (...) {
            let n = Max(CeilLg2(rhs), Length(lhs!));
            using (q = Qubit()) {
                H(q);
                Z(q);
                XorEqualsLessThanConst(q, lhs, rhs);
                Reset(q);
            }
        }
        adjoint self;
    }
}
