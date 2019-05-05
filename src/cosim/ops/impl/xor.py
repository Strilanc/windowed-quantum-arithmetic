import cosim
from ..signature_gate import SignatureGate


class _XorConstGateClass(SignatureGate):
    def emulate(self, forward: bool, lvalue: 'cosim.Mutable[int]', mask: int):
        lvalue.val ^= mask

    def do(self,
           controls: 'cosim.QubitIntersection',
           lvalue: 'cosim.Quint',
           mask: int):
        targets = []
        for i, q in enumerate(lvalue):
            if mask & (1 << i):
                targets.append(q)
        cosim.emit(cosim.OP_TOGGLE(cosim.RawQureg(targets)).controlled_by(controls))

    def describe(self, lvalue, mask):
        return 'OP_XOR_C {} ^= {}'.format(lvalue, mask)

    def __repr__(self):
        return 'cosim.OP_XOR_C'


class _XorRegisterGateClass(SignatureGate):
    def emulate(self, forward: bool, lvalue: 'cosim.Mutable[int]', mask: int):
        lvalue.val ^= mask

    def do(self,
           controls: 'cosim.QubitIntersection',
           lvalue: 'cosim.Quint',
           mask: 'cosim.Quint'):
        for i, q in enumerate(lvalue):
            cosim.emit(cosim.OP_TOGGLE(cosim.RawQureg([q])).controlled_by(controls & mask[i]))

    def describe(self, lvalue, mask):
        return 'OP_XOR {} ^= {}'.format(lvalue, mask)

    def __repr__(self):
        return 'cosim.OP_XOR'


OP_XOR_C = _XorConstGateClass()
OP_XOR = _XorRegisterGateClass()
