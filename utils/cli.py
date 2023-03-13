import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--daemon", default=False, help="exec in daemon mod", action="store_true"
)
args = parser.parse_args()
