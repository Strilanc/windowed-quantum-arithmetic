import random

import cirq

import cosim


def test_vs_emulation():
    with cosim.Sim(enforce_release_at_zero=False) as sim:
        bits = 4
        with cosim.qmanaged_int(bits=bits, name='lvalue') as lvalue:
            for _ in range(10):
                sim.randomize_location(lvalue)

                old_state = sim.snapshot()
                op = cosim.PlusEqualTimesGate(
                    lvalue=lvalue,
                    quantum_factor=random.randint(0, 1 << bits),
                    const_factor=random.randint(0, 1 << bits))
                cosim.emit(op)
                sim.apply_op_via_emulation(op, forward=False)
                assert sim.snapshot() == old_state
