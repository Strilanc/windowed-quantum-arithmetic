import cosim
from ..signature_gate import SignatureGate


class _LetUnaryGate(SignatureGate):
    def register_name_prefix(self):
        return '_let_unary_'

    def emulate(self,
                forward: bool,
                *,
                lvalue: 'cosim.Mutable[int]',
                binary: int):
        if forward:
            assert lvalue.val == 0
            lvalue.val = 1 << binary
        else:
            assert lvalue.val == 1 << binary
            lvalue.val = 0

    def do(self,
           controls: 'cosim.QubitIntersection',
           *,
           lvalue: cosim.Quint,
           binary: cosim.Quint):
        assert len(lvalue) >= 1 << len(binary)
        cosim.emit(cosim.LetAnd(lvalue[0]).controlled_by(controls))
        for i, q in enumerate(binary):
            s = 1 << i
            for j in range(s):
                a = lvalue[j]
                b = lvalue[j + s]
                cosim.emit(cosim.LetAnd(b).controlled_by(a & q))
                a ^= b

    def describe(self, lvalue, binary):
        return '{} := unary({})'.format(lvalue, binary)

    def __repr__(self):
        return 'cosim.LetUnaryGate'


LetUnary = _LetUnaryGate()
