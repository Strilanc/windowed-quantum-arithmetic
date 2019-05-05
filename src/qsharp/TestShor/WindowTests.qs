namespace Tests {
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Extensions.Convert;
    open Microsoft.Quantum.Extensions.Diagnostics;
    open FastShor;

    /// # Summary
    /// Checks that the given operation, when applied to LittleEndian registers storing
    /// the given inputs, results in those registers storing the given outputs.
    ///
    /// # Input
    /// ## n1
    /// Number of qubits in the first register.
    /// ## n2
    /// Number of qubits in the second register.
    /// ## input1
    /// Initial value for the first register.
    /// ## input2
    /// Initial value for the second register.
    /// ## output1
    /// Expected output value for the first register.
    /// ## output2
    /// Expected output value for the second register.
    /// ## op
    /// The operation to apply.
    operation AssertOpInOut2(n1: Int,
                             n2: Int,
                             input1: BigInt,
                             input2: BigInt,
                             output1: BigInt,
                             output2: BigInt,
                             op: ((LittleEndian, LittleEndian) => Unit)) : Unit {
        using (b1 = Qubit[n1]) {
            using (b2 = Qubit[n2]) {
                let le1 = LittleEndian(b1);
                let le2 = LittleEndian(b2);
                XorEqualConst(le1, input1);
                XorEqualConst(le2, input2);
                op(le1, le2);
                let v1 = MeasureResetBigInt(le1);
                let v2 = MeasureResetBigInt(le2);
                if (v1 != output1 or v2 != output2) {
                    fail $"Case failed.
                        AssertPerforms({n1}, {n2}, {input1}, {input2}, {output1}, {output2}, {op});

                        Expected output 1: {output1}
                          Actual output 1: {v1}

                        Expected output 2: {output2}
                          Actual output 2: {v2}";
                }
            }
        }

    }

    operation AssertOpImplementsPlusEqualConstTimesLE(op: ((LittleEndian, BigInt, LittleEndian) => Unit)) : Unit {
        AssertOpInOut2(10, 10,
                       ToBigInt(7), ToBigInt(5),
                       ToBigInt(7+13*5), ToBigInt(5),
                       op(_, ToBigInt(13), _));

        let x = RandomBigIntPow2(100);
        let y = RandomBigIntPow2(100);
        let z = RandomBigIntPow2(100);
        AssertOpInOut2(201, 100,
                       x, y,
                       x + y*z, y,
                       op(_, z, _));
    }

    operation ToffoliSim_PlusEqualConstTimesLE_RawCases_Test() : Unit {
        AssertOpImplementsPlusEqualConstTimesLE(PlusEqualConstTimesLE);
        AssertOpImplementsPlusEqualConstTimesLE(PlusEqualConstTimesLEKaratsuba);
        AssertOpImplementsPlusEqualConstTimesLE(PlusEqualConstTimesLEWindowed(_, _, _, 1));
        AssertOpImplementsPlusEqualConstTimesLE(PlusEqualConstTimesLEWindowed(_, _, _, 2));
        AssertOpImplementsPlusEqualConstTimesLE(PlusEqualConstTimesLEWindowed(_, _, _, 3));
        AssertOpImplementsPlusEqualConstTimesLE(PlusEqualConstTimesLEWindowed(_, _, _, 4));
        AssertOpImplementsPlusEqualConstTimesLE(PlusEqualConstTimesLEWindowed(_, _, _, 5));
    }
}
