# deekayen.alremote

[![CI](https://github.com/deekayen/ansible-role-alertlogic-collector/actions/workflows/ci.yml/badge.svg)](https://github.com/deekayen/ansible-role-alertlogic-collector/actions/workflows/ci.yml) [![Ansible Galaxy](https://img.shields.io/badge/galaxy-deekayen.alremote-blue.svg)](https://galaxy.ansible.com/ui/standalone/roles/deekayen/alremote/) [![Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.](https://www.repostatus.org/badges/latest/inactive.svg)](https://www.repostatus.org/#inactive) ![Apache 2.0 license](https://img.shields.io/badge/license-Apache--2.0-blue)

An Ansible role that installs the Alert Logic remote syslog collector (`al-log-syslog`) on Linux, provisions it with a registration key, and points the local syslog daemon at it.

The role installs the vendor's `LATEST` package from `scc.alertlogic.net/software/` (`al-log-syslog_LATEST_<arch>.deb` on Debian and Ubuntu, `al-log-syslog-LATEST-1.<arch>.rpm` on the RedHat family) after trusting the Alert Logic signing key. It runs `/etc/init.d/al-log-syslog provision --key <key>`, writes an rsyslog or syslog-ng drop-in that sends all messages to `127.0.0.1:1515`, labels TCP 1515 as `syslogd_port_t` when SELinux is enabled, and starts and enables the `al-log-syslog` service.

The Galaxy name is `deekayen.alremote`, not `deekayen.alertlogic_collector`.

## Requirements

- ansible-core 2.15 or newer on the controller.
- The `community.general` collection for the SELinux port task.
- Outbound HTTPS from the target to `scc.alertlogic.net`.
- Privilege escalation on the target. Run the play with `become: true`; the role installs packages and writes under `/etc`.
- Fact gathering left on. The role branches on `ansible_facts.os_family`, `ansible_facts.architecture`, and `ansible_facts.selinux`.

## Supported platforms

From `meta/main.yml`, and each one runs through Molecule in CI:

| Platform | Versions |
| --- | --- |
| EL (Rocky Linux in CI) | 9, 10 |
| Amazon Linux | 2023 |
| Debian | 12 (bookworm), 13 (trixie) |
| Ubuntu | 22.04 (jammy), 24.04 (noble), 26.04 (resolute) |

## Installation

From Ansible Galaxy:

```bash
ansible-galaxy role install deekayen.alremote
ansible-galaxy collection install community.general
```

Or pin it in `requirements.yml`:

```yaml
---
roles:
  - name: deekayen.alremote
    src: https://github.com/deekayen/ansible-role-alertlogic-collector.git
    scm: git
    version: main

collections:
  - name: community.general
```

```bash
ansible-galaxy install -r requirements.yml
```

## Role variables

| Variable | Default | Description |
| --- | --- | --- |
| `disable_gpg_check` | `false` | Passed to `dnf` as `disable_gpg_check` when installing the RPM on RedHat-family hosts. It has no effect on Debian or Ubuntu. |
| `al_remote_registration_key` | `your_registration_key_here` | Alert Logic registration key, passed to `al-log-syslog provision --key`. The default is a placeholder; set a real key. `tasks/assert.yml` fails the play on an empty string and prints a warning while the placeholder is in place. `meta/argument_specs.yml` describes the key as required except in AWS and Azure deployments. Keep it in Ansible Vault or a secrets lookup; no task sets `no_log`, so it appears in verbose output. |
| `al_remote_for_imaging` | `false` | Skip starting and enabling the `al-log-syslog` service, for hosts that will be captured as a machine image. Provisioning still runs. |

`vars/Debian.yml` and `vars/RedHat.yml` hold the package URLs, architecture mapping, and signing key fingerprint for each OS family; they are internal values.

## Behavior

- Provisioning runs only when `/var/alertlogic/lib/remote/etc/host_uuid` is absent. It always passes `--key`, including the placeholder value when `al_remote_registration_key` is left at its default.
- The packages are the vendor's `LATEST` builds. `apt` and `dnf` install them when the package is absent and do not pin a version.
- On Debian and Ubuntu, the signing key goes to `/etc/apt/trusted.gpg.d/al-agent-pkg-key.asc`. On the RedHat family, `rpm_key` imports it and checks fingerprint `9a2a3e9a817127b121b2b2fb00802f0e0186cc36`.
- The rsyslog drop-in is `/etc/rsyslog.d/al-remote.conf`. For syslog-ng, the role writes `/etc/syslog-ng/conf.d/al-remote.conf` and adds an `include` line to `/etc/syslog-ng/syslog-ng.conf`. The role detects syslog-ng by the presence of `/etc/init.d/syslog-ng`.
- Provisioning notifies a restart of `al-log-syslog`; logger changes restart rsyslog or reload syslog-ng.

## Dependencies

None.

## Example playbook

```yaml
---
- name: Install the Alert Logic remote syslog collector.
  hosts: syslog_collectors
  become: true

  vars:
    al_remote_registration_key: "{{ vault_al_remote_registration_key }}"

  roles:
    - deekayen.alremote
```

`vault_al_remote_registration_key` is a placeholder for a vaulted variable.

## Tags

| Tag | Tasks |
| --- | --- |
| `always` | Input validation and the OS family `include_vars`. |
| `install_collector` | The include of the package install tasks. |
| `install_al_collector` | Package installs and the service start. |
| `configure_al_collector` | The provisioning state check. |
| `provision_al_collector` | Provisioning state check, `al-log-syslog provision`, and the logger configuration include. |
| `rsyslog`, `syslog_ng`, `configure_al_collector_syslog` | Logger detection and drop-in files. |
| `selinux` | The SELinux port rule. |

`--skip-tags` works on any of these, and Molecule uses `--skip-tags provision_al_collector,configure_al_collector`. `--tags` does not select inner tags alone, because the task files are pulled in by an `include_tasks` that carries different tags. For example, `--tags install_al_collector` starts the service without installing the package, and `--tags install_collector` includes the install file but runs none of its tasks. `--tags provision_al_collector` runs provisioning but none of the logger configuration tasks it includes. `--tags selinux` works as expected.

## Known issues

- `al_remote_initscript` and `al_remote_syslog_ng_source` are set in `vars/Debian.yml` and `vars/RedHat.yml`, but no task or template reads them. `templates/etc/syslog-ng/al-remote.conf` hardcodes `source(s_src)`.

## Development

CI runs on every push to `main` and every pull request (see `.github/workflows/ci.yml`):

1. Lint: installs `community.general` from `molecule/default/requirements.yml`, then runs `ansible-lint --profile production` and `flake8 molecule/`.
2. Molecule: converge, idempotence, and testinfra verification in Docker against each distribution in the table above. `molecule.yml` sets `ANSIBLE_SKIP_TAGS=provision_al_collector,configure_al_collector`, since provisioning needs a real registration key, so CI does not exercise provisioning or the syslog drop-ins.

To run the same checks locally with Docker available:

```bash
pip3 install ansible-core ansible-lint flake8 molecule "molecule-plugins[docker]" docker pytest-testinfra
ansible-galaxy install -r molecule/default/requirements.yml
ansible-lint --profile production
flake8 molecule/
MOLECULE_DISTRO=rockylinux9 molecule test
```

`MOLECULE_DISTRO` selects a `geerlingguy/docker-<distro>-ansible` image. The values CI uses are `rockylinux9`, `rockylinux10`, `amazonlinux2023`, `ubuntu2204`, `ubuntu2404`, `ubuntu2604`, `debian12`, and `debian13`. The testinfra checks in `molecule/default/tests/test_default.py` confirm that the `al-log-syslog` package is installed, `/var/alertlogic/lib/remote/bin/al-remote` exists with mode `0755`, the signing key is trusted (the apt keyring file, or key ID `0186cc36` in the RPM database), and the `al-log-syslog` service is enabled.

### Repository layout

| Path | Purpose |
| --- | --- |
| `tasks/main.yml` | Validation, variable include, install, provision, logger, SELinux, and service steps. |
| `tasks/assert.yml` | Registration key check and placeholder warning, tagged `always`. |
| `tasks/install_collector.yml` | Signing key import and package install per OS family. |
| `tasks/provision_collector.yml` | `al-log-syslog provision`. |
| `tasks/configure_loggers.yml`, `tasks/_rsyslog.yml`, `tasks/_syslog_ng.yml` | Syslog forwarding to port 1515. |
| `tasks/selinux.yml` | SELinux port rule for TCP 1515. |
| `templates/etc/` | rsyslog and syslog-ng drop-ins. |
| `vars/` | Per-OS-family package URLs and key fingerprint. |
| `defaults/main.yml` | Every user-facing variable. |
| `molecule/default/` | Molecule scenario: `prepare.yml`, `converge.yml`, requirements, and testinfra tests. |
| `.github/workflows/` | `ci.yml` for lint and Molecule, `release.yml` for Galaxy import. |

## Releases

Pushing a git tag runs `.github/workflows/release.yml`, which imports the tagged commit into Ansible Galaxy as `deekayen.alremote`. The import needs a `GALAXY_API_KEY` repository or organization secret.

## License

Apache 2.0. See [LICENSE](LICENSE).

## Author

[David Norman](https://github.com/deekayen), adapted from the Alert Logic agent role in [alertlogic/al-agents-ansible-playbooks](https://github.com/alertlogic/al-agents-ansible-playbooks) by Muram Mohamed and Justin Early. Sponsorship links are in [.github/FUNDING.yml](.github/FUNDING.yml).
