from typing import Optional, Any, Union, Generic, TypeVar, List, Tuple, Iterable, overload

import cosim


T = TypeVar('T')


class RValue(Generic[T]):
    """A value or expression that only needs to exist temporarily."""

    def permutation_registers(self) -> Iterable['cosim.Qureg']:
        raise NotImplementedError()

    def value_from_permutation_registers(self, args: Tuple[int, ...]) -> T:
        raise NotImplementedError()

    def permutation_registers_from_value(self, val: T) -> Tuple[int, ...]:
        raise NotImplementedError()

    def existing_storage_location(self) -> Any:
        return None

    def make_storage_location(self, name: Optional[str] = None) -> Any:
        raise NotImplementedError()

    def phase_flip_if(self, controls: 'cosim.QubitIntersection'):
        with cosim.hold(self, controls=controls) as loc:
            cosim.phase_flip(loc)

    def init_storage_location(self,
                              location: Any,
                              controls: 'cosim.QubitIntersection'):
        raise NotImplementedError()

    def del_storage_location(self,
                             location: Any,
                             controls: 'cosim.QubitIntersection'):
        with cosim.invert():
            self.init_storage_location(location, controls)


@overload
def rval(val: 'cosim.Qubit') -> 'cosim.RValue[bool]':
    pass
@overload
def rval(val: 'cosim.Quint') -> 'cosim.RValue[int]':
    pass
@overload
def rval(val: 'int') -> 'cosim.RValue[int]':
    pass
@overload
def rval(val: 'bool') -> 'cosim.RValue[bool]':
    pass
@overload
def rval(val: 'cosim.RValue[T]') -> 'cosim.RValue[T]':
    pass
def rval(val: Any) -> 'cosim.RValue[Any]':
    """Wraps the given candidate value into a `cosim.RValue`, if needed.

    Args:
         val: The value that the caller wants as an rvalue.

    Returns:
        A `cosim.RValue` wrapper around the given candidate value.
    """
    if isinstance(val, bool):
        return cosim.BoolRValue(val)
    if isinstance(val, int):
        return cosim.IntRValue(val)
    if isinstance(val, cosim.Qubit):
        return cosim.QubitRValue(val)
    if isinstance(val, cosim.Quint):
        return cosim.QuintRValue(val)
    if isinstance(val, cosim.RValue):
        return val
    raise NotImplementedError(
        "Don't know how to wrap type {} (value {!r}).".format(
            type(val),
            val))
