package com.mhc_works.pdm.devicetest

import android.os.Handler
import android.os.Looper
import android.util.Log
import java.time.LocalTime
import java.time.temporal.ChronoUnit

/** One log for everything: in memory for the screen, and in logcat under one tag. */
object AppLog {
    const val TAG = "PdmDeviceTest"
    private const val MAX_LINES = 300
    private val lines = ArrayDeque<String>()
    private val main = Handler(Looper.getMainLooper())

    /** Set by the screen while it is shown; called on the main thread. */
    @Volatile
    var onChange: (() -> Unit)? = null

    fun log(message: String) {
        Log.i(TAG, message)
        val line = "${LocalTime.now().truncatedTo(ChronoUnit.SECONDS)} $message"
        synchronized(lines) {
            lines.addLast(line)
            while (lines.size > MAX_LINES) lines.removeFirst()
        }
        main.post { onChange?.invoke() }
    }

    fun error(what: String, t: Throwable) {
        Log.e(TAG, what, t)
        log("FAILED $what: ${t.javaClass.simpleName}: ${t.message}")
    }

    fun text(): String = synchronized(lines) { lines.joinToString("\n") }
}
