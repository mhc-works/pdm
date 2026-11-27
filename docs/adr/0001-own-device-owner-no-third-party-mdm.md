# PDM is Device Owner itself; no third-party MDM

A device is to be locked against installs and settings changes and managed from a distance. For that, one app has to be Device Owner. Decided on 2026-11-13: our own app is Device Owner, set up once on a device without accounts. PDM is distributed only through a closed test track of the Google Play Store, and updates reach the Device through the Play Store. PDM supports two ways to set it up: with `adb`, or with a factory reset and a QR code (see Consequences). No third-party MDM is used, although one would offer silent installation of Play apps.

## Considered Options

- **Android Management API (Google):** could do everything technically (managed Play Store, rules from the cloud). Not open to private persons: the terms allow commercial providers only, since 2025-11-01 enrolling devices needs Google's approval, and new projects have a quota of 0 devices.
- **Headwind MDM Community Edition (self-hosted):** kiosk mode, settings lock and remote control are paid features, Play apps cannot be installed from a distance, there is no ready arm64 package, no OEMConfig.

## Consequences

- Play apps cannot be installed silently; PDM can silently install only APKs it is given.
- A bug in PDM can lock a device out. Every locking feature therefore needs a way out first (see `GLOSSARY.md`).
- Device Owner can only be set while no account is on the device. A used device needs its accounts removed first, or a factory reset. Two ways to set it up, both supported:
  1. With `adb`, without losing data: install PDM from the Play Store, remove every account from the Device, run the one `dpm set-device-owner` command from a computer, add the account again.
  2. With a factory reset: the Admin scans a QR code in the setup wizard; the Device downloads the PDM APK from the address in the code and makes it Device Owner. That APK must carry the same signature as the Play Store version, so the Play Store updates it afterwards.
- `adb` is used only for that one command in way 1; nothing in daily operation or in the way out depends on it. PDM is never a `testOnly` build: the Play Store does not accept one, and a `testOnly` app cannot update itself by install session (found in the device test).
- Found in the device test (run-ahead on a Samsung tablet with Android 11): removing the accounts instead of a factory reset is enough to set Device Owner. It can be set, given up through the way out and set again repeatedly, and the account can be added again afterwards.
- Still to be confirmed in the device test: that the Play Store updates an app that is Device Owner, way 2 as a whole, and that Google accepts a Device Owner app in a closed test.
- Found in the device test: a supervised child account (Family Link) cannot be added next to a Device Owner. An ordinary Google account can be added after Device Owner is set; this was shown in the earlier tests. Samsung's Knox features for unattended remote control need a partner licence that a private app does not get.
