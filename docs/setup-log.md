# Setup Log

This file documents the setup process for my Raspberry Pi home-server lab.

The goal is to keep a clear, public-safe build record that shows technical progress, troubleshooting, and decision-making without exposing passwords, private keys, network secrets, patient data, or employer-confidential information.

## Project Context

This home server is part of a broader technical portfolio focused on:

* Linux administration
* SSH workflows
* Docker and containerized services
* Raspberry Pi infrastructure
* Secure self-hosted tools
* Data projects
* Future clinical AI and lab-informatics workflows

## Hardware

* Raspberry Pi 5
* microSD or SSD storage
* Chromebook used as the primary admin/setup machine
* Home network connection

More exact hardware details will be added as the build evolves.

## Operating System

Planned or in-progress server operating system:

* Ubuntu Server or Raspberry Pi OS

Final OS details will be documented once confirmed.

## Network Setup

Initial network goals:

* Connect the Raspberry Pi to the local network
* Confirm local IP address assignment
* Enable SSH access
* Configure a stable hostname for easier access
* Avoid relying permanently on a changing DHCP address

Public-safe note: local IP addresses, Wi-Fi details, router information, and network-specific identifiers should be generalized or omitted in this public repository.

## SSH Setup

Initial SSH goals:

* Connect from Chromebook to the Raspberry Pi
* Use a stable hostname when possible
* Document repeatable SSH commands
* Eventually configure SSH keys for safer authentication

Example sanitized SSH command:

```bash
ssh ubuntu@pi-server.local
```

## Current Status

* Repository created
* Professional GitHub profile configured
* Home server documentation started
* Setup log created

## Next Setup Tasks

* Confirm operating system version
* Confirm hostname
* Confirm SSH access method
* Document package updates
* Install Git if needed
* Install Docker
* Create a backup plan
* Create a security checklist
* Add architecture diagram

## Troubleshooting Notes

Use this section to document problems and fixes.

### Issue: Local IP address may change

Potential solution:

* Use hostname-based access such as `pi-server.local`
* Use router DHCP reservation if available
* If on a managed apartment network, document limitations and use a practical workaround

### Issue: Chromebook SSH setup

Potential solution:

* Save a reusable SSH connection
* Prefer hostname-based SSH when reliable
* Document the final working command

## Security Rules

Do not commit:

* Passwords
* SSH private keys
* API keys
* Tokens
* Personal network details
* Public IP addresses
* Patient data
* Employer-confidential information
* Screenshots from clinical systems
* Real LIS, Epic, or lab accession data

## Build Notes

Add dated notes below as the project progresses.

### 2026-06-24

* Created GitHub account branding for professional career shift
* Created `home-server-lab` repository
* Added initial README
* Started structured documentation
