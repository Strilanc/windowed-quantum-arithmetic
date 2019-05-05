namespace WindowedArithmetic
{
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Convert;

    operation RunPlusEqualProductMethod(t: BigInt,
                                        x: BigInt,
                                        y: BigInt,
                                        method: String) : BigInt {
        let nx = BitLength(x);
        let ny = BitLength(y);
        let nt = Max(nx+ny, BitLength(t)) + 1;
        let w = Max(1, FloorLg2(ny)-2);
        mutable result = ToBigInt(0);
        using (qt = Qubit[nt]) {
            using (qy = Qubit[ny]) {
                let vy = LittleEndian(qy);
                let vt = LittleEndian(qt);
                XorEqualConst(vy, y);
                XorEqualConst(vt, t);
                if (method == "window") {
                    PlusEqualConstTimesLEWindowed(vt, x, vy, w);
                } elif (method == "legacy") {
                    PlusEqualConstTimesLE(vt, x, vy);
                } elif (method == "karatsuba") {
                    PlusEqualConstTimesLEKaratsuba(vt, x, vy);
                } else {
                    fail $"Unknown method {method}";
                }
                let a = ForceMeasureResetBigInt(vy, y);
                set result = ForceMeasureResetBigInt(vt, t + x*y);
            }
        }
        return result;
    }
}
