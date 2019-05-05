"""Simulates factoring with Shor's algorithm, to estimate repetition counts.

Requires:
    python 3.5
    matplotlib
    sympy
"""

from typing import Optional, List, Dict, Callable, Any, NamedTuple, Tuple

from collections import defaultdict

import fractions
import math
import random
import sys

import matplotlib.pyplot as plt
import sympy


USAGE = """Usage:
    python sim-factor.py [--plot] [--min=#] [--max=#] [--rep=#]

If --plot is not set, simulates and prints csv data to stdout.
If --plot is set, reads csv data from stdin and plots it.

Meaning of numeric flags (only relevant when simulating):
    min defaults to 1, determines minimum problem bit size.
    max defaults to 80, determines maximum problem bit size.
    rep defaults to 1000, determines samples per bit size.

Generate samples:
    python sim-factor.py

Save samples:
    python sim-factor.py > data.csv

Plot saved samples:
    python sim-factor.py --plot < data.csv
"""

CSV_HEADER = "problem size (bits),repetitions,record,factor1,factor2"


Factors = NamedTuple(
    'Factors',
    [
        ('a', int),
        ('b', int),
    ]
)


SimulatedRun = NamedTuple(
    'SimulatedRun',
    [
        ('problem', 'FactorizationProblem'),
        ('quantum_sample_count', int),
        ('record', str),
        ('factors', Factors),
    ]
)


