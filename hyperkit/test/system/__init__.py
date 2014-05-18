
import os
from . import manager


def run_test(args):
    args.sub_func(args)


def run_setup(args):
    manager.SystemTestManager.create(args.directory)


def run_config(args):
    release = [tuple(x.split("/", 2)) for x in args.release]
    m = manager.SystemTestManager(args.directory)
    m.set_hypervisors(args.hypervisor)
    m.set_releases(release)


def run_execute(args):
    pass


def run_report(args):
    pass


def test_parser(sub):
    parser = sub.add_parser("test", help="Run hyperkit system tests")
    parser.set_defaults(func=run_test)
    ts = parser.add_subparsers()
    setup_parser = ts.add_parser("setup", help="Set up the test environment")
    setup_parser.add_argument("directory", help="directory in which to create test state")
    setup_parser.set_defaults(sub_func=run_setup)

    config_parser = ts.add_parser("config", help="Configure test parameters")
    config_parser.add_argument("directory", help="directory containing test state")
    config_parser.add_argument("release", nargs="*", help="distro/release/architecture")
    config_parser.add_argument("-o", "--output", default=os.path.realpath("test_reports"), help="write test reports and database to this directory")
    config_parser.add_argument("-H", "--hypervisor", choices=("vmware", "vbox"), nargs="*", help="hypervisor to test (by default all present are tested)")
    config_parser.set_defaults(sub_func=run_config)

    execute_parser = ts.add_parser("run", help="run the tests")
    execute_parser.add_argument("directory", help="directory containing test state")
    execute_parser.set_defaults(sub_func=run_execute)

    report_parser = ts.add_parser("report", help="report on the tests")
    report_parser.add_argument("directory", help="directory containing test state")
    report_parser.set_defaults(sub_func=run_report)
