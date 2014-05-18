
def run_test(args):
    args.sub_func(args)


def run_setup(args):
    pass


def test_parser(sub):
    parser = sub.add_parser("test", help="Run hyperkit system tests")
    parser.set_defaults(func=run_test)
    ts = parser.add_subparsers()
    setup_parser = ts.add_parser("setup", help="Set up the test environment")
    setup_parser.set_defaults(sub_func=run_setup)
