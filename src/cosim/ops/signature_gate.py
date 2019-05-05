import inspect
from typing import List, Union, Any, get_type_hints, TypeVar

import cosim

T = TypeVar('T')


SignatureGateArgTypes = Union[cosim.RValue[Any], 'cosim.Operation']


class SignatureGate:
    def register_name_prefix(self):
        return ''

    def signature(self) -> List[type]:
        sig = inspect.signature(self.emulate)
        type_hints = get_type_hints(self.emulate)
        result = []
        saw_forward = False
        for p in sig.parameters.values():
            if not saw_forward:
                assert p.name == 'forward'
                saw_forward = True
                continue
            assert p.name in type_hints
            t = type_hints[p.name]
            result.append(t)
        assert saw_forward
        return result

    def operation(self, *args, **kwargs) -> 'cosim.Operation':
        v = cosim.ArgsAndKwargs(args, kwargs).match_parameters(self.do, skip=1)
        def wrap_constants(x: cosim.ArgParameter):
            if x.parameter_type == cosim.Quint:
                if isinstance(x.arg, int):
                    return cosim.IntRValue(x.arg)
            if x.parameter_type == cosim.Qubit:
                if isinstance(x.arg, bool):
                    return cosim.BoolRValue(x.arg)
            return x.arg
        return cosim.SignatureOperation(self, v.map(wrap_constants))

    def __call__(self, *args, **kwargs):
        return self.operation(*args, **kwargs)

    def emulate(self, forward: bool, *args, **kwargs):
        raise NotImplementedError()

    def do(self, controls: 'cosim.QubitIntersection', *args, **kwargs):
        raise NotImplementedError()

    def describe(self, *args) -> str:
        raise NotImplementedError()

    def __str__(self):
        try:
            return self.describe(*[str(e) for e in self.signature()])
        except TypeError:
            return '[DESCRIBE-ERR] ' + object.__str__(self)
