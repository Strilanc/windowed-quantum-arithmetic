from typing import List, Optional, Union, Tuple, Callable, TYPE_CHECKING, Iterable, Any

import cosim


def qmanaged(val: Union[None, int, 'cosim.Qubit', 'cosim.Qureg', 'cosim.Quint'] = None, *, name: Optional[str] = None) -> 'cosim.QallocManager':
    if val is None:
        q = cosim.Qubit('qalloc' if name is None else name)
        return QallocManager(cosim.RawQureg([q]), q)

    if isinstance(val, int):
        q = cosim.NamedQureg('' if name is None else name, val)
        return QallocManager(q, q)

    if isinstance(val, cosim.Qubit):
        assert name is None
        return QallocManager(cosim.RawQureg([val]), val)

    if isinstance(val, cosim.Qureg):
        assert name is None
        return QallocManager(val, val)

    if isinstance(val, cosim.Quint):
        assert name is None
        return QallocManager(val.qureg, val)

    raise NotImplementedError()


def qmanaged_int(*, bits: int, name: str = ''):
    return cosim.qmanaged(cosim.Quint(cosim.NamedQureg(name, bits)))


class QallocManager:
    def __init__(self, qureg: 'cosim.Qureg', wrap: Any):
        self.qureg = qureg
        self.wrap = wrap

    def __enter__(self):
        if len(self.qureg):
            cosim.emit(AllocQuregOperation(self.qureg))
        return self.wrap

    def __exit__(self, exc_type, exc_val, exc_tb):
        if len(self.qureg) and exc_type is None:
            cosim.emit(ReleaseQuregOperation(self.qureg))


def qalloc(val: Union[None, int] = None,
           *,
           name: Optional[str] = None,
           x_basis: bool = False) -> 'Any':
    if val is None:
        result = cosim.Qubit(name or '')
        reg = cosim.RawQureg([result])
    elif isinstance(val, int):
        result = cosim.NamedQureg(name or '', length=val)
        reg = result
    else:
        raise NotImplementedError()

    if len(reg):
        cosim.emit(AllocQuregOperation(reg, x_basis))

    return result


def qfree(target: Union[cosim.Qubit, cosim.Qureg, cosim.Quint],
          equivalent_expression: 'Union[None, bool, int, cosim.RValue[Any]]' = None,
          dirty: bool = False):

    if equivalent_expression is not None:
        cosim.rval(equivalent_expression).del_storage_location(
            target, cosim.QubitIntersection.EMPTY)

    if isinstance(target, cosim.Qubit):
        reg = cosim.RawQureg([target])
    elif isinstance(target, cosim.Qureg):
        reg = target
    elif isinstance(target, cosim.Quint):
        reg = target.qureg
    else:
        raise NotImplementedError()
    if len(reg):
        cosim.emit(cosim.ReleaseQuregOperation(reg, dirty=dirty))


def qalloc_int(*, bits: int, name: Optional[str] = None) -> 'Any':
    result = cosim.Quint(qureg=cosim.NamedQureg(length=bits, name=name or ''))
    if bits:
        cosim.emit(AllocQuregOperation(result.qureg))
    return result


class AllocQuregOperation(cosim.FlagOperation):
    def __init__(self,
                 qureg: 'cosim.Qureg',
                 x_basis: bool = False):
        self.qureg = qureg
        self.x_basis = x_basis

    def inverse(self):
        return ReleaseQuregOperation(self.qureg, self.x_basis)

    def __str__(self):
        return 'ALLOC[{}, {}] {}'.format(
            len(self.qureg), 'X' if self.x_basis else 'Z', self.qureg)

    def __repr__(self):
        return 'cosim.AllocQuregOperation({!r})'.format(self.qureg)

    def controlled_by(self, controls):
        raise ValueError("Can't control allocation.")


class ReleaseQuregOperation(cosim.FlagOperation):
    def __init__(self,
                 qureg: 'cosim.Qureg',
                 x_basis: bool = False,
                 dirty: bool = False):
        self.qureg = qureg
        self.x_basis = x_basis
        self.dirty = dirty

    def inverse(self):
        if self.dirty:
            raise NotImplementedError()
        return AllocQuregOperation(self.qureg, self.x_basis)

    def __str__(self):
        return 'RELEASE {} [{}{}]'.format(
            self.qureg,
            'X' if self.x_basis else 'Z',
            ', dirty' if self.dirty else '')

    def controlled_by(self, controls):
        raise ValueError("Can't control deallocation.")
