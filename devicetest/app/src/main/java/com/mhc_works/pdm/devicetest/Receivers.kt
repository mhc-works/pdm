package com.mhc_works.pdm.devicetest

import android.app.Activity
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInstaller
import android.os.Build

/** adb shell am broadcast -n <package>/.WayOutReceiver -a com.mhc_works.pdm.devicetest.WAY_OUT */
class WayOutReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        AppLog.log("WAY OUT broadcast received, action=${intent.action}")
        if (intent.action == ACTION_WAY_OUT) Actions(context).wayOut()
    }
}

/** A package was added: the fallback of ADR-0003 decides, if the switch is on. */
class PackageAddedReceiver @JvmOverloads constructor(private val source: String = "manifest") : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_PACKAGE_ADDED) return
        if (intent.getBooleanExtra(Intent.EXTRA_REPLACING, false)) return
        val pkg = intent.data?.schemeSpecificPart ?: return
        Actions(context).handleNewPackage(pkg, source)
    }
}

/** Results of install and uninstall sessions and of the test SMS. */
class ResultReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val label = intent.getStringExtra(EXTRA_LABEL)
        when (intent.action) {
            SMS -> {
                val code = resultCode
                AppLog.log(if (code == Activity.RESULT_OK) "sms sent" else "sms FAILED, result code $code (SmsManager.RESULT_*)")
            }
            INSTALL, UNINSTALL -> {
                val status = intent.getIntExtra(PackageInstaller.EXTRA_STATUS, Int.MIN_VALUE)
                val message = intent.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE)
                AppLog.log("${intent.action} $label: status=$status (${statusName(status)}) message=$message")
                if (status == PackageInstaller.STATUS_PENDING_USER_ACTION) {
                    val confirm = if (Build.VERSION.SDK_INT >= 33) {
                        intent.getParcelableExtra(Intent.EXTRA_INTENT, Intent::class.java)
                    } else {
                        @Suppress("DEPRECATION")
                        intent.getParcelableExtra(Intent.EXTRA_INTENT)
                    }
                    if (confirm != null) {
                        AppLog.log("the system wants a tap from the user, opening its dialog")
                        context.startActivity(confirm.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                    }
                }
            }
        }
    }

    private fun statusName(status: Int) = when (status) {
        PackageInstaller.STATUS_SUCCESS -> "SUCCESS"
        PackageInstaller.STATUS_PENDING_USER_ACTION -> "PENDING_USER_ACTION"
        PackageInstaller.STATUS_FAILURE -> "FAILURE"
        PackageInstaller.STATUS_FAILURE_BLOCKED -> "FAILURE_BLOCKED"
        PackageInstaller.STATUS_FAILURE_ABORTED -> "FAILURE_ABORTED"
        PackageInstaller.STATUS_FAILURE_INVALID -> "FAILURE_INVALID"
        PackageInstaller.STATUS_FAILURE_CONFLICT -> "FAILURE_CONFLICT"
        PackageInstaller.STATUS_FAILURE_STORAGE -> "FAILURE_STORAGE"
        PackageInstaller.STATUS_FAILURE_INCOMPATIBLE -> "FAILURE_INCOMPATIBLE"
        else -> "UNKNOWN"
    }

    companion object {
        const val INSTALL = "com.mhc_works.pdm.devicetest.INSTALL_RESULT"
        const val UNINSTALL = "com.mhc_works.pdm.devicetest.UNINSTALL_RESULT"
        const val SMS = "com.mhc_works.pdm.devicetest.SMS_RESULT"
        const val EXTRA_LABEL = "label"
    }
}
