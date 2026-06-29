# Diagrams

This folder will store public-safe diagrams for the home-server lab.

The goal is to visually document the server architecture, network layout, Docker service structure, backup strategy, and future AI/lab-informatics project connections.

## Purpose

Diagrams help explain:

* Server architecture
* Network relationships
* Docker service layout
* Backup flow
* Data flow
* Future project structure
* Troubleshooting concepts

## Planned Diagrams

Possible future diagrams:

```text
home-server-architecture.md
network-layout.md
docker-services.md
backup-flow.md
future-ai-lab-informatics-stack.md
```

## Diagram Standards

Diagrams should be:

* Public-safe
* Clear
* Simple
* Useful
* Updated as the build changes
* Free of private network details
* Free of patient or employer-confidential information

## Security Rules

Do not include:

* Public IP addresses
* Full MAC addresses
* Wi-Fi names or passwords
* Router admin details
* Private service URLs
* Patient data
* Employer data
* Clinical screenshots
* Real accession numbers, MRNs, case IDs, or sample identifiers

Use placeholders instead:

```text
Raspberry Pi Server
Admin Laptop / Chromebook
Home Network
Private Backup Device
Docker Services
Future Portfolio Projects
```

## Possible Architecture Concept

```text
Chromebook / Admin Machine
        |
        | SSH
        v
Raspberry Pi Home Server
        |
        | Docker
        v
Self-Hosted Services
        |
        | Future Use
        v
AI, Data, and Lab-Informatics Projects
```

## Future Improvements

* Add first architecture diagram
* Add Docker service diagram
* Add backup flow diagram
* Add public-safe network diagram
* Add future clinical AI/lab-informatics stack diagram
