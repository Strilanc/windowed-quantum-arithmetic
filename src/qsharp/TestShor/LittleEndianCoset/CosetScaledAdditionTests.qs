namespace Quantum.TestShor {
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Diagnostics;
    open FastShor;
    
    operation PlusEqualTimesConst_Coset_Test () : Unit {
        let x = 2;
        let y = 3;
        let c = 37;
        let n = 6;
        let m = 5;
        using (qs = Qubit[n*2]) {
            let a = CosetInit(qs[0..n-1], x, m);
            let b = CosetInit(qs[n..2*n-1], y, m);
            PlusEqualTimesConst_Coset(a, b, c, m);
            AssertIntEqual(MeasureInteger(b!) % m, y, "");
            AssertIntEqual(MeasureInteger(a!) % m, (x + y*c) % m, "");
        }
    }
}
