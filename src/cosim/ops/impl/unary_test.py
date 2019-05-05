import cirq

import cosim


def test_let_unary_circuit():
    with cosim.Sim():
        with cosim.LogCirqCircuit() as circuit:
            with cosim.qmanaged_int(bits=3, name='b') as b:
                with cosim.qmanaged_int(bits=8, name='u') as u:
                    with cosim.qmanaged(cosim.Qubit(name='_c')) as c:
                            cosim.emit(cosim.LetUnary(
                                binary=b,
                                lvalue=u).controlled_by(c))

    cirq.testing.assert_has_diagram(circuit, r"""
_c: -----@-----------------------------------------------------------
         |
b[0]: ---|---@-------------------------------------------------------
         |   |
b[1]: ---|---|-------@-------@---------------------------------------
         |   |       |       |
b[2]: ---|---|-------|-------|-------@-------@-------@-------@-------
         |   |       |       |       |       |       |       |
u[0]: ---X---@---X---@---X---|-------@---X---|-------|-------|-------
             |   |   |   |   |       |   |   |       |       |
u[1]: -------X---@---|---|---@---X---|---|---@---X---|-------|-------
                     |   |   |   |   |   |   |   |   |       |
u[2]: ---------------X---@---|---|---|---|---|---|---@---X---|-------
                             |   |   |   |   |   |   |   |   |
u[3]: -----------------------X---@---|---|---|---|---|---|---@---X---
                                     |   |   |   |   |   |   |   |
u[4]: -------------------------------X---@---|---|---|---|---|---|---
                                             |   |   |   |   |   |
u[5]: ---------------------------------------X---@---|---|---|---|---
                                                     |   |   |   |
u[6]: -----------------------------------------------X---@---|---|---
                                                             |   |
u[7]: -------------------------------------------------------X---@---
        """, use_unicode_characters=False)


def test_del_unary_circuit():
    with cosim.Sim(phase_fixup_bias=True):
        with cosim.LogCirqCircuit() as circuit:
            with cosim.qmanaged_int(bits=3, name='b') as b:
                with cosim.qmanaged_int(bits=8, name='u') as u:
                    with cosim.qmanaged(cosim.Qubit(name='_c')) as c:
                            cosim.emit(cosim.LetUnary(
                                binary=b,
                                lvalue=u).inverse().controlled_by(c))

    cirq.testing.assert_has_diagram(circuit, r"""
_c: -------------------------------------------------------------------------------------------------------------Z---

b[0]: -------------------------------------------------------------------------------------------------Z-------------
                                                                                                       |
b[1]: ---------------------------------------------------------------------Z-------------Z-------------|-------------
                                                                           |             |             |
b[2]: -------------Z-------------Z-------------Z-------------Z-------------|-------------|-------------|-------------
                   |             |             |             |             |             |             |
u[0]: -------------|-------------|-------------|---X---------@-------------|---X---------@---X---------@---Mxc-------
                   |             |             |   |                       |   |             |
u[1]: -------------|-------------|---X---------@---|-------------X---------@---|-------------@---Mxc-----------------
                   |             |   |             |             |             |
u[2]: -------------|---X---------@---|-------------|-------------|-------------@---Mxc-------------------------------
                   |   |             |             |             |
u[3]: ---X---------@---|-------------|-------------|-------------@---Mxc---------------------------------------------
         |             |             |             |
u[4]: ---|-------------|-------------|-------------@---Mxc-----------------------------------------------------------
         |             |             |
u[5]: ---|-------------|-------------@---Mxc-------------------------------------------------------------------------
         |             |
u[6]: ---|-------------@---Mxc---------------------------------------------------------------------------------------
         |
u[7]: ---@---Mxc-----------------------------------------------------------------------------------------------------
        """, use_unicode_characters=False)

    del u
    del b
    del c
    with cosim.Sim(phase_fixup_bias=False):
        with cosim.LogCirqCircuit() as circuit:
            with cosim.qmanaged_int(bits=3, name='b') as b:
                with cosim.qmanaged_int(bits=8, name='u') as u:
                    with cosim.qmanaged(cosim.Qubit(name='_c')) as c:
                            cosim.emit(cosim.LetUnary(
                                binary=b,
                                lvalue=u).inverse().controlled_by(c))

    cirq.testing.assert_has_diagram(circuit, r"""
u[0]: ---------------------------------X-------------------X---------X---------Mxc---
                                       |                   |         |
u[1]: -----------------------X---------|---------X---------|---------@---Mxc---------
                             |         |         |         |
u[2]: -------------X---------|---------|---------|---------@---Mxc-------------------
                   |         |         |         |
u[3]: ---X---------|---------|---------|---------@---Mxc-----------------------------
         |         |         |         |
u[4]: ---|---------|---------|---------@---Mxc---------------------------------------
         |         |         |
u[5]: ---|---------|---------@---Mxc-------------------------------------------------
         |         |
u[6]: ---|---------@---Mxc-----------------------------------------------------------
         |
u[7]: ---@---Mxc---------------------------------------------------------------------
        """, use_unicode_characters=False)
