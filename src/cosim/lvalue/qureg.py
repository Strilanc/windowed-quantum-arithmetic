from typing import Optional, Iterable, Union

import cirq

import cosim


class Qureg:
    def __len__(self):
        raise NotImplementedError()

    def __getitem__(self, item):
        raise NotImplementedError()


@cirq.value_equality
class RawQureg(Qureg):
    def __init__(self, qubits: Iterable['cosim.Qubit']):
        self.qubits = tuple(qubits)

    def _value_equality_values_(self):
        return self.qubits

    def __len__(self):
        return len(self.qubits)

    def __getitem__(self, item):
        r = range(len(self))[item]
        if isinstance(r, range):
            return RangeQureg(self, r)
        return self.qubits[r]

    def __str__(self):
        return '[{}]'.format(', '.join(str(e) for e in self.qubits))

    def __repr__(self):
        return 'cosim.RawQureg({!r})'.format(self.qubits)


@cirq.value_equality
class NamedQureg(Qureg):
    def __init__(self, name: 'Union[cosim.UniqueHandle, str]', length: int):
        self.name = name if isinstance(name, cosim.UniqueHandle) else cosim.UniqueHandle(name)
        self.length = length

    def _value_equality_values_(self):
        return self.name, self.length

    def __len__(self):
        return self.length

    def __getitem__(self, item):
        r = range(self.length)[item]
        if isinstance(r, int):
            return cosim.Qubit(self.name, r)
        if isinstance(r, range):
            return RangeQureg(self, r)
        return NotImplemented

    def __repr__(self):
        return 'cosim.NamedQureg({!r}, {!r})'.format(self.name, self.length)

    def __str__(self):
        return str(self.name)


@cirq.value_equality
class RangeQureg(Qureg):
    def __new__(cls, sub: Qureg, index_range: range):
        if (index_range.start == 0 and
                index_range.stop == len(sub) and
                index_range.step == 1):
            return sub
        return super().__new__(cls)

    def __init__(self, sub: Qureg, index_range: range):
        self.sub = sub
        self.range = index_range

    def _value_equality_values_(self):
        return self.sub, self.range

    def __len__(self):
        return len(self.range)

    def __getitem__(self, item):
        r = self.range[item]
        if isinstance(r, int):
            return self.sub[r]
        if isinstance(r, range):
            return RangeQureg(self.sub, r)
        return NotImplemented

    def __repr__(self):
        return 'cosim.RangeQureg({!r}, {!r})'.format(self.sub, self.range)

    def __str__(self):
        return '{}[{}:{}{}]'.format(
            self.sub,
            '' if self.range.start == 0 else self.range.start,
            '' if self.range.stop == len(self.sub) else self.range.stop,
            '' if self.range.step == 1 else ':{}'.format(self.range.step))
