// namespace Quantum.TestShor
// {
//     open Microsoft.Quantum.Primitive;
//     open Microsoft.Quantum.Canon;
//     open Microsoft.Quantum.Extensions.Diagnostics;
//     open FastShor;

//     operation InitAnd_vs_CCNot_Test () : Unit {
//         using (qs = Qubit[4]) {
//             InitDual(qs);
//             using (t = Qubit()) {
//                 InitAnd(qs[0], qs[1], t);
//                 CCNOT(qs[0], qs[1], t);
//             }
//             UncomputeDual(qs);
//         }
//     }

//     operation UncomputeAnd_vs_CCNot_Test () : Unit {
//         for (_ in 0..9) {
//             using (qs = Qubit[4]) {
//                 InitDual(qs);
//                 using (t = Qubit()) {
//                     CCNOT(qs[0], qs[1], t);
//                     UncomputeAnd(qs[0], qs[1], t);
//                 }
//                 UncomputeDual(qs);
//             }
//         }
//     }

//     operation PhaseNegate_vs_Z_Test () : Unit {
//         for (n in 0..4) {
//             using (qs = Qubit[n*2]) {
//                 InitDual(qs);
//                 Controlled PhaseNegate(qs[0..n-1], ());
//                 if (n > 0) {
//                     Controlled Z(qs[0..n-2], qs[n-1]);
//                 }
//                 UncomputeDual(qs);
//             }
//         }
//     }

//     operation Toggle_vs_X_Test () : Unit {
//         for (n in 1..5) {
//             using (qs = Qubit[n*2]) {
//                 InitDual(qs);
//                 Controlled Toggle(qs[0..n-2], qs[n-1]);
//                 Controlled X(qs[0..n-2], qs[n-1]);
//                 UncomputeDual(qs);
//             }
//         }
//     }

//     operation UncomputeToggle_vs_X_Test () : Unit {
//         for (_ in 0..9) {
//             for (n in 0..4) {
//                 using (qs = Qubit[n*2]) {
//                     InitDual(qs);
//                     using (t = Qubit()) {
//                         Controlled X(qs, t);
//                         Controlled UncomputeToggle(qs, t);
//                         UncomputeDual(qs);
//                     }
//                 }
//             }
//         }
//     }
// }
