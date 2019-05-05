namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;

    operation PhaseNegate() : Unit {
        body (...) {
            // Global phase is unobservable.
        }
        controlled (cs, ...) {
            if (Length(cs) == 0) {
                // Global phase is unobservable.
            } elif (USE_SHORTCUTS()) {
                Controlled Z(cs[1..Length(cs)-1], cs[0]);
            } elif (Length(cs) == 1) {
                Z(cs[0]);
            } elif (Length(cs) == 2) {
                CZ(cs[0], cs[1]);
            } else {
                using (q = Qubit()) {
                    InitAnd(cs[0], cs[1], q);
                    Controlled PhaseNegate([q] + cs[2..Length(cs)-1], ());
                    UncomputeAnd(cs[0], cs[1], q);
                }
            }
        }
    }

    operation Toggle(t: Qubit) : Unit {
        body (...) {
            X(t);
        }
        adjoint self;
        controlled (cs, ...) {
            if (USE_SHORTCUTS()) {
                Controlled X(cs, t);
            } elif (Length(cs) == 0) {
                X(t);
            } elif (Length(cs) == 1) {
                CNOT(cs[0], t);
            } else {
                using (q = Qubit()) {
                    InitAnd(cs[0], cs[1], q);
                    Controlled Toggle([q] + cs[2..Length(cs)-1], t);
                    UncomputeAnd(cs[0], cs[1], q);
                }
            }
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
            if (USE_SHORTCUTS()) {
                Controlled X(cs, t);
            } elif (Length(cs) == 0) {
                X(t);
            } elif (Length(cs) == 1) {
                CNOT(cs[0], t);
            } else {
                if (MResetX(t) == One) {
                    Controlled PhaseNegate(cs, ());
                }
            }
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
            H(t);
            T(t);
            CNOT(b, t);
            Adjoint T(t);
            CNOT(a, t);
            T(t);
            CNOT(b, t);
            Adjoint T(t);
            H(t);
            Adjoint S(t);
        }
        adjoint (...) {
            if (MResetX(t) == One) {
                CZ(a, b);
            }
        }
    }

    operation UncomputeAnd(a: Qubit, b: Qubit, t: Qubit) : Unit {
        body (...) {
            Adjoint InitAnd(a, b, t);
        }
        adjoint auto;
    }

    operation LetPlus (lvalue: Qubit) : Unit {
        body (...) {
            H(lvalue);
        }
    }

    operation DelMeasurePlus (lvalue: Qubit) : Bool {
        body (...) {
            return MResetX(lvalue) == One;
        }
    }
}
