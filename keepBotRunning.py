import subprocess

filename = 'pebblebot.py'
while True:
    p = subprocess.Popen('python '+filename, shell=True).wait()