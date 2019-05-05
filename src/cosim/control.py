from typing import Union, Any, Optional

import cosim


class ControlledRValue(cosim.RValue):
    def __init__(self,
                 controls: cosim.QubitIntersection,
                 rvalue: cosim.RValue):
        self.controls = controls
        self.rvalue = rvalue

    def make_storage_location(self, name: Optional[str] = None):
        return self.rvalue.make_storage_location(name)

    def init_storage_location(self,
                              location: Any,
                              controls: 'cosim.QubitIntersection'):
        self.rvalue.init_storage_location(location, controls & self.controls)

    def del_storage_location(self,
                             location: Any,
                            controls: 'cosim.QubitIntersection'):
        self.rvalue.del_storage_location(location, controls & self.controls)

    def __str__(self):
        return 'controlled({}, {})'.format(self.rvalue, self.controls)

    def __repr__(self):
        return 'cosim.ControlledRValue({!r}, {!r})'.format(self.controls,
                                                           self.rvalue)


class _ControlledByWithoutRValue:
    def __init__(self, controls: cosim.QubitIntersection):
        self.controls = controls

    def __and__(self, other):
        if isinstance(other, ControlledRValue):
            return ControlledRValue(self.controls & other.controls, other.rvalue)
        if isinstance(other, cosim.RValue):
            return ControlledRValue(self.controls, other)
        if isinstance(other, int):
            return ControlledRValue(self.controls, cosim.IntRValue(other))
        return NotImplemented

    def __rand__(self, other):
        return self.__and__(other)


def controlled_by(qubits: Union[cosim.Qubit, cosim.QubitIntersection]):
    if isinstance(qubits, cosim.Qubit):
        qubits = cosim.QubitIntersection((qubits,))
    return _ControlledByWithoutRValue(qubits)
