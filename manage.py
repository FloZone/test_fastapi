import subprocess
import sys


def lint_command():
    print("Linting")
    print("flake8 pass...")
    return subprocess.run(["flake8", "./src/"]).returncode == 0


def format_command():
    print("Formatting")
    print("isort pass...")
    if subprocess.run(["isort", "--atomic", "./src/"]).returncode != 0:
        return False
    print("black pass...")
    return (
        subprocess.run(
            [
                "black",
                "--target-version",
                "py38",
                "-l",
                "120",
                "./src/",
            ],
        ).returncode
        == 0
    )


if __name__ == "__main__":
    if sys.argv[1] == "lint":
        sys.exit(0 if lint_command() else 1)
    elif sys.argv[1] == "format":
        sys.exit(0 if format_command() else 1)
    sys.exit(0)
