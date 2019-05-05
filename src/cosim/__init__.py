from cosim.lens import (
    capture,
    CaptureLens,
    condition,
    emit,
    invert,
    Lens,
    Log,
)

from cosim.rvalue import (
    BoolRValue,
    HeldRValueManager,
    hold,
    IntRValue,
    rval,
    RValue,
    QubitIntersection,
    QubitRValue,
    QuintRValue,
    ScaledIntRValue,
)

from cosim.lvalue import (
    NamedQureg,
    RangeQureg,
    RawQureg,
    pad,
    pad_all,
    PaddedQureg,
    Qubit,
    Quint,
    Qureg,
    UniqueHandle,
)

from cosim.util import (
    ArgParameter,
    ArgsAndKwargs,
    ceil_lg2,
    floor_lg2,
    leading_zero_bit_count,
    modular_multiplicative_inverse,
    MultiWith,
    popcnt,
)

from cosim.control import (
    controlled_by,
    ControlledRValue,
)

from cosim.sim import (
    Sim,
)

from cosim.log_cirq import (
    LogCirqCircuit,
    CountNots,
)

from cosim.ops import (
    ControlledOperation,
    DelAnd,
    FlagOperation,
    HeldMultipleRValue,
    IfLessThanRVal,
    IfLessThanThenGate,
    InverseOperation,
    LetAnd,
    LetUnary,
    LookupRValue,
    LookupTable,
    measure,
    measure_x_for_phase_fixup_and_reset,
    MeasureOperation,
    MeasureXForPhaseKickOperation,
    Mutable,
    OP_PHASE_FLIP,
    OP_TOGGLE,
    OP_XOR,
    OP_XOR_C,
    Operation,
    LetRValueOperation,
    DelRValueOperation,
    phase_flip,
    PlusEqualGate,
    PlusEqualTimesGate,
    SignatureGate,
    SignatureGateArgTypes,
    SignatureOperation,
    SubEffect,
    XorLookupOperation,
)

from cosim.qalloc import (
    AllocQuregOperation,
    qalloc,
    qalloc_int,
    QallocManager,
    qmanaged,
    qfree,
    qmanaged_int,
    ReleaseQuregOperation,
)
