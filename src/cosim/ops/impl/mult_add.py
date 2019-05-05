from typing import Optional

import cosim
from ..signature_gate import SignatureGate


class _PlusEqualTimesGateClass(SignatureGate):
    def register_name_prefix(self):
        return '_mult_add_'

    def emulate(self,
                forward: bool,
                lvalue: 'cosim.Mutable[int]',
                quantum_factor: int,
                const_factor: int):
        lvalue.val += quantum_factor * const_factor * (1 if forward else -1)

    def do(self,
           controls: 'cosim.QubitIntersection',
           lvalue: 'cosim.Quint',
           quantum_factor: 'cosim.Quint',
           const_factor: int):
        for i, q in enumerate(quantum_factor):
            lvalue += (const_factor << i) & cosim.controlled_by(q)

    def describe(self, lvalue, quantum_factor, const_factor):
        return 'SCALE-ADD {} += {} * {}'.format(lvalue,
                                                quantum_factor,
                                                const_factor)

    def __repr__(self):
        return 'cosim.PlusEqualTimesGate'


PlusEqualTimesGate = _PlusEqualTimesGateClass()
