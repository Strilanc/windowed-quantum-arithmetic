namespace FastShor {
    open Microsoft.Quantum.Extensions.Bitwise;
    open Microsoft.Quantum.Primitive;
    open Microsoft.Quantum.Canon;
    
    /// # Summary
    /// Chooses a coset register length sufficient to perform period finding.
    ///
    /// # Input
    /// ## modulusLength
    /// The number of bits in the modulus in f(k) = g**k (mod N).
    /// ## safetyFactor
    /// The representable deviation will be at least this many times the maximum deviation.
    /// Doubling this value will halve the probability of failure due to deviation.
    function CosetRegisterLengthForPeriodFinding(modulusLength: Int, safetyFactor: Int) : Int {
        let n = modulusLength;
        mutable p = 2*CeilLg2(n) + CeilLg2(safetyFactor);
        for (_ in 0..50) {
            let d = Max(1, TimesEqualConstRaisedToExponentMod_Coset_MaxDeviation(n + p, 2*n));
            let g = FloorLg2(d);
            let r = (1 <<< p) / (d * safetyFactor);
            if (r == 0) {
                set p = p + 1;
            } elif (r > 2) {
                set p = p - 1;
            } else {
                return n + p;
            }
        }
        fail "Didn't converge.";
    }

    /// # Summary
    /// Maximum amount of coset deviation added into or subtracted out of the
    /// lvalue and workspace registers by the TimesEqualConstRaisedToExponentMod_Coset
    /// operation.
    function TimesEqualConstRaisedToExponentMod_Coset_MaxDeviation(exponentLength: Int, 
                                                                   registerLength: Int) : Int {
        let d = PlusEqualTimesConst_Coset_MaxDeviation(registerLength);
        
        // Because 'PlusEqualTimesConst_Coset' adds into one register, subtracts out of the other,
        // then swaps them, it alternates increasing and decreasing the deviation of each register.
        // This halves the maximum deviation, and square roots the expected deviation (assuming
        // random deviations at each step).
        return (d * exponentLength + 1) / 2;
    }

    /// # Summary
    /// Maximum amount of coset deviation added into or subtracted out of the
    /// lvalue and workspace registers by the PlusEqualTimesConst_Coset operation.
    function PlusEqualTimesConst_Coset_MaxDeviation(regLength: Int) : Int {
        let g = PlusEqualTimesConst_Coset_GroupSize(regLength);
        let reps = (regLength + g - 1) / g;
        return reps * PlusEqualLookup_Coset_MaxDeviation();
    }

    /// # Summary
    /// Maximum amount of coset deviation added into the lvalue register by the
    /// PlusEqualLookup operation.
    function PlusEqualLookup_Coset_MaxDeviation() : Int {
        return 1;
    }

    /// # Summary
    /// Picks the lookup group size 'g' to use for lookup accelerated multiplication.
    ///
    /// # Input
    /// ## regLength
    /// The length of the coset registers being operated on.
    function PlusEqualTimesConst_Coset_GroupSize(regLength: Int) : Int {
        return _estimateOptimalGroupSize(regLength);
    }

    function _estimateOptimalGroupSize(n: Int) : Int {
        mutable bestG = 1;
        mutable bestCost = _costAtGroupSize(n, 1);
        for (g in 2..30) {
            let c = _costAtGroupSize(n, g);
            if (c < bestCost) {
                set bestCost = c;
                set bestG = g;
            }
        }
        return bestG;
    }

    function _costAtGroupSize(n: Int, g: Int) : Int {
        let perOpCost = _additionCost(n) + _lookupCost(1 <<< g) + _delLookupCost(1 <<< g);
        return (n + g - 1) / g * perOpCost;
    }

    function _additionCost(n: Int) : Int {
        return 2*n;
    }

    function _lookupCost(n: Int) : Int {
        return 2*n;
    }

    function _delLookupCost(n: Int) : Int {
        let low = 1 <<< CeilLg2(n);
        let high = 1 <<< FloorLg2(n);
        return _unaryCost(low) + _lookupCost(high) + _delUnaryCost(low);
    }

    function _unaryCost(n: Int) : Int {
        // runs fast enough to saturate factories
        return n;
    }

    function _delUnaryCost(n: Int) : Int {
        // dominated by Clifford work that can be parallelized
        return n / 10;
    }
}
