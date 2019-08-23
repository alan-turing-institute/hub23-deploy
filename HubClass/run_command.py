import subprocess

def run_cmd(cmd):
    """Run a subprocess command

    Parameters
    ----------
    cmd: List of strings.

    Returns
    -------
    result: Dictionary
    """
    result = {}

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output = proc.communicate()

    result["returncode"] = proc.returncode
    result["output"] = output[0].decode(encoding="utf-8")
    result["err_msg"] = output[1].decode(encoding="utf-8")

    return result

def run_pipe_cmd(cmds):
    """Pipe together multiple commands

    Parameters
    ----------
    cmds: Nested list of strings

    Returns
    -------
    result: Dictionary
    """
    N = len(cmds)  # Number of commands to pipe together
    procs = []     # List to track processes in
    result = {}    # Dictionary to store outputs in

    for i in range(N):
        if i == 0:
            proc = subprocess.Popen(
                cmds[i],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            procs.append(proc)
        else:
            proc = subprocess.Popen(
                cmds[i],
                stdin=procs[i-1].stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            procs[i-1].stdout.close()
            procs.append(proc)

    output = procs[-1].communicate()

    result["returncode"] = procs[-1].returncode
    result["output"] = output[0].decode(encoding="utf-8")
    result["err_msg"] = output[1].decode(encoding="utf-8")

    return result
