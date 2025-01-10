from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '--context_paths', "-c",
        type=str,
        nargs='+',
        help='Path(s) to use as context for the code assistant.'
    )
    parser.add_argument(
        'working_dir',
        default='.',
        type=str,
        help='Working directory for the code assistant.'
    )
    return parser.parse_args()
