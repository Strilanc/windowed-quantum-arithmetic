from typing import Union

import cosim
from ..operation import Operation


class _PhaseFlipOp(Operation):
    def mutate_state(self, forward: bool, *args, **kwargs):
        pass

    def state_locations(self):
        return cosim.ArgsAndKwargs([], {})

    def permute(self, forward: bool, *args):
        pass

    def do(self, controls: 'cosim.QubitIntersection'):
        raise ValueError("The phase flip gate is fundamental.")

    def inverse(self):
        return self

    def __repr__(self):
        return 'cosim.OP_PHASE_FLIP'


def phase_flip(condition: 'Union[bool, cosim.Qubit, cosim.QubitIntersection, cosim.RValue[bool]]' = True):
    if condition is False:
        pass
    elif condition is True:
        cosim.emit(OP_PHASE_FLIP)
    elif isinstance(condition, (cosim.Qubit, cosim.QubitIntersection)):
        cosim.emit(OP_PHASE_FLIP.controlled_by(condition))
    elif isinstance(condition, cosim.RValue):
        with cosim.hold(condition) as q:
            cosim.emit(OP_PHASE_FLIP.controlled_by(q))
    else:
        raise NotImplementedError("Unknown phase flip condition: {!r}".format(condition))


OP_PHASE_FLIP = _PhaseFlipOp()
