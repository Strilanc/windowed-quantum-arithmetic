from typing import Optional, Any, Union, Generic, TypeVar, List, Tuple, Iterable, overload

import cosim


T = TypeVar('T')


@overload
def hold(val: 'cosim.Qubit',
         name: Optional[str] = None,
         controls: 'Optional[cosim.QubitIntersection]' = None) -> 'cosim.HeldRValueManager[bool]':
    pass
@overload
def hold(val: 'cosim.Quint',
         name: Optional[str] = None,
         controls: 'Optional[cosim.QubitIntersection]' = None) -> 'cosim.HeldRValueManager[int]':
    pass
@overload
def hold(val: 'int',
         name: Optional[str] = None,
         controls: 'Optional[cosim.QubitIntersection]' = None) -> 'cosim.HeldRValueManager[int]':
    pass
@overload
def hold(val: 'bool',
         name: Optional[str] = None,
         controls: 'Optional[cosim.QubitIntersection]' = None) -> 'cosim.HeldRValueManager[bool]':
    pass
@overload
def hold(val: 'cosim.RValue[T]',
         name: Optional[str] = None,
         controls: 'Optional[cosim.QubitIntersection]' = None) -> 'cosim.HeldRValueManager[T]':
    pass


def hold(val: Union[T, 'cosim.RValue[T]', 'cosim.Qubit', 'cosim.Quint'],
         *,
         name: str = '',
         controls: 'Optional[cosim.QubitIntersection]' = None
         ) -> 'cosim.HeldRValueManager[T]':
    """Returns a context manager that ensures the given rvalue is allocated.

    Usage:
        ```
        with cosim.hold(5) as reg:
            # reg is an allocated quint storing the value 5
            ...
        ```

    Args:
        val: The value to hold.
        name: Optional name to use when allocating space for the value.
        controls: If any of these are not set, the result is a default value
            (e.g. False or 0) instead of the rvalue.

    Returns:
        A cosim.HeldRValueManager wrapping the given value.
    """
    return cosim.HeldRValueManager(
        cosim.rval(val),
        controls=controls or cosim.QubitIntersection.EMPTY,
        name=name)


class HeldRValueManager(Generic[T]):
    def __init__(self, rvalue: 'cosim.RValue[T]',
                 *,
                 controls: 'cosim.QubitIntersection',
                 name: str = ''):
        assert isinstance(name, str)
        self.name = name
        self.rvalue = rvalue
        self.controls = controls
        self.location = None  # type: Optional[Any]
        self.qalloc = None  # type: Optional[Any]

    def __repr__(self):
        return 'cosim.HeldRValueManager({!r}, {!r})'.format(
            self.rvalue, self.name)

    def __enter__(self):
        assert self.location is None
        self.location = self.rvalue.existing_storage_location()
        if self.location is None:
            self.location = self.rvalue.make_storage_location(self.name)
            self.qalloc = cosim.qmanaged(self.location)
            self.qalloc.__enter__()
            cosim.emit(cosim.LetRValueOperation(
                self.rvalue, self.location).controlled_by(self.controls))
        return self.location

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.qalloc is not None and exc_type is None:
            cosim.emit(cosim.DelRValueOperation(
                self.rvalue, self.location).controlled_by(self.controls))
            self.qalloc.__exit__(exc_type, exc_val, exc_tb)
