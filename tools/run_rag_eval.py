import subprocess, sys
if __name__ == "__main__":
    out = sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else 'rag_eval.json'
    fmin = sys.argv[sys.argv.index('--min-faithful')+1] if '--min-faithful' in sys.argv else '0.8'
    emin = sys.argv[sys.argv.index('--min-exact')+1] if '--min-exact' in sys.argv else '0.7'
    use_langsmith = "--use-langsmith" in sys.argv
    cmd = ["python", "-m", "rag_eval", "--output_path", out, "--min_faithful", fmin, "--min_exact", emin]
    if use_langsmith:
        cmd.append("--use-langsmith")
    subprocess.run(cmd, check=True)
