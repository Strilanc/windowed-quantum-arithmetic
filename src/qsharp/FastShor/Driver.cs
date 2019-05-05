using System;
using System.Threading;
using Microsoft.Quantum.Simulation.Core;
using Microsoft.Quantum.Simulation.Simulators;
using Microsoft.Quantum;
using Microsoft.Quantum.Simulation.Simulators.QCTraceSimulators;
using System.Diagnostics;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Quantum.Canon;

namespace FastShor {
    struct DoOp {
        public readonly string Name;
        public readonly QubitReg Controls;
        public readonly bool Adjoint;
        public readonly object[] Args;
        public DoOp(string Name, bool Adjoint, QubitReg Controls, object[] Args) {
            this.Name = Name;
            this.Controls = Controls;
            this.Adjoint = Adjoint;
            this.Args = Args;
        }
    }

    class NamedAllocations {
        public readonly List<(string, int[])> allocations = new List<(string, int[])>();
        public long[] latestTable = new long[0];

        public string Alloc(IEnumerable<int> qubits) {
            for (var c = 'a'; ; c++) {
                if (allocations.Any(e => e.Item1 == c.ToString())) {
                    continue;
                }
                allocations.Add((c.ToString(), qubits.ToArray()));
                return c.ToString();
            }
        }

        public string Release(IEnumerable<int> qubits) {
            var q = qubits.ToHashSet();
            for (var i = 0; i < allocations.Count; i++) {
                if (q.SetEquals(allocations[i].Item2)) {
                    var result = allocations[i].Item1;
                    allocations.RemoveAt(i);
                    return result;
                }
            }
            return null;
        }

        public QubitReg Rewrite(QubitReg qureg) {
            var q = qureg.offsets.ToHashSet();
            foreach (var (c, qs) in allocations) {
                if (q.IsSubsetOf(qs)) {
                    var qubits = qs.Select(e => Array.IndexOf(qs, e)).ToArray();
                    return new QubitReg(
                        c,
                        "",
                        qubits,
                        qubits.SequenceEqual(Enumerable.Range(0, qs.Length)));
                }
            }
            return qureg;
        }
    }

    struct QubitReg {
        public readonly int[] offsets;
        public readonly string name;
        public readonly string tag;
        public readonly bool allInTheName;
        public QubitReg(string name, string tag, int[] offsets, bool allInTheName = false) {
            this.name = name;
            this.offsets = offsets;
            this.tag = tag;
            this.allInTheName = allInTheName;
        }

        public int Length {
            get {
                return offsets.Length;
            }
        }
        public override string ToString() {
            if (allInTheName) {
                return name;
            }
            return $"{tag}{name}{DriverUtil.DescribeIdRange(offsets)}";
        }
    }
    public static class Driver {
        static int[] QubitsToIds(System.Collections.IEnumerable qubits) {
            var result = new List<int>();
            foreach (var e in qubits) {
                result.Add(((Qubit)e).Id);
            }
            return result.ToArray();
        }

