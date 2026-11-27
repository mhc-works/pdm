# Devices reach the Server with their own key; rules count only with the Admin's signature

The Admin changes settings on a Device from a distance without a remote help session: the Device fetches its rules from the Server (ADR-0002). That connection crosses the internet, and whoever controls it controls the Device. Decided on 2026-11-27:

- **Device to Server:** HTTPS with certificates on both sides (mutual TLS). The Server is reachable from the internet and refuses, in the TLS handshake, every connection without the certificate of an enrolled Device. The Device's private key is created on the Device in the Android Keystore and never leaves it. The Device accepts only the Server key it was given at enrolment.
- **Admin to Server:** the Admin signs in with a passkey, not a password.
- **Rules:** a Device applies a rule only if it carries the signature of an admin key the Device trusts. The admin key is not stored on the Server. Every rule carries a rising number, and a Device refuses a rule older than the last one it applied.
- **Handover:** the list of admin keys a Device trusts is itself changed by a signed rule. So an Admin can hand over to another person, move to a new phone, or add a second Admin.
- **Loss:** a recovery key, created at setup and kept offline, can do one thing only: put a new admin key in place. If it is lost too, the way out on the Device remains, and the Device is enrolled again.

## Considered Options

- **Server reachable only through a VPN:** a little less to attack, but every Device needs a third-party VPN app that is always on (against ADR-0005), and no rule arrives while the VPN is down.
- **Rules only at home on the Wi-Fi:** contradicts ADR-0002, which wants Devices managed while away.
- **A list of apps that may talk to the Server:** rejected. A package name can be forged; the Server admits a Device by its key.
- **Passkeys for Devices:** a passkey needs a person who confirms. The key in the Android Keystore is the same technique without one.
- **Trusting whatever the Server sends:** simpler, but then whoever takes over the Server has all Devices.
- **Signatures only for rules that lock:** fewer confirmations for the Admin, but two paths in the code.

## Consequences

- This narrows a consequence of ADR-0002: whoever takes over the Server can still read the reports and withhold rules, but can no longer lock a Device, remove apps or change rules.
- The Admin confirms every change of rules with the admin key, so the Admin needs a tool that holds it.
- The admin key and the recovery key are locks in the sense of `GLOSSARY.md`: the way out on the Device must work without either.
- Not decided yet: how a Device is enrolled and gets the Server key and the first admin key (the QR code of ADR-0001 is the candidate); where the admin key lives; the form of the recovery key (a printed code is the candidate); whether the Server asks a Device for key attestation, to show that the key sits in real hardware inside PDM.
