import subprocess, sys
if __name__ == "__main__":
    out = sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else 'swebench.json'
    variant = sys.argv[sys.argv.index('--variant')+1] if '--variant' in sys.argv else 'verified'
    min_solve = sys.argv[sys.argv.index('--min-solve')+1] if '--min-solve' in sys.argv else '0.35'
    cmd = ["python", "-m", "swebench", "--variant", variant, "--min_solve", min_solve, "--output_path", out]
    subprocess.run(cmd, check=True)