        static string DescribeQubits(System.Collections.IEnumerable qubits) {
            return $"reg{DriverUtil.DescribeIdRange(QubitsToIds(qubits))}";
        }
        static string DescribeArray(object x, NamedAllocations alloc, bool includeOuter = true) {
            if (x is object[]) {
                var s = string.Join(", ", (x as object[]).Select(e => DescribeArray(e, alloc)));
                if (includeOuter) {
                    return "[" + s + "]";
                }
                return s;
            } else if (x is QubitReg) {
                return alloc.Rewrite((QubitReg)x).ToString();
            } else {
                return x.ToString();
            }
        }
        static object unpackTuple(object vt) {
            var result = unpackTupleOnce(vt);
            if (result == vt) {
                return result;
            } else if (result is object[]) {
                var x = (object[])result;
                return x.Select(unpackTuple).ToArray();
            } else {
                return unpackTuple(result);
            }
        }
        static object unpackTupleOnce(object vt) {
            dynamic v = vt;
            var t = vt.GetType().IsGenericType ? v.GetType().GetGenericTypeDefinition() : null;
            if (vt is QVoid) {
                return new object[0];
            } else if (t == typeof(ControlledOperation<,>.In)) {
                return (object) v.Value;
            } else if (t == typeof(ValueTuple<>)) {
                return new object[] { v.Item1 };
            } else if (t == typeof(ValueTuple<,>)) {
                return new object[] { v.Item1, v.Item2 };
            } else if (t == typeof(ValueTuple<,,>)) {
                return new object[] { v.Item1, v.Item2, v.Item3 };
            } else if (t == typeof(ValueTuple<,,,>)) {
                return new object[] { v.Item1, v.Item2, v.Item3, v.Item4 };
            } else if (t == typeof(QArray<>)) {
                dynamic arr = System.Linq.Enumerable.ToArray(v);
                object[] res = new object[arr.Length];
                for (var i = 0; i < arr.Length; i++) {
                    res[i] = (object)arr[i];
                }
                if (res.All(e => e.ToString().StartsWith("q:"))) {
                    return new QubitReg("", "reg", QubitsToIds(res));
                }
                return res;
            } else if (vt is LittleEndian) {
                return new QubitReg("", "int", QubitsToIds((vt as LittleEndian).Data));
            } else if (vt is CosetLittleEndian) {
                return new QubitReg("", "coset", QubitsToIds((vt as CosetLittleEndian).Data.Data));
            } else if (vt is QubitReg || vt is long) {
                return vt;
            } else if (vt.ToString().StartsWith("q:")) {
                return new QubitReg("", "qubit", new[] { ((Qubit) vt).Id });
            } else if (vt is Pauli) {
                return vt;
            }
            //return vt;
            throw new ArgumentException();
        }

        static DoOp Decompile(ICallable op, IApplyData arg) {
            var r = unpackTuple(arg.Value);
            var isControlled = op.IsControlled();
            var isAdjoint = op.IsAdjoint();
            QubitReg controls = new QubitReg("", "", new int[0]);
            if (isControlled) {
                var x = (object[])r;
                if (x.Length > 0) {
                    r = x[1];
                    controls = (x[0] as QubitReg?) ?? (new QubitReg("q", "", new[] {
                        ((Qubit)x[0]).Id
                    }));
                }
            }
            return new DoOp(op.Name, isAdjoint, controls, EnsureArrayWrapped(r));
        }

        static object[] EnsureArrayWrapped(object x) {
            return x.GetType().IsArray ? (object[]) x : new object[] { x }; ;
        }

        static string DescribeArgs(ICallable op, IApplyData arg, NamedAllocations alloc) {
            var p = Decompile(op, arg);
            var newArgs = p.Args.ToArray();

            var result = "";
            if (!p.Adjoint && (p.Name.StartsWith("Let") || p.Name.EndsWith("Init"))) {
                var qreg = (QubitReg) newArgs[0];
                var s = alloc.Alloc(qreg.offsets);
                result += $"{s} := {DriverUtil.DescribeIdRange(qreg.offsets)}\n";
            }
            for (var i = 0; i < newArgs.Length; i++) {
                var arr = newArgs[i] as object[];
                if (arr != null && arr.All(e => e is long)) {
                    newArgs[i] = "tab";
                    var tab = arr.Select(e => (long)e).ToArray();
                    if (!alloc.latestTable.SequenceEqual(tab)) {
                        alloc.latestTable = tab;
                        result += $"tab = [{string.Join(", ", tab)}]\n";
                    }
                    break;
                }
            }
            if (p.Controls.Length > 0) {
                //var y = string.Join(" and ", p.Controls);
                result += $"if {DescribeArray(p.Controls, alloc, false)} then ";
            }
            if (p.Adjoint) {
                result += "undo ";
            }
            result += $"{p.Name}({DescribeArray(newArgs, alloc, false)})";

            if (!p.Adjoint && (p.Name.StartsWith("Del"))) {
                var qreg = (QubitReg)newArgs[0];
                var s = alloc.Release(qreg.offsets);
                //result += $"\ndel {s}";
            }
            return result;
        }

