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

## Way out

Test this first. Either tap the WAY OUT button, or from a computer:

```
adb shell am broadcast -n com.mhc_works.pdm.devicetest/.WayOutReceiver -a com.mhc_works.pdm.devicetest.WAY_OUT
```

Both unsuspend every package the app suspended, clear every restriction it added, and give up Device
Owner. The list of what it changed is kept on the device, so this works after a restart. If both fail,
because the app is `testOnly` this always works:

```
adb shell dpm remove-active-admin com.mhc_works.pdm.devicetest/.AdminReceiver
adb shell pm unsuspend --user 0 <package>
```

## Other adb commands

```
adb logcat -s PdmDeviceTest
adb shell appops set com.mhc_works.pdm.devicetest GET_USAGE_STATS allow
adb uninstall com.mhc_works.pdm.devicetest
```

The last one may need the way out first. Phone numbers and package names are typed on the device,
never written into the code.
