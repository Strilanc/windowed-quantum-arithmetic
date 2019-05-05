import cirq
import pytest

import cosim


def test_raw_qureg_init():
    eq = cirq.testing.EqualsTester()
    a = cosim.Qubit()
    b = cosim.Qubit()
    eq.add_equality_group(cosim.RawQureg([a, b]), cosim.RawQureg([a, b]))
    eq.add_equality_group(cosim.RawQureg([b, a]))
    eq.add_equality_group(cosim.RawQureg([]))


def test_raw_qureg_getitem_len():
    a = cosim.Qubit()
    b = cosim.Qubit()
    q = cosim.RawQureg([a,  b])
    assert len(q) == 2
    assert q[0] == a
    assert q[:] == q
    assert q[0:2] == q


def test_raw_qureg_repr():
    cirq.testing.assert_equivalent_repr(
        cosim.RawQureg([cosim.Qubit()]),
        setup_code='import cosim'
    )


def test_named_qureg_init():
    eq = cirq.testing.EqualsTester()

    q1 = cosim.NamedQureg('test', 10)
    q2 = cosim.NamedQureg('test', 10)
    assert 'test' in str(q1)
    assert 'test' in str(q2)
    assert str(q1) != str(q2)

    eq.add_equality_group(cosim.NamedQureg('', 5))
    eq.add_equality_group(cosim.NamedQureg('', 5))
    eq.add_equality_group(q1)
    eq.add_equality_group(q2)
    eq.add_equality_group(cosim.NamedQureg('q', 2))

    h = cosim.UniqueHandle('test')
    eq.add_equality_group(cosim.NamedQureg(h, 10), cosim.NamedQureg(h, 10))
    eq.add_equality_group(cosim.NamedQureg(h, 5))


def test_named_qureg_get_item_len():
    h = cosim.UniqueHandle('a')
    q = cosim.NamedQureg(h, 5)
    assert q[0] == cosim.Qubit(h, 0)
    assert len(q) == 5
    assert q[:] == q
    assert q[2:4] == cosim.RangeQureg(q, range(2, 4))


def test_named_qureg_repr():
    cirq.testing.assert_equivalent_repr(
        cosim.NamedQureg('a', 3),
        setup_code='import cosim')


def test_range_qureg_init():
    eq = cirq.testing.EqualsTester()

    a = cosim.NamedQureg('a', 5)
    b = cosim.NamedQureg('b', 5)
    eq.add_equality_group(a[:2])
    eq.add_equality_group(a[:3])
    eq.add_equality_group(b[:3])


def test_range_qureg_getitem_len():
    h = cosim.UniqueHandle('a')
    a = cosim.NamedQureg(h, 5)
    r = cosim.RangeQureg(a, range(1, 3))
    assert r[0] == cosim.Qubit(h, 1);
    assert r[1] == cosim.Qubit(h, 2);
    assert r[-1] == cosim.Qubit(h, 2);
    with pytest.raises(IndexError):
        _ = r[2]


def test_range_qureg_repr():
    h = cosim.UniqueHandle('a')
    a = cosim.NamedQureg(h, 5)
    r = cosim.RangeQureg(a, range(1, 3))
    cirq.testing.assert_equivalent_repr(
        r,
        setup_code='import cosim')
