import cosim
from ..signature_gate import SignatureGate


class _NotGateClass(SignatureGate):
    def emulate(self, forward: bool, lvalue: 'List[cosim.Mutable[bool]]'):
        for q in lvalue:
            q.val = not q.val

    def do(self,
           controls: 'cosim.QubitIntersection',
           lvalue: 'cosim.Qureg'):
        raise ValueError("The NOT gate is fundamental.")

    def __pow__(self, power):
        if power in [1, -1]:
            return self
        return NotImplemented

    def describe(self, lvalue):
        return 'OP_TOGGLE {}'.format(lvalue)

    def __repr__(self):
        return 'cosim.OP_TOGGLE'


OP_TOGGLE = _NotGateClass()
