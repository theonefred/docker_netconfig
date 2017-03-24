import shlex, subprocess

def run(command_line):
    args = shlex.split(command_line)
    print args
    try:
        res = subprocess.check_output(args, shell=True, stderr=subprocess.STDOUT)
        return res
    except subprocess.CalledProcessError as e:
        print e.output
        return e.output
