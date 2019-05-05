import collections
from typing import List, Union, Callable, Any, Optional, Tuple

import cirq
import cosim


def separate_controls(op: 'cosim.Operation') -> 'Tuple[cosim.Operation, cosim.QubitIntersection]':
    if isinstance(op, cosim.ControlledOperation):
        return op.uncontrolled, op.controls
    return op, cosim.QubitIntersection.EMPTY

def _toggle_targets(lvalue: 'cosim.Qureg') -> 'cosim.Qureg':
    return lvalue

class MultiNotGate(cirq.Gate):
    def _circuit_diagram_info_(self, args: cirq.CircuitDiagramInfoArgs):
        return ['X'] * args.known_qubit_count
class MeasureXFixupGate(cirq.Gate):
    def _circuit_diagram_info_(self, args):
        return 'Mxc'
class MeasureResetGate(cirq.Gate):
    def _circuit_diagram_info_(self, args):
        return 'Mr'


class LogCirqCircuit(cosim.Lens):
    def __init__(self):
        super().__init__()
        self.circuit = cirq.Circuit()

    def _val(self):
        return self.circuit

    def modify(self, operation: 'cosim.Operation'):
        unknown = False

        op, controls = separate_controls(operation)
        if isinstance(op, cosim.MeasureOperation):
            qubits = [cirq.NamedQubit(str(q)) for q in op.targets]
            if op.reset:
                self.circuit.append(MeasureResetGate()(*qubits))
            else:
                self.circuit.append(cirq.measure(*qubits))

        elif isinstance(op, cosim.MeasureXForPhaseKickOperation):
            q = op.target
            q2 = cirq.NamedQubit(str(q))
            self.circuit.append(MeasureXFixupGate()(q2))


        elif op == cosim.OP_PHASE_FLIP:
            if len(controls):
                g = cirq.Z
                for _ in range(len(controls) - 1):
                    g = cirq.ControlledGate(g)
                ctrls = [cirq.NamedQubit(str(q)) for q in controls]
                self.circuit.append(g(*ctrls))

        elif isinstance(op, cosim.SignatureOperation):
            if op.gate == cosim.OP_TOGGLE:
                g = MultiNotGate()
                for _ in range(len(controls)):
                    g = cirq.ControlledGate(g)
                ctrls = [cirq.NamedQubit(str(q)) for q in controls]
                targets = op.args.pass_into(_toggle_targets)
                if len(targets):
                    targs = [cirq.NamedQubit(str(q)) for q in targets]
                    self.circuit.append(g(*ctrls, *targs))
            else:
                unknown = True

        elif isinstance(op, cosim.AllocQuregOperation):
            pass
        elif isinstance(op, cosim.ReleaseQuregOperation):
            pass
        else:
            unknown = True

        # if unknown:
        #     raise NotImplementedError("Unrecognized operation: {!r}".format(operation))

        return [operation]


class CountNots(cosim.Lens):
    def __init__(self):
        super().__init__()
        self.counts = collections.Counter()

    def _val(self):
        return self.counts

    def modify(self, operation: 'cosim.Operation'):
        op, controls = separate_controls(operation)

        if isinstance(op, cosim.SignatureOperation):
            if op.gate == cosim.OP_TOGGLE:
                targets = op.args.pass_into(_toggle_targets)
                if len(controls) > 1:
                    self.counts[1] += 2 * (len(targets) - 1)
                    self.counts[len(controls)] += 1
                else:
                    self.counts[len(controls)] += len(targets)

        return [operation]
