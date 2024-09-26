import subprocess
import venv
import shutil

def create_venv(venv_path: str) -> None:
    venv.create(venv_path, with_pip=True)

def install_package(venv_path: str, package: str) -> int:
    subprocess.run([f"{venv_path}/bin/pip", "install", package], check=True)

def import_package(venv_path: str, package: str) -> str:
    subprocess.run([f"{venv_path}/bin/python", "-X", "importtime", "-c", f"{package}"], check=True)

"""
v0.5.0
import time: self [us] | cumulative | imported package
import time:       297 |     408355 | snowflake.telemetry._internal.exporter.otlp.proto.logs
"""

"""
v0.6.0.dev
import time: self [us] | cumulative | imported package
import time:       320 |     219479 | snowflake.telemetry._internal.exporter.otlp.proto.logs
"""
def main():
    venv_path = ".benchmark-import-venv"
    create_venv(venv_path)
    install_package(venv_path, "./")
    print("Import time:")
    import_package(venv_path, "import snowflake.telemetry._internal.exporter.otlp.proto.logs")
    shutil.rmtree(venv_path)

if __name__ == "__main__":
    main()
