# PDM is Device Owner itself; no third-party MDM

A device is to be locked against installs and settings changes and managed from a distance. For that, one app has to be Device Owner. Decided on 2026-11-13: our own app is Device Owner, set up once with `adb` on a device without accounts. No third-party MDM is used, although one would offer silent installation of Play apps.

## Considered Options

- **Android Management API (Google):** could do everything technically (managed Play Store, rules from the cloud). Not open to private persons: the terms allow commercial providers only, since 2025-11-01 enrolling devices needs Google's approval, and new projects have a quota of 0 devices.
- **Headwind MDM Community Edition (self-hosted):** kiosk mode, settings lock and remote control are paid features, Play apps cannot be installed from a distance, there is no ready arm64 package, no OEMConfig.

## Consequences

- Play apps cannot be installed silently; PDM can silently install only APKs it is given.
- A bug in PDM can lock a device out. Every locking feature therefore needs a way out first (see `GLOSSARY.md`).
- Device Owner can only be set while no account is on the device. A used device needs its accounts removed first, or a factory reset.
- Found in the device test: a supervised child account (Family Link) cannot be added next to a Device Owner. Samsung's Knox features for unattended remote control need a partner licence that a private app does not get.
