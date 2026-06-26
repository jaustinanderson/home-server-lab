# Network Notes

This file documents network setup decisions for the Raspberry Pi home-server lab.

The goal is to maintain a clear, public-safe record of how the server is reached on the local network without exposing private network details, router information, passwords, public IP addresses, or other sensitive configuration.

## Network Goals

The home server should be reachable in a stable, repeatable way from the primary admin machine.

Primary goals:

* Connect the Raspberry Pi to the local network
* Confirm that the server receives a local network address
* Access the server over SSH
* Prefer hostname-based access when possible
* Avoid relying permanently on a changing DHCP address
* Document public-safe troubleshooting steps

## Preferred Access Method

The preferred access method is hostname-based SSH:

```bash
ssh ubuntu@pi-server.local
```

This is easier to remember than a local IP address and is more portable if the server receives a different DHCP address later.

## Local IP Address Strategy

A local IP address can be useful during setup, but it may change if the router assigns a new DHCP lease.

Example sanitized local IP format:

```text
192.168.x.x
```

Do not commit actual public IP addresses or sensitive network identifiers.

## DHCP Reservation

A DHCP reservation tells the router to keep assigning the same local IP address to the Raspberry Pi.

This is useful because:

* SSH commands stay consistent
* Bookmarks and saved connections remain valid
* Services are easier to find
* Troubleshooting is simpler

However, DHCP reservation may not be available on managed apartment networks or shared network environments.

## Managed Network Limitation

If the home network is managed by an apartment, ISP, or building network provider, router-level DHCP reservation may not be available.

Practical alternatives:

* Use `pi-server.local` hostname access
* Use Tailscale later for stable private networking
* Keep a setup note showing how to check the current local IP
* Avoid exposing services directly to the public internet

## Hostname

Preferred hostname:

```text
pi-server
```

Preferred local network address:

```text
pi-server.local
```

The hostname should be short, clear, and stable.

## Useful Network Commands

Check IP addresses on the server:

```bash
ip addr
```

Show active network connections:

```bash
nmcli connection show
```

Show hostname:

```bash
hostname
```

Show detailed hostname information:

```bash
hostnamectl
```

Test local network reachability from another machine:

```bash
ping pi-server.local
```

SSH using hostname:

```bash
ssh ubuntu@pi-server.local
```

SSH using a temporary local IP placeholder:

```bash
ssh ubuntu@192.168.x.x
```

## Troubleshooting

### Hostname does not work

If this command fails:

```bash
ssh ubuntu@pi-server.local
```

Check:

* The Raspberry Pi is powered on
* The Raspberry Pi is connected to the same local network
* The hostname is set correctly
* mDNS/Avahi is installed and running if needed
* The admin machine supports `.local` hostname resolution

### Local IP changed

If the previous IP no longer works:

* Check the current IP from the router or network device list
* Run `ip addr` directly on the server if local access is available
* Use hostname access when possible
* Configure DHCP reservation if router access is available
* Consider Tailscale later for a more stable private network path

### Managed apartment network

If router configuration is unavailable:

* Use hostname access locally
* Avoid depending on router-level settings
* Avoid public port forwarding
* Use Tailscale or another private VPN-style tool later if remote access is needed

## Security Notes

Do not publicly document:

* Wi-Fi passwords
* Router admin credentials
* Public IP addresses
* Full device MAC addresses
* Private network diagrams with identifying details
* ISP account information
* Screenshots showing personal network names or device identifiers

## Future Improvements

* Confirm final hostname
* Confirm preferred SSH command
* Decide whether DHCP reservation is available
* Add Tailscale notes if used
* Create a simple network diagram
* Document remote access strategy
* Document firewall assumptions
