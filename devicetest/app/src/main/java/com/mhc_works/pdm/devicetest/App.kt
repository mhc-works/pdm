package com.mhc_works.pdm.devicetest

import android.app.Application
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build

class App : Application() {
    override fun onCreate() {
        super.onCreate()
        // Second delivery path next to the manifest receiver, while the process lives. The log says
        // which one fired, so the device test shows whether the manifest receiver alone is enough.
        val filter = IntentFilter(Intent.ACTION_PACKAGE_ADDED).apply { addDataScheme("package") }
        val receiver = PackageAddedReceiver("running process")
        if (Build.VERSION.SDK_INT >= 33) {
            registerReceiver(receiver, filter, Context.RECEIVER_NOT_EXPORTED)
        } else {
            registerReceiver(receiver, filter)
        }
    }
}
