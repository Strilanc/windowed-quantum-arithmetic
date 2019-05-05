from typing import Any, Optional

import cosim

from cosim.rvalue import RValue
from .add import uma_sweep
from ..signature_gate import SignatureGate


class _IfLessThanThenGateClass(SignatureGate):
    def register_name_prefix(self):
        return '_cmp_'

    def emulate(self,
                forward: bool,
                *,
                lhs: int,
                rhs: int,
                or_equal: bool,
                effect: 'cosim.SubEffect'):
        condition = lhs <= rhs if or_equal else lhs < rhs
        if condition:
            effect.op.mutate_state(forward,
                                   *effect.args.args,
                                   **effect.args.kwargs)

    def do(self,
           controls: 'cosim.QubitIntersection',
           *,
           lhs: 'cosim.Quint',
           rhs: 'cosim.Quint',
           or_equal: 'cosim.Qubit',
           effect: 'cosim.Operation'):
        n = max(len(lhs), len(rhs))

        with cosim.pad_all(lhs, rhs, min_len=n) as (lhs, rhs):
            # Propagate carries.
            with cosim.invert():
                uma_sweep(lhs, or_equal, rhs, cosim.QubitIntersection.EMPTY)

            # Apply effect.
            cosim.emit(cosim.ControlledOperation(effect, controls & rhs[-1]))

            # Uncompute carries.
            uma_sweep(lhs, or_equal, rhs, cosim.QubitIntersection.EMPTY)

    def describe(self, lhs, rhs, or_equal, effect):
        return 'IF {} < {} + {}: {}'.format(
            lhs, rhs, or_equal, effect)


class IfLessThanRVal(RValue[bool]):
    def __init__(self,
                 lhs: RValue[int],
                 rhs: RValue[int],
                 or_equal: RValue[bool]):
        self.lhs = lhs
        self.rhs = rhs
        self.or_equal = or_equal

    def existing_storage_location(self) -> Any:
        return None

    def make_storage_location(self, name: Optional[str] = None) -> Any:
        return cosim.qmanaged(name='_cmp')

    def phase_flip_if(self, controls: 'cosim.QubitIntersection'):
        cosim.emit(IfLessThanThenGate(
            lhs=self.lhs,
            rhs=self.rhs,
            or_equal=self.or_equal,
            effect=cosim.OP_PHASE_FLIP.controlled_by(controls)))

    def init_storage_location(self,
                              location: Any,
                              controls: 'cosim.QubitIntersection'):
        cosim.emit(IfLessThanThenGate(
            lhs=self.lhs,
            rhs=self.rhs,
            or_equal=self.or_equal,
            effect=cosim.OP_TOGGLE(location).controlled_by(controls)))

    def del_storage_location(self,
                             location: Any,
                             controls: 'cosim.QubitIntersection'):
     if cosim.measure_x_for_phase_fixup_and_reset(location):
         self.phase_flip_if(controls)



IfLessThanThenGate = _IfLessThanThenGateClass()
