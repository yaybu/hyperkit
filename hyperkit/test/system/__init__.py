
import os
import json
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


def run_run(args):
    m = manager.SystemTestManager(args.directory)
    r = m.exec_test(args.hypervisor, args.distro, args.release, args.architecture)
    if args.json:
        print json.dumps(r)
    else:
        for stage, results in r.items():
            if stage == 'analysis':
                print "Analysis"
                print "--------"
                print
                print results
            else:
                print stage
                print "=" * len(stage)
                print
                print "Return value", results['code']
                if results['stdout']:
                    print
                    print "Standard output"
                    print "---------------"
                    print
                    print results['stdout']
                if results['stderr']:
                    print
                    print "Standard error"
                    print "--------------"
                    print
                    print results['stderr']


def run_start(args):
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
    config_parser.add_argument("-H", "--hypervisor", default=(), choices=("vmware", "vbox"), nargs="*", help="hypervisor to test (by default all present are tested)")
    config_parser.set_defaults(sub_func=run_config)

    start_parser = ts.add_parser("start", help="start running outstanding tests")
    start_parser.add_argument("directory", help="directory containing test state")
    start_parser.set_defaults(sub_func=run_start)

    run_parser = ts.add_parser("run", help="run a single test")
    run_parser.add_argument("--json", action="store_true", help="produce output in json format")
    run_parser.add_argument("directory", help="directory containing test state")
    run_parser.add_argument("hypervisor")
    run_parser.add_argument("distro")
    run_parser.add_argument("release")
    run_parser.add_argument("architecture")
    run_parser.set_defaults(sub_func=run_run)

    report_parser = ts.add_parser("report", help="report on the tests")
    report_parser.add_argument("directory", help="directory containing test state")
    report_parser.set_defaults(sub_func=run_report)
