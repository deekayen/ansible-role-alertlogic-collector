"""Testinfra checks for the Alert Logic syslog collector role."""

REMOTE_BIN = "/var/alertlogic/lib/remote/bin/al-remote"
KEY_ID = "0186cc36"


def test_collector_package_installed(host):
    assert host.package("al-log-syslog").is_installed


def test_collector_binary(host):
    assert host.file("/var/alertlogic").is_directory
    remote = host.file(REMOTE_BIN)
    assert remote.is_file
    assert remote.mode == 0o755


def test_signing_key_trusted(host):
    if host.exists("apt-get"):
        key = host.file("/etc/apt/trusted.gpg.d/al-agent-pkg-key.asc")
        assert key.is_file
        assert key.mode == 0o644
    else:
        keys = host.check_output("rpm -q gpg-pubkey --qf '%{VERSION}\\n'")
        assert KEY_ID in keys.lower().split()


def test_collector_service_enabled(host):
    assert host.service("al-log-syslog").is_enabled
