namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;

    operation Toggle(t: Qubit) : Unit {
        body (...) {
            X(t);
        }
        adjoint self;
        controlled (cs, ...) {
            Controlled X(cs, t);
            // if (Length(cs) == 0) {
            //     X(t);
            // } elif (Length(cs) == 1) {
            //     CNOT(cs[0], t);
            // } else {
            //     using (q = Qubit()) {
            //         InitAnd(cs[0], cs[1], q);
            //         Controlled Toggle([q] + cs[2..Length(cs)-1], t);
            //         UncomputeAnd(cs[0], cs[1], q);
            //     }
            // }
        }
        controlled adjoint self;
    }

    operation InitToggle(t: Qubit) : Unit {
        body (...) {
            Toggle(t);
        }
        adjoint auto;
        controlled auto;
        controlled adjoint (cs, ...) {
            Controlled X(cs, t);
            // if (Length(cs) == 0) {
            //     X(t);
            // } elif (Length(cs) == 1) {
            //     CNOT(cs[0], t);
            // } else {
            //     if (MResetX(t) == One) {
            //         Controlled PhaseNegate(cs, ());
            //     }
            // }
        }
    }

    operation UncomputeToggle(t: Qubit) : Unit {
        body (...) {
            Adjoint InitToggle(t);
        }
        adjoint auto;
        controlled auto;
        controlled adjoint auto;
    }

    operation InitAnd(a: Qubit, b: Qubit, t: Qubit) : Unit {
        body(...) {
            CCNOT(a, b, t);
            // H(t);
            // T(t);
            // CNOT(b, t);
            // Adjoint T(t);
            // CNOT(a, t);
            // T(t);
            // CNOT(b, t);
            // Adjoint T(t);
            // H(t);
            // Adjoint S(t);
        }
        adjoint (...) {
            CCNOT(a, b, t);
            // if (MResetX(t) == One) {
            //     CZ(a, b);
            // }
        }
    }

    operation UncomputeAnd(a: Qubit, b: Qubit, t: Qubit) : Unit {
        body (...) {
            Adjoint InitAnd(a, b, t);
        }
        adjoint auto;
    }
}
