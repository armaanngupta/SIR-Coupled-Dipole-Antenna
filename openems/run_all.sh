export LD_LIBRARY_PATH=/opt/openEMS/lib
python3 sir_dipole.py e --fields > log_e.txt 2>&1
for c in a b c d bent; do python3 sir_dipole.py $c > log_$c.txt 2>&1; done
for s in C=0.2 C=0.8 er=4.0 er=4.6 h=1.2 h=2.0; do python3 sir_dipole.py e --sweep $s > log_$s.txt 2>&1; done
echo ALLDONE > alldone.txt
