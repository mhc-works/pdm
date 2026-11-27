package com.mhc_works.pdm.devicetest

import java.security.MessageDigest

/** Pure logic, no Android classes, so it runs in plain JUnit tests. */

/** One package per line; blank lines and lines starting with # are ignored. */
fun parseApproved(text: String): Set<String> =
    text.lineSequence().map { it.trim() }.filter { it.isNotEmpty() && !it.startsWith("#") }.toSet()

/** The approved text with the packages not yet in it appended, one per line. */
fun approvedWith(text: String, packages: Collection<String>): String {
    val missing = packages.filter { it !in parseApproved(text) }.distinct()
    return if (missing.isEmpty()) text else (text.trimEnd() + "\n" + missing.joinToString("\n")).trimStart('\n')
}

/** ADR-0003 fallback: true when a newly added package has to be suspended at once. */
fun shouldSuspend(
    newPackage: String,
    approved: Set<String>,
    ownPackage: String,
    isSystemApp: Boolean,
): Boolean = !isSystemApp && newPackage != ownPackage && newPackage !in approved

// shortcut: salted SHA-256 and no attempt limit, PDM needs a real KDF and a lockout
fun hashPin(salt: ByteArray, pin: String): ByteArray =
    MessageDigest.getInstance("SHA-256").digest(salt + pin.toByteArray())

fun verifyPin(salt: ByteArray, hash: ByteArray, pin: String): Boolean =
    MessageDigest.isEqual(hash, hashPin(salt, pin))

/** Foreground time per package in milliseconds, longest first, without packages that never ran. */
fun topForeground(millisByPackage: Map<String, Long>, limit: Int): List<Pair<String, Long>> =
    millisByPackage.filter { it.value > 0 }.toList()
        .sortedWith(compareByDescending<Pair<String, Long>> { it.second }.thenBy { it.first })
        .take(limit)