def simulate_factoring_repetition_samples(
        min_bit_size: int,
        max_bit_size: int,
        samples_per_size: int,
        output: Callable[[SimulatedRun], Any] = lambda a, b: None
) -> Dict[int, List[int]]:
    result = {}
    for bits in range(min_bit_size, max_bit_size + 1):
        bit_result = []
        print('Working on bit size {}'.format(bits),
              end='',
              file=sys.stderr,
              flush=True)
        for k in range(samples_per_size):
            if k % (samples_per_size // 50 + 1) == 0:
                print('.', end='', file=sys.stderr, flush=True)
            problem = FactorizationProblem.random_problem(bits)
            run = count_samples_during_simulated_factoring(problem)
            bit_result.append(run)
            output(run)
        print(file=sys.stderr, flush=True)
        result[bits] = bit_result
    return result


def count_samples_during_simulated_factoring(
        problem: 'FactorizationProblem') -> SimulatedRun:
    samples = 0
    if problem.modulus == 1:
        return SimulatedRun(
            problem, 0, '(trivial)', Factors(1, 1))
    if problem.modulus % 2 == 0:
        return SimulatedRun(
            problem, 0, '(even)', Factors(problem.modulus // 2, 2))

    record = ''
    for _ in range(1000):
        base = random.randint(2, problem.modulus - 1)
        c = math.gcd(base, problem.modulus)
        if c != 1:
            factors = Factors(c, problem.modulus // c)
            assert factors[0] * factors[1] == problem.modulus
            return SimulatedRun(problem, samples, record + '(gcd)', factors)

        sampler = problem.shor_sampler(base)
        factors, rec = attempt_factor_via_two_samples_using_base(
            base, problem.modulus, sampler)

        record += rec
        samples += sampler.sample_count
        if factors is not None:
            assert factors[0] * factors[1] == problem.modulus
            return SimulatedRun(problem, samples, record, factors)
    raise RuntimeError('Failed to factor {} after {} samples'.format(
        problem.modulus, samples))


def attempt_factor_via_two_samples_using_base(
        base: int,
        modulus: int,
        sampler: 'ShorSampler'
        ) -> Tuple[Optional[Factors], str]:
    # First sample.
    s1 = sampler.sample()
    p1 = attempt_recover_period_from_sample(base, s1, modulus)
    if p1 is not None:
        return attempt_factor_from_period(base, p1, modulus), 'i'

    # Second sample.
    s2 = sampler.sample()
    p2 = attempt_recover_period_from_sample(base, s2, modulus)
    if p2 is not None:
        return attempt_factor_from_period(base, p2, modulus), '_i'

    # Combined sample.
    s3 = int(sympy.lcm(s1, s2))
    p3 = attempt_recover_period_from_sample(base, s3, modulus)
    if p3 is not None:
        return attempt_factor_from_period(base, p3, modulus), '_C'

    return None, '_!'


def attempt_recover_period_from_sample(base: int,
                                       sample: int,
                                       modulus: int) -> Optional[int]:
    """A sampled value may omit small factors of the actual period.

    Args:
        base: The base in pow(base, period, modulus) == 1.
        sample: The sampled value that's supposed to equal the period.
        modulus: The modulus in pow(base, period, modulus) == 1.

    Returns:
        A value for period that satisfies pow(base, period, modulus) == 1, or
        else None if it the sampled value is too different from the true
        period.
    """
    for missing_multiple in range(1, 100):
        if pow(base, sample * missing_multiple, modulus) == 1:
            return sample * missing_multiple
    return None


def attempt_factor_from_period(base: int,
                               period: int,
                               modulus: int
                               ) -> Optional[List[int]]:
    """Attempts to recover a factor using the solution to b^r = 1 (mod N)."""
    if period % 2 == 1:
        return None
    s = pow(base, period // 2, modulus)
    if s == modulus - 1:
        return None

    factor = math.gcd(s - 1, modulus)
    other_factor = modulus // factor
    assert factor != 1 and factor != modulus
    assert factor * other_factor == modulus
    return [factor, other_factor]


class ShorSampler:
    """Emulates sampling from the quantum part of Shor's algorithm."""

    def __init__(self, secretly_known_period: int):
        self._secretly_known_period = secretly_known_period
        self.sample_count = 0

    def sample(self) -> int:
        self.sample_count += 1
        p = self._secretly_known_period
        k = random.randint(0, p-1)
        d = fractions.Fraction(k, p).denominator
        return d


class FactorizationProblem:
    """A number to factor, and side channel information to help emulation."""

    def __init__(self, factor1: int, factor2: int):
        assert math.gcd(factor1, factor2) == 1

        self.modulus = factor1 * factor2

        # https://en.wikipedia.org/wiki/Euler's_theorem
        self._secretly_known_period_multiple = int(
            sympy.totient(factor1) * sympy.totient(factor2))
        self._secretly_known_period_multiple_factors = sympy.factorint(
            self._secretly_known_period_multiple)

    def shor_sampler(self, base: int) -> ShorSampler:
        """Returns an object to emulate running the quantum part of factoring.

        The object is specialized to the given base value.
        """

        period_multiple = self._secretly_known_period_multiple
        assert pow(base, period_multiple, self.modulus) == 1

        # Remove unnecessary factors.
        for k, v in self._secretly_known_period_multiple_factors.items():
            for _ in range(v):
                if pow(base, period_multiple // k, self.modulus) == 1:
                    period_multiple //= k
        assert pow(base, period_multiple, self.modulus) == 1

        return ShorSampler(period_multiple)

    @staticmethod
    def random_problem(bits: int) -> 'FactorizationProblem':
        """Produces a factorization problem for the given bit size.

        Generates two distinct random primes of equal or adjacent bit sizes, and
        multiplies them together to produce the factoring problem.
        """
        if bits <= 1:
            return FactorizationProblem(1, 1)
        if bits <= 2:
            return FactorizationProblem(2, 1)
        if bits <= 3:
            return FactorizationProblem(2, 3)

        bits = max(bits, 2)
        h1 = bits // 2
        h2 = bits - h1
        while True:
            prime_1 = sympy.randprime(1 << (h1 - 1), 2 << h1)
            prime_2 = sympy.randprime(1 << (h2 - 1), 2 << h2)
            if prime_2 == prime_1:
                continue
            if (prime_1 * prime_2).bit_length() != bits:
                continue
            return FactorizationProblem(prime_1, prime_2)


def read_csv_data_from(read) -> Dict[int, List[int]]:
    """Loads data generated from previous simulations."""
    lines = read.readlines()
    results = defaultdict(lambda: [])
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == CSV_HEADER:
            continue
        parts = line.split(',')
        results[int(parts[0])].append(int(parts[1]))
    return results


def plot_results(results: Dict[int, List[int]]) -> None:
    """Plots repetition data generated from simulations.

    The plot is a sample mean curve and perturbed scatter plot points.
    """
    xs = []
    ys = []
    x_avg = []
    y_avg = []
    for k in sorted(results.keys()):
        v = results[k]
        for e in v:
            xs.append(k + random.random() - 0.5)
            ys.append(e + random.random() - 0.5)
        x_avg.append(k)
        y_avg.append(sum(v) / len(v))
    y_max = max(int(e + 1.5) for e in ys)
    x_max = ((max(xs) + 9)//10)*10 + 0.5
    plt.yticks([0, 1.5] + list(range(5, y_max + 2, 5)))
    plt.grid(True)
    plt.ylim(-0.5, y_max)
    plt.xlim(0, x_max)
    plt.title("Repetitions of the quantum part of Shor's algorithm during "
              "simulated factorings")
    plt.xlabel('problem size (bits)')
    plt.ylabel('repetitions')
    plt.scatter(xs, ys, s=0.5)
    plt.plot(x_avg, y_avg, color='k', linewidth=4)
    plt.show()


def parse_args() -> Dict[str, Optional[str]]:
    known = {
        'plot',
        'min',
        'max',
        'rep',
    }
    result = {}
    for k in sys.argv[1:]:
        if not k.startswith('--'):
            raise ValueError()
        k = k[2:]
        if '=' in k:
            k, v = k.split('=')
        else:
            v = None
        if k not in known:
            raise ValueError()
        result[k] = v
    return result


def main():
    try:
        args = parse_args()
        if args.get('plot') is not None:
            raise ValueError()
        plot = 'plot' in args
        min_bit_size = int(args.get('min', 1))
        max_bit_size = int(args.get('max', 80))
        samples_per_size = int(args.get('rep', 1000))
    except:
        print('\033[31m{}\033[0m'.format(USAGE), file=sys.stderr)
        return

    if plot:
        results = read_csv_data_from(sys.stdin)
        plot_results(results)
    else:
        print(CSV_HEADER)
        try:
            results = simulate_factoring_repetition_samples(
                min_bit_size=min_bit_size,
                max_bit_size=max_bit_size,
                samples_per_size=samples_per_size,
                output=lambda run: print('{}, {}, "{}", {}, {}, {}'.format(
                    run.problem.modulus.bit_length(),
                    run.quantum_sample_count,
                    run.record,
                    run.problem.modulus,
                    run.factors[0],
                    run.factors[1]), flush=True))
        except KeyboardInterrupt:
            return


if __name__ == '__main__':
    main()
