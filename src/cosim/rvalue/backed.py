from typing import Optional, Any, Tuple, Iterable

import cirq

import cosim
from .rvalue import RValue


@cirq.value_equality
class QubitRValue(RValue[bool]):
    def __init__(self, val: 'cosim.Qubit'):
        self.val = val

    def _value_equality_values_(self):
        return self.val

    def permutation_registers(self) -> Iterable['cosim.Qureg']:
        return [cosim.RawQureg([self.val])]

    def permutation_registers_from_value(self, val: bool) -> Tuple[int, ...]:
        return int(val),

    def value_from_permutation_registers(self, args: Tuple[int, ...]
                                         ) -> bool:
        return args[0] != 0

    def existing_storage_location(self) -> Any:
        return self.val

    def make_storage_location(self, name: Optional[str] = None):
        raise ValueError('existing storage')

    def init_storage_location(self,
                              location: Any,
                              controls: 'cosim.QubitIntersection'):
        raise ValueError('existing storage')

    def del_storage_location(self,
                             location: Any,
                             controls: 'cosim.QubitIntersection'):
        raise ValueError('existing storage')

    def __str__(self):
        return 'rval({})'.format(self.val)

    def __repr__(self):
        return 'cosim.QubitRValue({!r})'.format(self.val)


@cirq.value_equality
class QuintRValue(RValue[int]):
    def __init__(self, val: 'cosim.Quint'):
        self.val = val

    def _value_equality_values_(self):
        return self.val

    def permutation_registers(self) -> Iterable['cosim.Qureg']:
        return [self.val.qureg]

    def permutation_registers_from_value(self, val: int) -> Tuple[int, ...]:
        return val,

    def value_from_permutation_registers(self, args: Tuple[int, ...]
                                         ) -> int:
        return args[0]

    def existing_storage_location(self) -> Any:
        return self.val

    def make_storage_location(self, name: Optional[str] = None):
        raise ValueError('existing storage')

    def init_storage_location(self,
                              location: Any,
                              controls: 'cosim.QubitIntersection'):
        raise ValueError('existing storage')

    def del_storage_location(self,
                             location: Any,
                             controls: 'cosim.QubitIntersection'):
        raise ValueError('existing storage')

    def __str__(self):
        return 'rval({})'.format(self.val)

    def __repr__(self):
        return 'cosim.QuintRValue({!r})'.format(self.val)
