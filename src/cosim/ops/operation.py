from typing import Union, Any

import cosim


class Operation:
    def do(self, controls: 'cosim.QubitIntersection'):
        raise RuntimeError('Unprocessed terminal operation: {!r}'.format(self))

    def state_locations(self) -> 'cosim.ArgsAndKwargs[Union[cosim.Qureg, cosim.Qubit, cosim.Quint], Any]':
        raise NotImplementedError('state_locations not implemented by {!r}'.format(self))

    def mutate_state(self, forward: bool, *args, **kwargs):
        raise NotImplementedError('mutate_state not implemented by {!r}'.format(self))

    def inverse(self) -> 'Operation':
        return cosim.InverseOperation(self)

    def controlled_by(self, controls: Union['cosim.Qubit',
                                            'cosim.QubitIntersection']):
        if isinstance(controls, cosim.Qubit):
            return cosim.ControlledOperation(self, cosim.QubitIntersection((controls,)))
        if len(controls) == 0:
            return self
        return cosim.ControlledOperation(self, controls)


class FlagOperation(Operation):
    def state_locations(self):
        return ()

    def mutate_state(self, forward: bool, *args, **kwargs):
        pass

    def inverse(self):
        raise NotImplementedError('{!r} has no defined inverse'.format(self))


class LetRValueOperation(Operation):
    def __init__(self, rvalue: 'cosim.RValue', loc: Any):
        self.rvalue = rvalue
        self.loc = loc

    def inverse(self) -> 'cosim.Operation':
        return DelRValueOperation(self.rvalue, self.loc)

    def do(self, controls: 'cosim.QubitIntersection'):
        self.rvalue.init_storage_location(self.loc, controls)

    def __str__(self):
        return '{} := {}'.format(self.loc, self.rvalue)

    def __repr__(self):
        return 'cosim.LetRValueOperation({!r}, {!r})'.format(self.rvalue,
                                                             self.loc)


class DelRValueOperation(Operation):
    def __init__(self, rvalue: 'cosim.RValue', loc: Any):
        self.rvalue = rvalue
        self.loc = loc

    def inverse(self) -> 'cosim.Operation':
        return LetRValueOperation(self.rvalue, self.loc)

    def do(self, controls: 'cosim.QubitIntersection'):
        self.rvalue.init_storage_location(self.loc, controls)

    def __str__(self):
        return '{} := {}'.format(self.loc, self.rvalue)

    def __repr__(self):
        return 'cosim.LetRValueOperation({!r}, {!r})'.format(self.rvalue,
                                                             self.loc)
