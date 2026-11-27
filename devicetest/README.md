# Device test app

A throwaway Android app for the **device test** (see [GLOSSARY.md](../GLOSSARY.md)). It settles the
open assumptions of ADR-0001 to ADR-0003: can an app that is Device Owner block the Play Store without
stopping updates, silently install and uninstall, see usage, start remote help and send a text. It is
**not PDM** and will be deleted when the test is done.

It is a standalone Gradle project (`com.mhc_works.pdm.devicetest`, one Activity, no libraries).
Every action logs its result or the exception text to the screen and to logcat under the tag
`PdmDeviceTest`. Log lines are English only (ADR-0004); labels have a German translation.

## Build

```
cd devicetest
./gradlew testDebugUnitTest lintDebug assembleDebug
```

CI runs the same on pull requests. The app is `testOnly`, so install it with `-t`.

## Set up a device

Device Owner can only be set while no account is on the device (ADR-0001). Placeholders only below:

```
adb install -t app/build/outputs/apk/debug/app-debug.apk
adb shell dpm set-device-owner com.mhc_works.pdm.devicetest/.AdminReceiver
```

## Watch new installs

The "watch new installs" switch (the fallback of ADR-0003) relies on a DeviceAdminService that the system binds as long as the app is Device Owner, which keeps the app
process alive without a notification. Every process start sweeps all installed packages, suspending those
that are not approved. Switching it on takes every installed non-system app as approved, so the sweep cannot
lock the existing apps; switching it off removes nothing from the list.

## Way out

Test this first. Either tap the WAY OUT button, or from a computer:

```
adb shell am broadcast -n com.mhc_works.pdm.devicetest/.WayOutReceiver -a com.mhc_works.pdm.devicetest.WAY_OUT
```

Both unsuspend every package the app suspended, unhide every package it hid, clear every restriction it added, and give up Device
Owner. The list of what it changed is kept on the device, so this works after a restart. If both fail,
because the app is `testOnly` this always works:

```
adb shell dpm remove-active-admin com.mhc_works.pdm.devicetest/.AdminReceiver
```

It removes Device Owner and the restrictions, but suspended packages stay suspended, and
`adb shell pm unsuspend` cannot lift them (found on Android 16). To lift them, set Device Owner again
and send the way out broadcast above.

## Other adb commands

```
adb logcat -s PdmDeviceTest
adb shell appops set com.mhc_works.pdm.devicetest GET_USAGE_STATS allow
adb uninstall com.mhc_works.pdm.devicetest
```

The last one may need the way out first. Phone numbers and package names are typed on the device,
never written into the code. The one exception is the package field, which starts with Samsung's
Notes app as a harmless app to suspend or hide.
