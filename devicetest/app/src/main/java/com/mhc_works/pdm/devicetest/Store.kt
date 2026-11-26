package com.mhc_works.pdm.devicetest

import android.content.Context
import android.content.SharedPreferences

/** What this app changed, kept on disk so the way out is complete after a restart. */
class Store(context: Context) {
    private val prefs: SharedPreferences =
        context.applicationContext.getSharedPreferences("devicetest", Context.MODE_PRIVATE)

    var restrictions: Set<String>
        get() = prefs.getStringSet(RESTRICTIONS, emptySet()) ?: emptySet()
        set(value) = prefs.edit().putStringSet(RESTRICTIONS, value.toSet()).apply()

    var suspended: Set<String>
        get() = prefs.getStringSet(SUSPENDED, emptySet()) ?: emptySet()
        set(value) = prefs.edit().putStringSet(SUSPENDED, value.toSet()).apply()

    var watchNewInstalls: Boolean
        get() = prefs.getBoolean(WATCH, false)
        set(value) = prefs.edit().putBoolean(WATCH, value).apply()

    var approvedText: String
        get() = prefs.getString(APPROVED, "") ?: ""
        set(value) = prefs.edit().putString(APPROVED, value).apply()

    private companion object {
        const val RESTRICTIONS = "restrictions"
        const val SUSPENDED = "suspended"
        const val WATCH = "watch"
        const val APPROVED = "approved"
    }
}
