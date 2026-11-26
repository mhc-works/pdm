package com.mhc_works.pdm.devicetest

/** Pure logic, no Android classes, so it runs in plain JUnit tests. */

/** One package per line; blank lines and lines starting with # are ignored. */
fun parseApproved(text: String): Set<String> =
    text.lineSequence().map { it.trim() }.filter { it.isNotEmpty() && !it.startsWith("#") }.toSet()

/** ADR-0003 fallback: true when a newly added package has to be suspended at once. */
fun shouldSuspend(
    newPackage: String,
    approved: Set<String>,
    ownPackage: String,
    isSystemApp: Boolean,
): Boolean = !isSystemApp && newPackage != ownPackage && newPackage !in approved

/** Foreground time per package in milliseconds, longest first, without packages that never ran. */
fun topForeground(millisByPackage: Map<String, Long>, limit: Int): List<Pair<String, Long>> =
    millisByPackage.filter { it.value > 0 }.toList()
        .sortedWith(compareByDescending<Pair<String, Long>> { it.second }.thenBy { it.first })
        .take(limit)
