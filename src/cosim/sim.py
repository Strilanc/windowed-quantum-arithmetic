import random
from typing import List, Union, Callable, Any, Optional, Tuple, Set, Dict

import cirq
import cosim


def separate_controls(op: 'cosim.Operation') -> 'Tuple[cosim.Operation, cosim.QubitIntersection]':
     if isinstance(op, cosim.ControlledOperation):
         return op.uncontrolled, op.controls
     return op, cosim.QubitIntersection.EMPTY


def _toggle_targets(lvalue: 'cosim.Qureg') -> 'cosim.Qureg':
    return lvalue


class Sim(cosim.Lens):
    def __init__(self,
                 enforce_release_at_zero: bool = True,
                 phase_fixup_bias: Optional[bool] = None,
                 emulate_additions: bool = False):
        super().__init__()
        self._bool_state = {}  # type: Dict[cosim.Qubit, bool]
        self.enforce_release_at_zero = enforce_release_at_zero
        self.phase_fixup_bias = phase_fixup_bias
        self.emulate_additions = emulate_additions

    def snapshot(self):
        return dict(self._bool_state)

    def _read_qubit(self, qubit: 'cosim.Qubit') -> bool:
        return self._bool_state[qubit]

    def _write_qubit(self, qubit: 'cosim.Qubit', new_val: bool):
        self._bool_state[qubit] = new_val

    def _read_quint(self, quint: 'cosim.Quint') -> int:
        t = 0
        for q in reversed(quint):
            t <<= 1
            t |= 1 if self._read_qubit(q) else 0
        return t

    def _write_quint(self, quint: 'cosim.Quint', new_val: int):
        for i, q in enumerate(quint):
            self._write_qubit(q, bool((new_val >> i) & 1))

    def apply_op_via_emulation(self, op: 'cosim.Operation', *, forward: bool = True):
        locs = op.state_locations()
        args = self.resolve_location(locs)
        op.mutate_state(forward, args)
        self.overwrite_location(locs, args)

    def resolve_location(self, loc: Union[cosim.Quint, cosim.Qubit, cosim.Qureg, cosim.ArgsAndKwargs, cosim.IntRValue, cosim.BoolRValue], allow_mutate: bool = True):
        if isinstance(loc, cosim.Qubit):
            val = self._read_qubit(loc)
            if allow_mutate:
                return cosim.Mutable(val)
            return val
        if isinstance(loc, cosim.Qureg):
            val = [self._read_qubit(q) for q in loc]
            if allow_mutate:
                return cosim.Mutable(val)
            return val
        if isinstance(loc, cosim.QubitIntersection):
            return all(self._read_qubit(q) for q in loc)
        if isinstance(loc, cosim.Quint):
            t = self._read_quint(loc)
            if allow_mutate:
                return cosim.Mutable(t)
            return t
        if isinstance(loc, cosim.ArgsAndKwargs):
            return loc.map(self.resolve_location)
        if isinstance(loc, (cosim.IntRValue, cosim.BoolRValue)):
            return loc.val
        if isinstance(loc, (int, bool)):
            return loc
        if isinstance(loc, cosim.ControlledRValue):
            if self.resolve_location(loc.controls):
                return self.resolve_location(loc.rvalue, allow_mutate=False)
            else:
                return 0
        if isinstance(loc, cosim.LookupRValue):
            address = self.resolve_location(loc.address, allow_mutate=False)
            return loc.table.values[address]
        if isinstance(loc, cosim.QuintRValue):
            return self.resolve_location(loc.val, allow_mutate=False)
        if isinstance(loc, cosim.Operation):
            return cosim.SubEffect(
                op=loc,
                args=self.resolve_location(loc.state_locations()))
        raise NotImplementedError(
            "Unrecognized type for resolve_location ({!r}): {!r}".format(type(loc), loc))

    def randomize_location(self, loc: Union[cosim.Quint, cosim.Qubit, cosim.Qureg]):
        if isinstance(loc, cosim.Qubit):
            self._write_qubit(loc, random.random() < 0.5)
        elif isinstance(loc, cosim.Qureg):
            for q in loc:
                self._write_qubit(q, random.random() < 0.5)
        elif isinstance(loc, cosim.Quint):
            for q in loc:
                self._write_qubit(q, random.random() < 0.5)
        elif isinstance(loc, cosim.ControlledRValue):
            if self.resolve_location(loc.controls):
                self.randomize_location(loc.rvalue)
        else:
            raise NotImplementedError(
                "Unrecognized type for randomize_location {!r}".format(loc))

    def overwrite_location(self, loc: Union[cosim.Quint, cosim.Qubit, cosim.Qureg, cosim.ArgsAndKwargs], val: Union['cosim.Mutable', Any]):
        if isinstance(loc, cosim.Qubit):
            self._write_qubit(loc, val.val)
        elif isinstance(loc, cosim.Qureg):
            for q, v in zip(loc, val.val):
                self._write_qubit(q, v)
        elif isinstance(loc, cosim.Quint):
            self._write_quint(loc, val.val)
        elif isinstance(loc, cosim.ArgsAndKwargs):
            loc.zip_map(val, self.overwrite_location)
        elif isinstance(loc, (cosim.IntRValue, cosim.BoolRValue)):
            assert self.resolve_location(loc) == loc.val
        elif isinstance(loc, (bool, int)):
            assert self.resolve_location(loc) == val
        elif isinstance(loc, cosim.ControlledRValue):
            if self.resolve_location(loc.controls):
                self.overwrite_location(loc.rvalue, val)
        elif isinstance(loc, cosim.LookupRValue):
            assert self.resolve_location(loc) == val
        elif isinstance(loc, cosim.QuintRValue):
            assert self.resolve_location(loc) == val
        elif isinstance(loc, cosim.Operation):
            self.overwrite_location(loc.state_locations(), val.args)
        else:
            raise NotImplementedError(
                "Unrecognized type for overwrite_location {!r}".format(loc))

    def modify(self, operation: 'cosim.Operation'):
        op, cnt = separate_controls(operation)

        if isinstance(op, cosim.AllocQuregOperation):
            assert len(cnt) == 0
            for q in op.qureg:
                assert q not in self._bool_state
                if op.x_basis:
                    self._write_qubit(q, random.random() < 0.5)
                else:
                    self._write_qubit(q, False)
            return []

        if self.emulate_additions:
            emulate = False
            if isinstance(op, cosim.InverseOperation):
                if isinstance(op.sub, cosim.SignatureOperation):
                    if op.sub.gate in [cosim.PlusEqualGate,
                                       cosim.IfLessThanThenGate]:
                        emulate = True
            elif isinstance(op, cosim.SignatureOperation):
                if op.gate in [cosim.PlusEqualGate,
                               cosim.IfLessThanThenGate]:
                    emulate = True
            if emulate:
                self.apply_op_via_emulation(operation)
                return []

        if isinstance(op, cosim.ReleaseQuregOperation):
            assert len(cnt) == 0
            for q in op.qureg:
                if self.enforce_release_at_zero and not op.dirty:
                    assert self._read_qubit(q) == 0, 'Failed to uncompute {}'.format(q)
                del self._bool_state[q]
            return []

        if isinstance(op, cosim.MeasureOperation):
            assert len(cnt) == 0
            assert op.raw_results is None
            results = [self._read_qubit(q) for q in op.targets]
            if op.reset:
                for q in op.targets:
                    self._write_qubit(q, False)
            op.raw_results = tuple(results)
            return []

        if isinstance(op, cosim.MeasureXForPhaseKickOperation):
            r = self.phase_fixup_bias
            if r is None:
                r = random.random() < 0.5
            op.result = r
            self._write_qubit(op.target, 0)
            return []

        if isinstance(op, cosim.SignatureOperation):
            if op.gate == cosim.OP_TOGGLE:
                targets = op.args.pass_into(_toggle_targets)
                assert set(targets).isdisjoint(cnt)
                if all(self._read_qubit(q) for q in cnt):
                    for t in targets:
                        self._write_qubit(t, not self._read_qubit(t))
                return []

        if op == cosim.OP_PHASE_FLIP:
            # skip
            return []

        return [operation]
