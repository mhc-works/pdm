# PDM is a management app with a self-hosted server, not a launcher

The project began as a home screen for one person's tablet. Decided on 2026-11-26: it is a management and security app for Android devices that takes its configuration from a server the admin hosts. PDM has no home screen of its own and no kiosk mode; how the home screen looks is left to the device. A kiosk mode may come later and has no priority.

## Considered Options

- **Two profiles on one base** (a kiosk for one user, an open device with rules for others): rejected, because the kiosk doubles the work and the device's own simple mode covers easy operation well enough.
- **Third-party MDM:** ruled out for the reasons in ADR-0001.

## Consequences

- The server is a service of its own on the admin's machine. Devices contact it themselves, so it works for devices that are away from home.
- The server can lock every device, remove apps and read usage data. Whoever takes it over has all devices. Work on it carries the label `security-review`.
- Without a kiosk the user can in principle open the Play Store and the Android settings. PDM has to lock each one (installs: ADR-0003).
- Remote help needs the user's confirmation on the device for every session. That is intended.
- User and admin can be the same person, for example when the admin manages their own device for security.
