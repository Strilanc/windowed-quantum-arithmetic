import cirq
import pytest

import cosim


def test_init():
    eq = cirq.testing.EqualsTester()

    q1 = cosim.Qubit('test', 10)
    q2 = cosim.Qubit('test', 10)
    assert 'test' in str(q1)
    assert 'test' in str(q2)
    assert str(q1) != str(q2)

    eq.add_equality_group(cosim.Qubit())
    eq.add_equality_group(cosim.Qubit())
    eq.add_equality_group(q1)
    eq.add_equality_group(q2)
    eq.add_equality_group(cosim.Qubit('q'))

    h = cosim.UniqueHandle('test')
    eq.add_equality_group(cosim.Qubit(h), cosim.Qubit(h))
    eq.add_equality_group(cosim.Qubit(h, 5))
    eq.add_equality_group(cosim.Qubit(h, 0), cosim.Qubit(h, 0))


def test_and():
    a = cosim.Qubit('a')
    b = cosim.Qubit('b')
    c = cosim.Qubit('c')
    d = cosim.Qubit('d')
    s = cosim.QubitIntersection((c, d))
    assert a & b == cosim.QubitIntersection((a, b))
    assert a & b & c == cosim.QubitIntersection((a, b, c))
    assert a & s == cosim.QubitIntersection((a, c, d))


def test_ixor():
    q = cosim.Qubit('q')
    c = cosim.Qubit('c')
    d = cosim.Qubit('d')

    # Unsupported classes cause type error.
    with pytest.raises(TypeError):
        q ^= None
    class C:
        pass
    with pytest.raises(TypeError):
        q ^= C()

    # False does nothing. True causes toggle.
    with cosim.capture() as out:
        q ^= False
    assert out == []
    with cosim.capture() as out:
        q ^= True
    assert out == [cosim.OP_TOGGLE(cosim.RawQureg([q]))]

    # Qubit and qubit intersection cause controlled toggle.
    with cosim.capture() as out:
        q ^= c
    assert out == [cosim.OP_TOGGLE(cosim.RawQureg([q])).controlled_by(c)]
    with cosim.capture() as out:
        q ^= c & d
    assert out == [cosim.OP_TOGGLE(cosim.RawQureg([q])).controlled_by(c & d)]

    # Classes can specify custom behavior via __rixor__.
    class Rixor:
        def __rixor__(self, other):
            cosim.emit('yay!')
            return other
    with cosim.capture() as out:
        q ^= Rixor()
    assert out == ['yay!']


def test_repr():
    cirq.testing.assert_equivalent_repr(
        cosim.Qubit('test'),
        setup_code='import cosim')

    cirq.testing.assert_equivalent_repr(
        cosim.Qubit('test', 10),
        setup_code='import cosim')
