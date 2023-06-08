import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--daemon",
    default=False,
    help="exec in daemon mod",
    action="store_true",
)
parser.add_argument(
    "-n",
    "--now",
    default=False,
    help="download now all weekly bases",
    action="store_true",
)
parser.add_argument(
    "-t",
    "--today",
    default=False,
    help="download now all today(daily) bases",
    action="store_true",
)
args = parser.parse_args()
