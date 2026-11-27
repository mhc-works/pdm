# Device Owner interfaces first; PDM builds its own only where the device test shows a gap

For every feature, PDM first uses what Android offers a Device Owner: `DevicePolicyManager` and the related platform mechanisms. Decided on 2026-11-27: PDM builds its own mechanism, or takes another route (an `adb` setup step, an accessibility service, a third-party app), only where the device test has shown that the Device Owner interface does not exist or is refused. The ADR or issue for that feature names the gap.

## Considered Options

- **Own mechanisms by default:** full control, but more code, more permissions and more that breaks with a platform update.
- **Device Owner interfaces first:** chosen. Found in the device test, a run-ahead on a Samsung tablet with Android 11:
  - **Keeping PDM's process alive:** an own foreground service started on `BOOT_COMPLETED` came up about 175 seconds after the screen was ready, needed a permanent notification and four extra permissions, and an app installed in that gap was usable for 82 seconds. The platform's `DeviceAdminService`, which the system binds for the Device Owner, had the process running 8 seconds after the screen was ready, with no notification and no extra permission. It was also bound after an app update without the app being opened.
  - Suspending apps, hiding apps, silent install and removal, user restrictions and the way out all work through Device Owner interfaces.

## Known gaps

Another route is needed here, so the limit of the rule is clear:

- The Play Store cannot be suspended; the system refuses it (ADR-0003).
- Reading app usage needs a separate setup step, because Device Owner does not grant usage access.
- Remote help needs screen sharing and an accessibility service of a third-party app.
- The system dialog shown for a suspended app cannot be extended.

## Consequences

- Fewer permissions and less own code to maintain.
- Behaviour depends on the platform and the manufacturer, so each use is confirmed in the device test, per device.
- A feature proposal states which Device Owner interface it uses, or why none fits.
