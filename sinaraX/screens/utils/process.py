import platform
from subprocess import PIPE, STDOUT, Popen


def start_cmd(cmd: str):
    _encoding = "utf-8"
    if "Windows" in platform.system():
        _encoding = "cp1251"
    with Popen(
        cmd,
        shell=True,
        stdout=PIPE,
        stderr=STDOUT,
        cwd=None,
    ) as child_process:

        stdout_bufer = b""
        while True:
            stdout_byte = child_process.stdout.read(1)
            stdout_bufer += stdout_byte

            if (stdout_byte == b"\r") or (stdout_byte == b"\n"):
                yield stdout_bufer.decode(encoding=_encoding)
                stdout_bufer = b""

            if stdout_byte == b"":
                break

        child_process.communicate()

        if child_process.returncode != 0:
            yield f"{cmd} failed!\n"


def decode_lines(cmd):
    lines = [" "]
    for decoded_line in start_cmd(cmd):
        if len(decoded_line) > 0:
            if lines[-1][-1] == "\r":
                lines[-1] = decoded_line
            else:
                lines.append(decoded_line)
        yield lines


if __name__ == "__main__":
    for line in start_cmd(
        "python3 -c 'import tqdm; import time; "
        "print(1); [(time.sleep(0.05)) "
        "for x in tqdm.tqdm(range(100))]; print(2);'"
    ):
        print(line)

    for line in start_cmd("ping ya.ru -c 3"):
        print(line)

    for lines in decode_lines(
        "python3 -c 'import tqdm; import time; print(1); "
        "[(time.sleep(0.05)) "
        "for x in tqdm.tqdm(range(100))]; print(2);'"
    ):
        print(f"{lines=}")
