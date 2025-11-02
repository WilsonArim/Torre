import subprocess, sys
if __name__ == "__main__":
    out = sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else 'harness.json'
    delta = sys.argv[sys.argv.index('--max-delta-sigma')+1] if '--max-delta-sigma' in sys.argv else None
    cmd = ["lm-eval", "--model", "hf", "--tasks", "MMLU,GSM8K,HellaSwag,BBH", "--output_path", out]
    if delta: cmd += ["--max_delta_sigma", delta]
    subprocess.run(cmd, check=True)
