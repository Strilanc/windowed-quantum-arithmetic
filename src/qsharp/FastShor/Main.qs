namespace FastShor
{
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;

    function USE_SHORTCUTS() : Bool {
        return false;
    }

    operation ShorFactor () : Unit {
        let modulus = 13613*14731; //15;
        let n = CeilLg2(modulus);
        let m = n + 4;
        let bas = 7;
        using (a_reg = Qubit[m]) {
            using (b_reg = Qubit[m]) {
                let a = CosetInit(a_reg, 1, modulus);
                let b = CosetInit(b_reg, 0, modulus);
                mutable k = 0;
                for (i in 0..3) {
                    let factor = SquarePow(bas, n-i, modulus);
                    using (q = Qubit()) {
                        LetPlus(q);
                        Controlled TimesEqualConst_Coset([q], (a, factor, modulus, b));
                        R1Frac(k, i, q);
                        H(q);
                        
                        if (DelMeasurePlus(q)) {
                            set k = k ||| (1 <<< i);
                        }
                    }
                    Message($"{k}/{2<<<i} = {k*1000/(2<<<i)}");
                }
                let b_val = MeasureInteger(b!);
                Message($"REMAINDER B {b_val % modulus}");
                let a_val = MeasureInteger(a!);
                Message($"REMAINDER A {a_val % modulus}");
            }
        }
        Message("DONE");
    }
}
