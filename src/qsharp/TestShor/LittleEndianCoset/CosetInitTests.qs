namespace Quantum.TestShor {
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Diagnostics;
    open FastShor;
    
    operation CosetInit_Test () : Unit {
        using (qs = Qubit[6]) {
            let r = CosetInit(qs, 3, 13);
            AssertIntEqual(MeasureInteger(r!) % 13, 3, "");
        }
    }
}
