/**
 * Class for encrypting VNC challenges.
 * Written from scratch following FIPS PUB 46 
 * http://www.itl.nist.gov/fipspubs/fip46-2.htm.
 * ©Vidar Holen, 2003
 * www.vidarholen.net
 * 
 * Ported to C#
 * ©Luis Rodríguez, 2010
 *
 * Released under the terms of the GNU General Public License.
 * 
 * Comments:
 * This file is not based on previous projects, unlike the vast
 * majority of DES implementation out there. None that I found
 * were both java and GPL, so here's to another step for the
 * community!
 *
 * This class, VNCEncrypt, has a deliberate implementation 
 * defect, brokengb(byte[],n), which is used to fetch a
 * bit out of the key schedule byte[] with the least significant 
 * bit first. 
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace WebLab.VM.WindowsVNC
{

    public class VNCEncrypt
    {
        private static int[] IP, IPR, ET, P, LS, PC1, PC2;
        private static int[][] S;
        byte[] key;
        byte[][] ks;
        static bool loaded;


        /** Sets all internal arrays to null. 
         * This will cause all subsequent actions to fail miserably until
         * load() is called, but it will free up some memory.
         * @see load()
         */
        public static void unload()
        {
            IP = IPR = ET = P = LS = PC1 = PC2 = null;
            S = null;
            loaded = false;
        }
        /** Loads all internal arrays.
         * If unload() has been called, load() is required to continue use.
         * @see unload()
         */
        public static void load()
        {
            if (loaded)
                return;

            loaded = true;

            generateIP();
            generateP();
            generateET();
            generateS();
            generateLS();
            generatePC();
        }

        public VNCEncrypt(byte[] key)
        {
            this.key = pad(key, 8);
            calculateKS();
        }

        public VNCEncrypt(String s)
            : this(data(s))
        {
        }

        /** Calculate key schedules */
        public void calculateKS()
        { //ok
            ks = new byte[16][];
            int c = 0, d = 0;
            long t;
            for (int i = 0; i < 28; i++)
            {
                c = sb(c, i, 28, brokengb(key, PC1[i]) == 1);
                d = sb(d, i, 28, brokengb(key, PC1[i + 28]) == 1);
            }
            for (int i = 0; i < 16; i++)
            {
                byte[] cd, cdp;
                t = 0;
                c = rol(c, 28, LS[i]); //ok
                d = rol(d, 28, LS[i]); //ok
                t = ((long)c << 28) | d;
                cd = ltoba(t, 7, 56);
                cdp = new byte[7];
                for (int j = 0; j < 48; j++)
                    sb(cdp, j, gb(cd, PC2[j]) == 1);
                ks[i] = cdp; //ok
            }
        }

        /** Encrypts the byte[]. 
         * @param b a byte array to be encrypted, must be of length 8. 
         */
        public byte[] encrypt(byte[] b)
        {
            if (!loaded)
                throw new Exception("Tables are not initialized. Call the load function before encrypting");

            byte[] L = new byte[4];
            byte[] R = new byte[4];
            byte[] EL, ER; //L' and R'
            b = permutate(b, true); //perform initial permutation
            //System.arraycopy(b,0,L,0,4);
            Array.Copy(b, 0, L, 0, 4);
            //System.arraycopy(b,4,R,0,4);
            Array.Copy(b, 4, R, 0, 4);
            for (int i = 0; i < 32; i++)
            {
                sb(L, i, gb(b, i) == 1);
                sb(R, i, gb(b, i + 32) == 1);
            }
            for (int i = 0; i < 16; i++)
            {
                EL = R;			// L' = R
                ER = add(L, f(R, ks[i])); 	// R' = L (+) f(R,Kn)
                L = EL;
                R = ER;
            }
            //append, with R first.
            byte[] r = cat(R, L);
            //perform permutation
            return permutate(r, false);
        }

        /** Rotate first i bits in v n steps to the left. */
        private static int rol(int v, int i, int n)
        {
            int of = (v >> (i - n)) & ((1 << n) - 1);
            v = (v << n) & ((1 << i) - 1);
            return v | of;
        }

        /** Perform initial permutation */
        private static byte[] permutate(byte[] b, bool f)
        {
            byte[] a = new byte[8];
            if (f) for (int i = 0; i < 64; i++)
                    sb(a, i, gb(b, IP[i]) == 1);
            else for (int i = 0; i < 64; i++)
                    sb(a, i, gb(b, IPR[i]) == 1);
            return a;
        }

        /** Perform P */
        private static byte[] PerformP(byte[] b)
        {
            byte[] r = new byte[4];
            for (int i = 0; i < 32; i++)
                sb(r, i, gb(b, P[i]) == 1);
            return r;
        }

        /** Perform E. */
        private static byte[] PerformE(byte[] b)
        {
            byte[] n = new byte[6];
            for (int i = 0; i < 48; i++)
                sb(n, i, gb(b, ET[i]) == 1);
            return n;
        }

        /** Perform S. */
        private static byte[] PerformS(byte[] n)
        {
            byte[] r = new byte[4];
            for (int i = 0; i < 8; i++)
            {
                int s = 0;
                for (int j = 0; j < 6; j++)
                {
                    s = (s << 1) | gb(n, i * 6 + j);
                }
                r[i / 2] |= (byte)(Sn(i, s) << ((i % 2) == 0 ? 4 : 0)); //I had 0:4. Damn me.
            }
            return r;
        }

        /** Performs lookup in an S table. */
        private static int Sn(int i, int n)
        {
            int a = (n >> 4) & 2 | (n & 1);
            int b = (n >> 1) & 0x0F;
            return S[i][a * 16 + b];
        }

        /** Performs f */
        private static byte[] f(byte[] R, byte[] K)
        {
            return PerformP(PerformS(add(PerformE(R), K)));
        }

        /** Gets bit number n from a byte[]. */
        private static int gb(byte[] b, int n)
        {
            return (b[n >> 3] >> (7 - (n & 0x07))) & 1;
        }
        /** Gets bit number n from a byte[], but doing it wrong (for VNC). */
        private static int brokengb(byte[] b, int n)
        {
            return (b[n >> 3] >> ((n & 0x07))) & 1;
        }

        /** Adjusts bit number n in a byte[]. */
        private static void sb(byte[] b, int n, bool on)
        {
            if (on) b[n >> 3] = (byte)(b[n >> 3] | (1 << (7 - (n & 0x07))));
            else b[n >> 3] = (byte)(b[n >> 3] & (~0 - (1 << (7 - (n & 0x07)))));
        }

        /** Gets bit number n from an int of i bits */
        private static int gb(int a, int n, int i)
        {
            return (a >> (i - n - 1)) & 1;
        }

        /** Gets bit number n from a long of i bits */
        private static int gb(long a, int n, int i)
        {
            return (int)((a >> (i - n - 1)) & 1);
        }

        /** Adjusts bit number n in an int of i bits */
        private static int sb(int a, int n, int i, bool on)
        {
            if (on) return a | (1 << (i - n - 1));
            else return a & (~0 - (1 << (i - n - 1)));
        }

        /** Convert b bits of a to a byte[] of length n */
        private static byte[] itoba(int a, int n, int b)
        {
            byte[] t = new byte[n];
            for (int i = 0; i < b; i++)
                sb(t, i, gb(a, i, b) == 1);
            return t;
        }

        /** Convert b bits of a to a byte[] of length n */
        private static byte[] ltoba(long a, int n, int b)
        {
            byte[] t = new byte[n];
            for (int i = 0; i < b; i++)
                sb(t, i, gb(a, i, b) == 1);
            return t;
        }

        /** Pad or truncate array into n elements. */
        private static byte[] pad(byte[] b, int n)
        {
            byte[] r = new byte[n];
            for (int i = 0; i < n; i++) r[i] = (byte)(b.Length < n ? 0 : b[i]);
            return r;
        }
        /** Returns a copy of the array. */
        private static byte[] copy(byte[] b)
        {
            byte[] a = new byte[b.Length];
            Array.Copy(b, 0, a, 0, b.Length);
            return a;
        }

        /** Generate Initial Permutation. 
         * This method generates the initial permutation table. It's called
         * by the class' static clause.
         */
        private static void generateIP()
        {
            IP = new int[64];
            IPR = new int[64];
            for (int i = 0; i < 64; i++)
                IP[i] = ((((i >> 3) << 1) + 1) % 9) + ((7 - (i & 0x07)) << 3);
            for (int i = 0; i < 64; i++)
                for (int j = 0; j < 64; j++)
                    if (IP[j] == i) IPR[i] = j;

        }

        /** Generate E Bit-Selection table. */
        private static void generateET()
        {
            ET = new int[48];
            int n = 31;
            for (int i = 0; i < 48; i++)
            {
                ET[i] = n;
                if (i % 6 == 5) n--; else n++;
                n &= 0x1F;
            }
        }

        /** Makes S. */
        private static void generateS()
        {
            S = new int[8][];
            S[0] = new int[] { 14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7, 0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8, 4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0, 15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13 };
            S[1] = new int[] { 15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10, 3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5, 0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15, 13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9 };
            S[2] = new int[] { 10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8, 13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1, 13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7, 1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12 };
            S[3] = new int[] { 7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15, 13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9, 10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4, 3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14 };
            S[4] = new int[] { 2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9, 14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6, 4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14, 11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3 };
            S[5] = new int[] { 12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11, 10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8, 9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6, 4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13 };
            S[6] = new int[] { 4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1, 13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6, 1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2, 6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12 };
            S[7] = new int[] { 13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7, 1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2, 7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8, 2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11 };
        }
        /** Makes P */
        private static void generateP()
        {
            P = new int[] { 15, 6, 19, 20, 28, 11, 27, 16, 0, 14, 22, 25, 4, 17, 30, 9, 1, 7, 23, 13, 31, 26, 2, 8, 18, 12, 29, 5, 21, 10, 3, 24 };
        }

        /** Makes PC-1 and -2.
         * Permuted choices. */
        private static void generatePC()
        {
            PC1 = new int[] { 56, 48, 40, 32, 24, 16, 8, 0, 57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18, 10, 2, 59, 51, 43, 35, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 60, 52, 44, 36, 28, 20, 12, 4, 27, 19, 11, 3 };
            PC2 = new int[] { 13, 16, 10, 23, 0, 4, 2, 27, 14, 5, 20, 9, 22, 18, 11, 3, 25, 7, 15, 6, 26, 19, 12, 1, 40, 51, 30, 36, 46, 54, 29, 39, 50, 44, 32, 47, 43, 48, 38, 55, 33, 52, 45, 41, 49, 35, 28, 31 };
        }

        /** Generates left shift table */
        private static void generateLS()
        {
            LS = new int[] { 1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1 };
        }

        /** "Bitwise addition modulo 2", xor two byte arrays.
         * They're assumed to be the same length 
         */
        private static byte[] add(byte[] a, byte[] b)
        {
            byte[] c = new byte[a.Length];
            for (int i = 0; i < a.Length; i++) c[i] = (byte)(a[i] ^ b[i]);
            return c;
        }

        /** Append two byte[]s */
        private static byte[] cat(byte[] a, byte[] b)
        {
            byte[] c = new byte[a.Length + b.Length];
            Array.Copy(a, 0, c, 0, a.Length);
            Array.Copy(b, 0, c, a.Length, b.Length);
            return c;
        }

        /** Parse a hex string into a byte[] */
        public static byte[] hex(String s)
        {
            byte[] b = new byte[s.Length / 2];
            for (int i = 0; i < s.Length; i += 2)
            {

                // Note: In Java, it was Substring(i, i+2)
                b[i / 2] = (byte)int.Parse("0x" + s.Substring(i, 2), System.Globalization.NumberStyles.AllowHexSpecifier);
            }
            return b;
        }

        //Methods for getting debugging bit strings
        //byte[], space every l bits, n number of bits
        public static String bits(byte[] b) { return bits(b, 8); }
        public static String bits(byte[] b, int l)
        {
            int n = b.Length * 8;
            return bits(b, l, n);
        }

        public static String bits(byte[] b, int l, int n)
        {
            string s = "";
            for (int i = 0; i < n; i++)
            {
                if (i % l == 0) s += " ";
                s += gb(b, i);
            }
            return s;
        }

        public static String bits(int c, int b, int l, int n)
        {
            String s = "";
            for (int i = 0; i < n; i++)
            {
                if (i % l == 0) s += " ";
                s += gb(c, i, b);
            }
            return s;
        }

        public static byte[] data(String s)
        {
            byte[] b = new byte[s.Length];
            for (int i = 0; i < b.Length; i++)
                b[i] = (byte)s[i];
            return b;
        }

    }



}
