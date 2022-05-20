import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_alremote_bin(host):
    assert host.file("/var/alertlogic").is_directory
    assert host.file("/var/alertlogic/lib/remote/bin/al-remote").is_file
    assert host.file("/var/alertlogic/lib/remote/bin/al-remote").mode == 0o755
