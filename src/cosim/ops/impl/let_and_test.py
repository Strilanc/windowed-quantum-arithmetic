import cirq

import cosim


def test_let_and_circuit():
    with cosim.Sim(enforce_release_at_zero=False):
        with cosim.LogCirqCircuit() as circuit:
            with cosim.qmanaged_int(bits=3, name='q') as q:
                cosim.emit(cosim.LetAnd(q[0]).controlled_by(q[1] & q[2]))

    cirq.testing.assert_has_diagram(circuit, r"""
q[0]: ---X---
         |
q[1]: ---@---
         |
q[2]: ---@---
        """, use_unicode_characters=False)


def test_del_and_circuit():
    with cosim.Sim(enforce_release_at_zero=False, phase_fixup_bias=True):
        with cosim.LogCirqCircuit() as circuit:
            with cosim.qmanaged_int(bits=3, name='q') as q:
                cosim.emit(cosim.DelAnd(q[0]).controlled_by(q[1] & q[2]))

    cirq.testing.assert_has_diagram(circuit, r"""
q[0]: ---Mxc-------

q[1]: ---------@---
               |
q[2]: ---------Z---
        """, use_unicode_characters=False)


    with cosim.Sim(enforce_release_at_zero=False, phase_fixup_bias=False):
        with cosim.LogCirqCircuit() as circuit:
            with cosim.qmanaged_int(bits=3, name='b') as q:
                cosim.emit(cosim.DelAnd(q[0]).controlled_by(q[1] & q[2]))

    cirq.testing.assert_has_diagram(circuit, r"""
b[0]: ---Mxc---
        """, use_unicode_characters=False)
