import atexit
import argparse
import sys

from pyVim import connect

from pyVmomi import vim

from pyvmomi_tools import cli


def get_args():
    parser = argparse.ArgumentParser()

    cli.args.add_connection_arguments(parser)

    parser.add_argument('-n', '--name',
                        required=True,
                        action='store',
                        help='The virtual_machine name prefix to look for.')

    return cli.args.prompt_for_password(parser)


args = get_args()

# form a connection...
si = connect.SmartConnect(host=args.host, user=args.user, pwd=args.password,
                          port=args.port)

# doing this means you don't need to remember to disconnect your script/objects
atexit.register(connect.Disconnect, si)


# search the whole inventory tree recursively... a brutish but effective tactic
def match_name(obj, name):
    return obj.name.startswith(name)


root_folder = si.content.rootFolder

print "using wait_for_updates"
for vm in root_folder.find_by(match_name, args.name):
    print "Found VirtualMachine: %s Name: %s" % (vm, vm.name)

    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
        task = vm.PowerOff()
        task.wait(success=lambda t: sys.stdout.write("\rpower off\n"))
        task = vm.PowerOn()
        task.wait(success=lambda t: sys.stdout.write("\rpower on\n"))
    else:
        task = vm.PowerOn()
        task.wait(success=lambda t: sys.stdout.write("\rpower on\n"))
        task = vm.PowerOff()
        task.wait(success=lambda t: sys.stdout.write("\rpower off\n"))

print "using task extensions"
for vm in root_folder.find_by(match_name, args.name):
    print "Found VirtualMachine: %s Name: %s" % (vm, vm.name)

    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
        vm.PowerOff().poll(
            periodic=lambda t: sys.stdout.write('\roff\n'),
            success=lambda t: vm.PowerOn().poll(
                periodic=lambda t: sys.stdout.write("\ron\n")))
    else:
        vm.PowerOn().poll(
            periodic=lambda t: sys.stdout.write('\ron\n'),
            success=lambda t: vm.PowerOff().poll(
                periodic=lambda t: sys.stdout.write("\roff\n")))

