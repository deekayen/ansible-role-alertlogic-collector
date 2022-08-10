# Alert Logic remote collector

[![Molecule](https://github.com/deekayen/ansible-role-alertlogic-collector/actions/workflows/ci.yml/badge.svg)](https://github.com/deekayen/ansible-role-alertlogic-collector/actions/workflows/ci.yml) [![Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.](https://www.repostatus.org/badges/latest/inactive.svg)](https://www.repostatus.org/#inactive)

This playbook is used to install and configure the Alert Logic remote collector service.

## Requirements

The following platforms are supported.

Debian versions:

* buster
* bullseye

Ubuntu versions:

* 22.04
* 20.04

RHEL/CentOS versions:

* 7.x
* 8.x

## Role Variables

* `al_remote_registration_key` - your unique registration key, required except in supported cloud deployments (AWS, Azure) String defaults to `your_registration_key_here`

## Dependencies

* no known dependencies

## Example Playbook

    ---
    - name: Install Alert Logic remote collector to specific hosts
      hosts: al_collectors
      roles:
        - role: deekayen.alremote
          vars:
            al_remote_registration_key: 'useWhenNotInAWSorAzure'

## Configurations

The variable `al_remote_for_imaging` determine your installation type.  It is a boolean value and by default is `false`.  Setting this value to true will prepare your agent for imaging only and will not provision the agent.

Performing an agent install using the cookbook's default attributes, will setup the agent and provision the instance immediately. If you have properly set your registration key, your host should appear within Alert Logic's Console within 15 minutes. Note: in AWS and Azure deployments the use of the key is optional and in general not necessary.

## License and Authors

Distributed under the Apache 2.0 license.

Original Authors of Alert Logic agent role:
Muram Mohamed (mmohamed@alertlogic.com)
Justin Early (jearly@alertlogic.com)

Derivative work remote collector install by:
David Norman [deekayen](https://github.com/deekayen)
