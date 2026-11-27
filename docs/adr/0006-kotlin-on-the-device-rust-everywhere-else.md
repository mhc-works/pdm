# Kotlin for the Android app, Rust for everything else

PDM needs an app on the Device and software on the Admin's side. Decided on 2026-11-27: the Android app is written in Kotlin; everything else is written in Rust: the Server, the server side and transport of remote help, and the management of the Devices.

On the Server everything takes data from the network, and Rust keeps that code memory safe. On Android the platform's entry points (the Device Owner receiver, services, accessibility, screen capture, screens) are Kotlin or Java classes anyway.

## Considered Options

- **Rust on the Device behind a thin Kotlin shell:** more build complexity and a JNI boundary for little gain, because the app mostly calls platform interfaces (ADR-0005).
- **One language everywhere:** not possible on Android without that shell.

## Consequences

- The Kotlin app treats everything from the Server as untrusted input and validates it.
- CodeQL already covers Kotlin in this repository's workflow.
