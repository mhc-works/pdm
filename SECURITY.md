# Security

PDM is Device Owner on the devices it manages, and its server can lock them, remove apps and read
usage data. A security bug here can lock people out of their own devices or hand them to someone
else. Please report anything you find privately, not in a public issue.

## How to report

Use GitHub's private vulnerability reporting of [mhc-works/pdm](https://github.com/mhc-works/pdm):
open the repository's Security tab and choose **Report a vulnerability**. Only the maintainers see
the report.

Please include what is affected, the steps to reproduce it, and what an attacker could do with it.

## What counts

- A way around a lock on a managed device, or a way to take over a device or the server.
- Anything that sends data from a device to a place the admin did not choose.
- A device that can no longer be unlocked or released from management.
- Anything in a pull request that runs code on a contributor's or maintainer's machine.
- Private data or a secret in this repository or its history.

## What happens next

You get a reply within a few days. Fixes go into `main` with credit to you, unless you would rather
stay anonymous. Please give a fix a reasonable chance to ship before you publish details.
