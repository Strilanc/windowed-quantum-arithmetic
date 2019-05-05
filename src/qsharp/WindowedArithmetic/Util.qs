namespace WindowedArithmetic {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Extensions.Convert;
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

    function SquarePow(b: BigInt, e: Int, modulus: BigInt) : BigInt {
        mutable r = b;
        for (i in 1..e) {
            set r = r * r % modulus;
        }
        return r;
    }

    function ProperMod(v: BigInt, modulus: BigInt) : BigInt {
        return ((v % modulus) + modulus) % modulus;
    }

    function BigIntToInt(v: BigInt) : Int {
        if (v < ToBigInt(0) or v >= ToBigInt(1) <<< 63) {
            fail "Out of range";
        }
        let bs = BigIntToBools(v);
        mutable result = 0;
        for (b in bs) {
            set result = result <<< 1;
            if (b) {
                set result = result + 1;
            }
        }
        return result;
    }

    function FloorBigLg2(n: BigInt) : Int {
        if (n <= ToBigInt(1)) {
            return 0;
        }
        let bools = BigIntToBools(n);
        mutable m = Length(bools) - 1;
        for (i in 0..7) {
            if (not bools[m]) {
                set m = m - 1;
            }
        }
        return m;
    }

    function CeilMultiple(numerator: Int, multiple: Int) : Int {
        return ((numerator + multiple - 1) / multiple) * multiple;
    }

    function CeilPowerOf2(n: Int) : Int {
        return 1 <<< CeilLg2(n);
    }

    function SkipLE(reg: LittleEndian, start: Int) : LittleEndian {
        return LittleEndian(reg![start..Length(reg!)-1]);
    }

    function SliceLE(reg: LittleEndian, start: Int, stop: Int) : LittleEndian {
        let clamp_stop = Min(stop, Length(reg!));
        return LittleEndian(reg![start..clamp_stop-1]);
    }

    operation ForceMeasureResetBigInt(qs: LittleEndian, expectedValue: BigInt) : BigInt {
        mutable result = ToBigInt(0);
        mutable i = 0;
        for (q in qs!) {
            AssertProb([PauliZ],
                       [q],
                       ((expectedValue >>> i) &&& ToBigInt(1)) != ToBigInt(0) ? One | Zero,
                       1.0,
                       $"Expected {expectedValue} but assertion failed.",
                       0.01);
            if (Measure([PauliZ], [q]) == One) {
                set result = result + (ToBigInt(1) <<< i);
                X(q);
            }
            set i = i + 1;
        }
        return result;
    }

    function CeilBigLg2(n: BigInt) : Int {
        if (n <= ToBigInt(1)) {
            return 0;
        }
        return FloorBigLg2(n - ToBigInt(1)) + 1;
    }

    function BitLength(n: BigInt) : Int {
        return CeilBigLg2(n + ToBigInt(1));
    }

    operation RandomBigIntPow2(bits: Int) : BigInt {
        mutable t = ToBigInt(0);
        for (i in 0..32..bits-1) {
            let m = Min(32, bits - i);
            set t = (t <<< m) + ToBigInt(RandomIntPow2(m));
        }
        return t;
    }

    operation MeasureResetBigInt(qs: LittleEndian) : BigInt {
        mutable result = ToBigInt(0);
        mutable i = 0;
        for (q in qs!) {
            if (Measure([PauliZ], [q]) == One) {
                set result = result + (ToBigInt(1) <<< i);
                X(q);
            }
            set i = i + 1;
        }
        return result;
    }
}
