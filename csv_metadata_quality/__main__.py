# SPDX-License-Identifier: GPL-3.0-only

from sys import argv

from csv_metadata_quality import app


def main():
    app.run(argv)


if __name__ == "__main__":
    main()
