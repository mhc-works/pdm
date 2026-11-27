# PDM (Private Device Manager)

An app for managing and securing a family's own Android devices. It locks settings and app installs, reports app usage, and takes its rules from a server the admin hosts, through which the admin manages the devices from a distance.

English is the source language of this project (ADR-0004). Each term names its German counterpart, because German is the first language the app is translated into.

## Language

### Roles

**User**:
The person who uses a managed device every day. They cannot change the rules on the device. User and admin can be the same person.
_German_: Nutzer
_Avoid_: end user, customer, senior, child

**Admin**:
The person who sets devices up and manages them through the server, mostly from a distance.
_German_: Admin
_Avoid_: administrator, manager, parent, caregiver

### System

**PDM**:
The app on the device. It is Device Owner there and enforces the server's rules.
_German_: PDM
_Avoid_: launcher, agent, MDM client

**Device**:
An Android tablet or phone on which PDM is set up as Device Owner.
_German_: Gerät
_Avoid_: client, endpoint

**Server**:
The service on the admin's own machine that holds the rules of all devices, collects their reports and takes approvals.
_German_: Server
_Avoid_: backend, cloud, MDM server

**Remote help**:
A session in which the admin sees and operates the screen of a device. The user starts it with one button and confirms it on the device.
_German_: Fernhilfe
_Avoid_: remote support, remote access, remote maintenance

### Protection

**Approval**:
The admin's decision, made on the server, that an app may be present and startable on a device. Without approval the user can neither install nor start an app.
_German_: Freigabe
_Avoid_: whitelist, permission, authorization

**Admin key**:
The key with which the admin signs rules. A device applies a rule only with the signature of an admin key it trusts. It is not stored on the server.
_German_: Admin-Schlüssel
_Avoid_: master key, root key, signing key

**Recovery key**:
A key kept offline that can only put a new admin key in place when the old one is lost.
_German_: Wiederherstellungsschlüssel
_Avoid_: backup key, master key, emergency key

**Way out**:
A way to lift the lock of a device that still works when PDM, the server or remote help fails. Every locking feature needs one before it is built.
_German_: Ausweg
_Avoid_: backdoor, emergency exit, escape hatch

### Method

**Device test**:
A check with a throwaway app that settles whether the open assumptions about locks, updates and remote help hold. It runs in three stages: the emulator, then a Samsung tablet in daily use, then the tablet PDM is first meant for. It comes before the spec and before PDM is built.
_German_: Gerätetest
_Avoid_: spike, prototype, feasibility study
