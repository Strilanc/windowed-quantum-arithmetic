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
    public static class DriverUtil {
        /// <summary>
        /// Determines if the given operation is a controlled variant.
        /// </summary>
        public static bool IsControlled(this ICallable op) {
            return op.Variant == OperationFunctor.Controlled
                || op.Variant == OperationFunctor.ControlledAdjoint;
        }

        /// <summary>
        /// Determines if the given operation is an adjoint variant.
        /// </summary>
        public static bool IsAdjoint(this ICallable op) {
            return op.Variant == OperationFunctor.Adjoint
                || op.Variant == OperationFunctor.ControlledAdjoint;
        }

        /// <summary>
        /// Returns the controls controlling an operation.
        /// 
        /// Uncontrolled operations have an empty controls list.
        /// </summary>
        static Qubit[] Controls(ICallable op, IApplyData arg) {
            // Uncontrolled operations have no controls.
            if (!op.IsControlled()) {
                return new Qubit[0];
            }

            // Get first element of (controls, args) tuple.
            dynamic v = arg.Value;
            QArray<Qubit> ctrls = v.Item1;
            return ctrls.ToArray();
        }

        /// <summary>
        /// Describes an operation as [CCC...]Name[^-1] based controls and adjointness.
        /// </summary>
        public static string AppliedName(this ICallable op, IApplyData arg) {
            var result = new string('C', Controls(op, arg).Length);
            result += op.Name;
            if (op.IsAdjoint()) {
                result += "^-1";
            }
            return result;
        }

        /// <summary>
        /// Describes a list of integers using python range notation (if possible).
        /// </summary>
        public static string DescribeIdRange(int[] ids) {
            if (ids.Length == 0) {
                return "[]";
            }
            if (ids.Length == 1) {
                return $"[{ids[0]}]";
            }

            var result = new List<string>();
            var step = 0;
            var end = ids[0];
            var start = ids[0];
            Action dump = () => {
                if (step == 0 || end == start + step) {
                    result.Add($"[{start}]");
                } else if (step == 1) {
                    result.Add($"[{start}:{end}]");
                } else if (step == -1) {
                    result.Add($"[{start}:{end}:-1]");
                }
            };

            foreach (var x in ids.Skip(1)) {
                if (step == 0) {
                    if (x > start) {
                        step = 1;
                    } else if (x < start) {
                        step = -1;
                    }
                    end = start + step;
                }
                if (end != x) {
                    dump();
                    start = x;
                    step = 0;
                    end = x;
                } else {
                    end += step;
                }
            }
            dump();
            return string.Join('+', result);
        }
    }
}