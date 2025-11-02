import subprocess, sys
if __name__ == "__main__":
    out = sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else 'truthfulqa.json'
    min_score = sys.argv[sys.argv.index('--min-score')+1] if '--min-score' in sys.argv else '0.6'
    cmd = ["python", "-m", "lm_eval", "--model", "hf", "--tasks", "truthfulqa", "--output_path", out, "--min_score", min_score]
    subprocess.run(cmd, check=True)
