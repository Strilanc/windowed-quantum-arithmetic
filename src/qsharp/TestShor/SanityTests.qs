// namespace Quantum.TestShor
// {
//     open Microsoft.Quantum.Primitive;
//     open Microsoft.Quantum.Canon;
//     open Microsoft.Quantum.Extensions.Diagnostics;
//     open Microsoft.Quantum.Extensions.Math;
//     open FastShor;

//     operation ModulusTest() : Unit {
//         AssertIntEqual(-1, -1 % 3, "");
//         AssertIntEqual(2, ProperMod(-1, 3), "");
//     }

//     operation ExponentTest() : Unit {
//         AssertIntEqual(2^3, 8, "");
//         AssertAlmostEqual(Sqrt(4.0), 2.0);
//     }
// }
