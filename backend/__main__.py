import sys

import uvicorn

from backend.utils import create_default_files

from . import create_api

SERVER_PORT = 5000
SERVER = "0.0.0.0"  # nosec: B104
LOG_LEVEL = "debug"


def main() -> None:
    create_default_files()
    uvicorn.run(create_api(), host=SERVER, port=SERVER_PORT, timeout_keep_alive=120)


if __name__ == "__main__":
    sys.exit(main())
