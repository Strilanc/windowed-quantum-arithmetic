from typing import Union

import cosim


def pad(base: 'Union[cosim.Qureg, cosim.Quint]', *, min_len: int) -> 'cosim.PaddedQureg':
    assert min_len >= 0
    if isinstance(base, cosim.Quint):
        return PaddedQureg(base.qureg, min_len)
    else:
        return PaddedQureg(base, min_len)


def pad_all(*bases: 'Union[cosim.Qureg, cosim.Quint]',
            min_len: int) -> 'cosim.MultiWith':
    assert min_len >= 0
    return cosim.MultiWith(pad(b, min_len=min_len) for b in bases)


class PaddedQureg:
    def __init__(self, base: 'cosim.Qureg', min_len: int):
        self.base = base
        self.padded = None
        self.min_len = min_len

    def __len__(self):
        return len(self.padded)

    def __getitem__(self, item):
        return self.padded[item]

    def __enter__(self) -> 'cosim.Qureg':
        if len(self.base) >= self.min_len:
            return self.base

        assert self.padded is None
        sub_name = str(self.base) if isinstance(self.base, cosim.NamedQureg) else ''
        q = cosim.NamedQureg('{}_pad'.format(sub_name), self.min_len - len(self.base))
        cosim.emit(cosim.AllocQuregOperation(q))
        self.padded = q
        return cosim.RawQureg(list(self.base) + list(q))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if len(self.base) >= self.min_len:
            return

        if exc_type is None:
            assert self.padded is not None
            cosim.emit(cosim.ReleaseQuregOperation(self.padded))
            self.padded = None
