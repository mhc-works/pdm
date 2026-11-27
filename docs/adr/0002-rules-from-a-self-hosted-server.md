# PDM is a management app with a self-hosted server, not a launcher

The project began as a home screen for one person's tablet. Decided on 2026-11-26: it is a management and security app for Android devices that takes its configuration from a server the admin hosts. PDM has no home screen of its own and no kiosk mode; how the home screen looks is left to the device. A kiosk mode may come later and has no priority.

## Considered Options

- **Two profiles on one base** (a kiosk for one user, an open device with rules for others): rejected, because the kiosk doubles the work and the device's own simple mode covers easy operation well enough.
- **Third-party MDM:** ruled out for the reasons in ADR-0001.

## Consequences

- The server is a service of its own on the admin's machine. Devices contact it themselves, so it works for devices that are away from home.
- The server can lock every device, remove apps and read usage data. Whoever takes it over has all devices. Work on it carries the label `security-review`.
- Without a kiosk the user can in principle open the Play Store and the Android settings. PDM has to lock each one (installs: ADR-0003).
- Remote help needs the User's active grant on the device for every session. That is intended. Decided on 2026-11-27: Android's own screen-sharing dialog stays, because the platform shows it for every session and a Device Owner cannot suppress it, and PDM additionally asks for a PIN of the User, so that a session is not granted with a single tap.
- Remote help is part of PDM itself and fully preconfigured: the User never types a server address or handles a separate app. The stock RustDesk app is not used. Found in the device test: about 15 taps for the first setup, 4 taps and a forced waiting time per later session, server address and key typed by hand, and its sharing service does not survive a restart. Its client can only be reused as a fork of the whole app, not as a library.
- The accessibility service that remote operation needs is switched on by hand once. When the User presses the help button, PDM checks it and, if it is off, leads the User to the right settings page.
- Not decided yet: the transport. An open protocol such as WebRTC with a self-hosted relay is the candidate; picture quality is to be compared in a prototype. An existing RustDesk server is not a requirement.
- User and admin can be the same person, for example when the admin manages their own device for security.
