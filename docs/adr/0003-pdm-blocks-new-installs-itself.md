# PDM blocks new installs itself, not with the system restriction

The user must not be able to install apps, the admin approves apps from a distance, and installed apps should keep updating by themselves. Decided on 2026-11-26: PDM makes the Play Store unstartable for the user and lets it keep running in the background. Installing from unknown sources stays blocked. We do not set the restriction `DISALLOW_INSTALL_APPS`, because it also blocks automatic updates.

The decision depends on the device test: if the blocked Play Store stops delivering updates, the fallback applies. Then the Play Store stays open, and PDM makes every newly installed app without approval unstartable at once, until the admin approves it.

## Considered Options

- **`DISALLOW_INSTALL_APPS`:** the only real system lock, but it prevents updates.
- **Removing new apps at once:** works for certain, but throws the download away; after a later approval the app has to be downloaded again. Making it unstartable is the better form of the same idea.

## Consequences

- Play apps cannot be installed silently from a distance (ADR-0001). The admin approves on the server; the app is then installed in a remote help session, or by one tap of the user on the Play Store page PDM opens.
- PDM can silently install and update only APKs from its own server, above all itself.
- Updates of Play apps cannot be forced, only allowed.
