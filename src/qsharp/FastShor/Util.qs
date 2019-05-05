namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;

    function Max(a: Int, b: Int) : Int {
        if (a > b) {
            return a;
        } else {
            return b;
        }
    }

    function Min(a: Int, b: Int) : Int {
        if (a < b) {
            return a;
        } else {
            return b;
        }
    }

    function CeilLg2(modulus: Int) : Int {
        mutable k = 0;
        for (i in 0..100) {
            if ((1 <<< k) < modulus) {
                set k = k + 1;
            }
        }
        return k;
    }

    function FloorLg2(modulus: Int) : Int {
        mutable k = 0;
        for (i in 0..100) {
            if ((2 <<< k) <= modulus) {
                set k = k + 1;
            }
        }
        return k;
    }

    function SquarePow(b: Int, e: Int, modulus: Int) : Int {
        mutable r = b;
        for (i in 1..e) {
            set r = r * r % modulus;
        }
        return r;
    }

    function ProperMod(v: Int, modulus: Int) : Int {
        return ((v % modulus) + modulus) % modulus;
    }
}
