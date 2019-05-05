import cosim
from ..signature_gate import SignatureGate


class _LetAndGate(SignatureGate):
    def emulate(self,
                forward: bool,
                *,
                lvalue: 'cosim.Mutable[bool]'):
        if forward:
            assert lvalue.val == 0
            lvalue.val = 1
        else:
            assert lvalue.val == 1
            lvalue.val = 0

    def __pow__(self, power):
        if power == -1:
            return DelAnd

    def do(self,
           controls: 'cosim.QubitIntersection',
           lvalue: cosim.Qubit):
        lvalue ^= controls

    def describe(self, lvalue):
        return '{} := 1'.format(lvalue)

    def __repr__(self):
        return 'cosim.LetAnd'


class _DelAndGate(SignatureGate):
    def emulate(self,
                forward: bool,
                *,
                lvalue: 'cosim.Mutable[bool]'):
        LetAnd.emulate(not forward, lvalue=lvalue)

    def do(self,
           controls: 'cosim.QubitIntersection',
           lvalue: cosim.Qubit):
        if cosim.measure_x_for_phase_fixup_and_reset(lvalue):
            cosim.phase_flip(controls)

    def __pow__(self, power):
        if power == -1:
            return LetAnd

    def describe(self, lvalue):
        return '{} =: del 1'.format(lvalue)

    def __repr__(self):
        return 'cosim.DelAnd'


LetAnd = _LetAndGate()
DelAnd = _DelAndGate()