        static void Main(string[] args) {
            var res = CountPrimitives(ShorFactor.Run, new Dictionary<string, string> {
                { "InitAnd", "CCZ" },
                { "CCZ", "CCZ" },
                { "CCZ^-1", "CCZ" },
                { "CCX", "CCZ" },
                { "CCX^-1", "CCZ" },
                { "R1Frac", "R" },

                { "InitAnd^-1", "C" },
                { "XorEqualConst", "C" },
                { "CNOT^-1", "C" },
                { "H", "C" },
                { "CNOT", "C" },
                { "CX", "C" },
                { "X", "C" },
                { "Measure", "C" },
                { "Reset", "C" },
            });
            foreach (var k in res.Keys) {
                Console.WriteLine($"{k}: {res[k]}");
            }
            var config = new QCTraceSimulatorConfiguration();
            config.usePrimitiveOperationsCounter = true;
            config.throwOnUnconstraintMeasurement = false;
            var qsim = new QCTraceSimulator(config);

            //var qsim = new Sim();
            //using (var qsim = new QuantumSimulator())
            {
                var terminalSet = new HashSet<string>(new[] {
                    "MeasureInteger",
                    "XorEqualConst",
                    "PlusEqual",
                    "MResetX",
                    "XorEqual",
                    "ResetAll",
                    "H",
                    "MResetZ",
                    "R1Frac",
                });
                var indent = 0;
                var terminalIndent = 0;
                var alloc = new NamedAllocations();
                qsim.OnOperationStart += (op, arg) => {
                    if (indent < 5 && terminalIndent == 0) {
                        foreach (var line in DescribeArgs(op, arg, alloc).Split('\n')) {
                            Console.WriteLine(new string(' ', indent * 4) + line);
                        }
                        Thread.Sleep(10);
                    }
                    indent += 1;
                    if (terminalSet.Contains(op.Name)) {
                        terminalIndent += 1;
                    }
                };
                qsim.OnOperationEnd += (op, arg) => {
                    indent -= 1;
                    if (terminalSet.Contains(op.Name)) {
                        terminalIndent -= 1;
                    }
                };
                var res2 = ShorFactor.Run(qsim);
                res2.Wait();
                //Console.WriteLine(String.Join(", ", qsim.MetricNames));
                var d = qsim.ToCSV();
                //foreach (var x in d.Keys) {
                //    Console.WriteLine(x);
                //    Console.WriteLine(d[x]);
                //}
                foreach (var k in qsim.MetricNames) {
                }
                double tCountAll = qsim.GetMetric<ShorFactor>(PrimitiveOperationsGroupsNames.T);
                Console.WriteLine($"{tCountAll}");
            }
            Thread.Sleep(1000000);
        }

        static Dictionary<string, int> CountPrimitives(
                Func<IOperationFactory, Task<QVoid>> runner,
                Dictionary<string, string> terminalSet) {
            var config = new QCTraceSimulatorConfiguration();
            config.throwOnUnconstraintMeasurement = false;
            var qsim = new QCTraceSimulator(config);

            var digging = true;
            var counts = new Dictionary<string, int>();
            var overdent = 0;
            var stack = new Stack<IApplyData>();
            qsim.OnOperationStart += (op, arg) => {
                stack.Push(arg);
                if (overdent == 0) {
                    digging = true;
                }
                if (overdent > 0 || terminalSet.ContainsKey(op.AppliedName(arg))) {
                    overdent += 1;
                }
            };
            qsim.OnOperationEnd += (op, arg) => {
                arg = stack.Pop();
                if (overdent == 0 && digging) {
                    counts[op.AppliedName(arg)] = -1000;
                    return;
                }
                if (overdent > 0) {
                    overdent -= 1;
                }
                if (overdent == 0) {
                    if (digging) {
                        var key = op.AppliedName(arg);
                        if (terminalSet.ContainsKey(key)) {
                            key = terminalSet[key];
                        }
                        if (!counts.ContainsKey(key)) {
                            counts[key] = 0;
                        }
                        counts[key] += 1;
                    }
                    digging = false;
                }
            };
            runner(qsim).Wait();
            return counts;
        }
    }
}