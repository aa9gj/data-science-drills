"""Rebuild everything: question banks (from the source files in this folder) and the site one level up.

    cd tools && python3 build.py

Steps that need the internet (downloading upstream question sources) are not repeated here:
pg_questions.json and club.sql are already-converted copies of the PostgreSQL Exercises
questions and database (see CREDITS.md). Each bank script verifies its own answers where it can.
"""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
for script in ['sql_bank.py', 'gen_shop.py', 'bank_sql_de.py', 'bank_py.py', 'bank_py_ml.py', 'bank_rsas.py', 'bank_rsas2.py']:
    print('==>', script)
    subprocess.run([sys.executable, '-I', script], cwd=here, check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, '-I', 'assemble2.py'], cwd=here, check=True, env={**os.environ, 'OUT': os.path.join(here, '..')})
