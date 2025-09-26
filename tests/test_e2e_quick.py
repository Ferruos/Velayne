import subprocess
import sys

def test_selftest_ok():
    proc = subprocess.run([sys.executable, "-m", "velayne.run", "--selftest"], capture_output=True, encoding="utf-8")
    assert proc.returncode == 0, f"Non-zero exit: {proc.returncode}, out={proc.stdout}, err={proc.stderr}"
    assert "SELFTEST OK" in proc.stdout, f"No SELFTEST OK in output: {proc.stdout}"