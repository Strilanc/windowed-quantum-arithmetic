namespace Quantum.TestShor {
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Diagnostics;
    open FastShor;
    
    operation PlusEqualTimesConst_Coset_GroupSize_Test () : Unit {
        let f = PlusEqualTimesConst_Coset_GroupSize;
        //mutable d = 0;
        //for (n in 0..10000) {
        //    let s = f(n);
        //    if (s > d) {
        //        set d = s;
        //        Message($"BECAME {s} AT {n} with COST {_costAtGroupSize(n, s)}");
        //    }
        //}
        AssertIntEqual(f(64), 4, "");
        AssertIntEqual(f(128), 4, "");
        AssertIntEqual(f(256), 5, "");
        AssertIntEqual(f(512), 6, "");
        AssertIntEqual(f(1024), 7, "");
        AssertIntEqual(f(2048), 8, "");
        AssertIntEqual(f(4096), 8, "");
    }

    operation CosetRegisterLengthForPeriodFinding_100_Test () : Unit {
        let f = CosetRegisterLengthForPeriodFinding(_, 100);

        //mutable d = 0;
        //for (n in 0..10000) {
        //    let s = f(n)-n;
        //    if (s > d) {
        //        set d = s;
        //        Message($"BECAME {s} AT {n}");
        //    }
        //}
        AssertIntEqual(f(16)-16, 15, "");
        AssertIntEqual(f(32)-32, 16, "");
        AssertIntEqual(f(64)-64, 18, "");
        AssertIntEqual(f(128)-128, 20, "");
        AssertIntEqual(f(256)-256, 21, "");
        AssertIntEqual(f(512)-512, 23, "");
        AssertIntEqual(f(1024)-1024, 25, "");
        AssertIntEqual(f(2048)-2048, 27, "");
        AssertIntEqual(f(4096)-4096, 29, "");
        AssertIntEqual(f(8192)-8192, 30, "");
    }

    operation CosetRegisterLengthForPeriodFinding_1000_Test () : Unit {
        let f = CosetRegisterLengthForPeriodFinding(_, 1000);

        //mutable d = 0;
        //for (n in 0..10000) {
        //    let s = f(n)-n;
        //    if (s > d) {
        //        set d = s;
        //        Message($"BECAME {s} AT {n}");
        //    }
        //}
        AssertIntEqual(f(16)-16, 18, "");
        AssertIntEqual(f(32)-32, 20, "");
        AssertIntEqual(f(64)-64, 21, "");
        AssertIntEqual(f(128)-128, 23, "");
        AssertIntEqual(f(256)-256, 25, "");
        AssertIntEqual(f(512)-512, 26, "");
        AssertIntEqual(f(1024)-1024, 28, "");
        AssertIntEqual(f(2048)-2048, 30, "");
        AssertIntEqual(f(4096)-4096, 32, "");
        AssertIntEqual(f(8192)-8192, 34, "");
    }
}
