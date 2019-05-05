import random

import cirq

import cosim


def test_plus_equal_gate_circuit():
    with cosim.Sim(enforce_release_at_zero=False):
        with cosim.LogCirqCircuit() as circuit:
            with cosim.qmanaged_int(bits=3, name='a') as a:
                with cosim.qmanaged_int(bits=4, name='t') as t:
                    with cosim.qmanaged(cosim.Qubit(name='_c')) as c:
                        cosim.emit(
                            cosim.PlusEqualGate(lvalue=t, offset=a, carry_in=c))

    cirq.testing.assert_has_diagram(circuit, r"""
_c: -----X-------@---------------------------------------------------------------@---@-------X---
         |       |                                                               |   |       |
a[0]: ---@---@---X---X-------@-----------------------------------@---@-------X---X---|---@---@---
             |   |   |       |                                   |   |       |   |   |   |
a[1]: -------|---|---@---@---X---X-------@-------@---@-------X---X---|---@---@---|---|---|-------
             |   |       |   |   |       |       |   |       |   |   |   |       |   |   |
a[2]: -------|---|-------|---|---@---@---X---@---X---|---@---@---|---|---|-------|---|---|-------
             |   |       |   |       |   |   |   |   |   |       |   |   |       |   |   |
t[0]: -------X---@-------|---|-------|---|---|---|---|---|-------|---|---|-------@---X---X-------
                         |   |       |   |   |   |   |   |       |   |   |
t[1]: -------------------X---@-------|---|---|---|---|---|-------@---X---X-----------------------
                                     |   |   |   |   |   |
t[2]: -------------------------------X---@---|---@---X---X---------------------------------------
                                             |
t[3]: ---------------------------------------X---------------------------------------------------
        """, use_unicode_characters=False)


def test_vs_emulation():
    with cosim.Sim(enforce_release_at_zero=False) as sim:
        bits = 4
        with cosim.qmanaged_int(bits=bits, name='lvalue') as lvalue:
            for _ in range(10):
                sim.randomize_location(lvalue)

                old_state = sim.snapshot()
                op = cosim.PlusEqualGate(lvalue=lvalue,
                                         offset=random.randint(0, 1 << bits),
                                         carry_in=random.random() < 0.5)
                cosim.emit(op)
                sim.apply_op_via_emulation(op, forward=False)
                assert sim.snapshot() == old_state
