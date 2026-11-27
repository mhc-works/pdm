package com.mhc_works.pdm.devicetest

import android.app.PendingIntent
import android.app.admin.DeviceAdminReceiver
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.content.pm.PackageInstaller
import android.os.Build
import android.util.Base64
import android.telephony.SmsManager
import java.io.InputStream
import java.security.SecureRandom

const val PLAY_STORE = "com.android.vending"
const val RUSTDESK = "com.carriez.flutter_hbb"
const val ACTION_WAY_OUT = "com.mhc_works.pdm.devicetest.WAY_OUT"

class AdminReceiver : DeviceAdminReceiver()

/** Everything that changes the device. Each function logs its result or the exception, and never throws. */
class Actions(context: Context) {
    private val ctx = context.applicationContext
    private val store = Store(ctx)
    private val dpm = ctx.getSystemService(DevicePolicyManager::class.java)
    private val admin = ComponentName(ctx, AdminReceiver::class.java)

    private fun attempt(what: String, block: () -> Unit) {
        try {
            block()
        } catch (t: Throwable) {
            AppLog.error(what, t)
        }
    }

    fun status() = attempt("status") {
        AppLog.log("Device Owner: ${dpm.isDeviceOwnerApp(ctx.packageName)}")
        AppLog.log("Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT}), ${Build.MANUFACTURER} ${Build.MODEL}")
        AppLog.log("Restrictions set by this app: ${store.restrictions.sorted()}")
        AppLog.log("Packages suspended by this app: ${store.suspended.sorted()}")
        AppLog.log("Packages hidden by this app: ${store.hidden.sorted()}")
        AppLog.log("Watch new installs: ${store.watchNewInstalls}")
    }

    /** Returns the packages the system refused to change (empty array means all done). */
    private fun setSuspended(packages: List<String>, suspended: Boolean): List<String> {
        val refused = dpm.setPackagesSuspended(admin, packages.toTypedArray(), suspended).toList()
        val done = packages - refused.toSet()
        store.suspended = if (suspended) store.suspended + done else store.suspended - done.toSet()
        return refused
    }

    fun suspend(pkg: String, suspended: Boolean) = attempt("${if (suspended) "suspend" else "unsuspend"} $pkg") {
        val refused = setSuspended(listOf(pkg), suspended)
        AppLog.log("${if (suspended) "suspend" else "unsuspend"} $pkg -> refused: $refused")
    }

    /** Returns whether the system accepted the change. */
    private fun setHidden(pkg: String, hidden: Boolean): Boolean {
        val ok = dpm.setApplicationHidden(admin, pkg, hidden)
        if (ok) store.hidden = if (hidden) store.hidden + pkg else store.hidden - pkg
        return ok
    }

    fun hide(pkg: String, hidden: Boolean) = attempt("${if (hidden) "hide" else "unhide"} $pkg") {
        AppLog.log("${if (hidden) "hide" else "unhide"} $pkg -> ${setHidden(pkg, hidden)}")
    }

    fun setPin(pin: String) = attempt("set PIN") {
        if (pin.length < 4) {
            AppLog.log("set PIN refused: shorter than 4 digits")
            return@attempt
        }
        val salt = ByteArray(16).also { SecureRandom().nextBytes(it) }
        store.pinSalt = Base64.encodeToString(salt, Base64.NO_WRAP)
        store.pinHash = Base64.encodeToString(hashPin(salt, pin), Base64.NO_WRAP)
        AppLog.log("PIN set")
    }

    fun releaseWithPin(pin: String, pkg: String) = attempt("release with PIN $pkg") {
        if (store.pinHash.isEmpty()) {
            AppLog.log("no PIN set")
        } else if (!verifyPin(Base64.decode(store.pinSalt, Base64.NO_WRAP), Base64.decode(store.pinHash, Base64.NO_WRAP), pin)) {
            AppLog.log("wrong PIN")
        } else {
            AppLog.log("PIN accepted, releasing $pkg")
            suspend(pkg, false)
            hide(pkg, false)
        }
    }

    fun setRestriction(key: String, on: Boolean) = attempt("restriction $key") {
        if (on) {
            dpm.addUserRestriction(admin, key)
            store.restrictions = store.restrictions + key
        } else {
            dpm.clearUserRestriction(admin, key)
            store.restrictions = store.restrictions - key
        }
        AppLog.log("restriction $key ${if (on) "added" else "cleared"}")
    }

    /** Lifts everything this app set, then gives up Device Owner. Reports every step. */
    fun wayOut() {
        attempt("way out") {
            if (!dpm.isDeviceOwnerApp(ctx.packageName)) {
                AppLog.log("WAY OUT: this app is not Device Owner, nothing to lift")
                return@attempt
            }
            val packages = store.suspended.toList()
            if (packages.isNotEmpty()) {
                attempt("way out: unsuspend") {
                    AppLog.log("WAY OUT: unsuspend $packages -> refused: ${setSuspended(packages, false)}")
                }
            }
            for (pkg in store.hidden.toList()) {
                attempt("way out: unhide $pkg") {
                    AppLog.log("WAY OUT: unhide $pkg -> ${setHidden(pkg, false)}")
                }
            }
            for (key in store.restrictions.toList()) {
                attempt("way out: clear restriction $key") {
                    dpm.clearUserRestriction(admin, key)
                    store.restrictions = store.restrictions - key
                    AppLog.log("WAY OUT: restriction $key cleared")
                }
            }
            @Suppress("DEPRECATION")
            dpm.clearDeviceOwnerApp(ctx.packageName)
            AppLog.log("WAY OUT: Device Owner cleared, still owner: ${dpm.isDeviceOwnerApp(ctx.packageName)}")
        }
    }

    fun uninstall(pkg: String) = attempt("uninstall $pkg") {
        ctx.packageManager.packageInstaller.uninstall(pkg, resultIntent(ResultReceiver.UNINSTALL, pkg).intentSender)
        AppLog.log("uninstall $pkg requested, waiting for the result")
    }

    /** Streams the APK into an install session; the outcome arrives at ResultReceiver. */
    fun install(apk: InputStream, label: String) = attempt("install $label") {
        val installer = ctx.packageManager.packageInstaller
        val params = PackageInstaller.SessionParams(PackageInstaller.SessionParams.MODE_FULL_INSTALL)
        if (Build.VERSION.SDK_INT >= 31) {
            params.setRequireUserAction(PackageInstaller.SessionParams.USER_ACTION_NOT_REQUIRED)
        }
        val id = installer.createSession(params)
        installer.openSession(id).use { session ->
            apk.use { input ->
                session.openWrite("base.apk", 0, -1).use { out ->
                    input.copyTo(out)
                    session.fsync(out)
                }
            }
            session.commit(resultIntent(ResultReceiver.INSTALL, label, id).intentSender)
        }
        AppLog.log("install session $id committed for $label, waiting for the result")
    }

    fun sendTestSms(number: String, text: String) = attempt("sms") {
        val sms = if (Build.VERSION.SDK_INT >= 31) {
            ctx.getSystemService(SmsManager::class.java)
        } else {
            @Suppress("DEPRECATION")
            SmsManager.getDefault()
        }
        sms.sendTextMessage(number, null, text, resultIntent(ResultReceiver.SMS, "sms"), null)
        AppLog.log("sms handed to the system, waiting for the sent result")
    }

    /** The decision for one newly added package; called from PackageAddedReceiver. */
    fun handleNewPackage(pkg: String, source: String) = attempt("watch $pkg") {
        if (!store.watchNewInstalls) return@attempt
        val system = try {
            isSystem(ctx.packageManager.getApplicationInfo(pkg, 0))
        } catch (e: Exception) {
            AppLog.log("watch $pkg: cannot read its flags (${e.javaClass.simpleName}), treated as not system")
            false
        }
        val suspend = shouldSuspend(pkg, parseApproved(store.approvedText), ctx.packageName, system)
        AppLog.log("watch $pkg: new package via $source receiver, system=$system, suspend=$suspend")
        if (suspend) AppLog.log("watch $pkg: refused: ${setSuspended(listOf(pkg), true)}")
    }

    private fun isSystem(info: ApplicationInfo) =
        info.flags and (ApplicationInfo.FLAG_SYSTEM or ApplicationInfo.FLAG_UPDATED_SYSTEM_APP) != 0

    private fun isOwner(): Boolean {
        val owner = dpm.isDeviceOwnerApp(ctx.packageName)
        if (!owner) AppLog.log("watch: this app is not Device Owner, not watching")
        return owner
    }

    /** The switch was turned on: take the installed apps as approved, then sweep. */
    fun watchOn() = attempt("watch on") {
        // Approval means "was there when watching began, or the admin approved it"; turning off removes nothing.
        val installed = ctx.packageManager.getInstalledApplications(0).filterNot { isSystem(it) }.map { it.packageName }
        val before = parseApproved(store.approvedText).size
        store.approvedText = approvedWith(store.approvedText, installed)
        AppLog.log("watch on: ${parseApproved(store.approvedText).size - before} installed packages added to the approved list")
        sweep()
    }

    /** Suspends every installed package the fallback would have suspended and this app has not yet. */
    fun sweep() = attempt("sweep") {
        if (!store.watchNewInstalls || !isOwner()) return@attempt
        val approved = parseApproved(store.approvedText)
        val installed = ctx.packageManager.getInstalledApplications(0)
        var suspended = 0
        for (info in installed) {
            val pkg = info.packageName
            if (pkg in store.suspended || !shouldSuspend(pkg, approved, ctx.packageName, isSystem(info))) continue
            attempt("sweep $pkg") {
                AppLog.log("sweep $pkg: suspended, refused: ${setSuspended(listOf(pkg), true)}")
                suspended++
            }
        }
        AppLog.log("sweep done: ${installed.size} checked, $suspended suspended")
    }

    /** The admin's decision: put the package on the approved list and unsuspend it. */
    fun approve(pkg: String) = attempt("approve $pkg") {
        store.approvedText = approvedWith(store.approvedText, listOf(pkg))
        AppLog.log("approve $pkg: added to the approved list")
        suspend(pkg, false)
    }

    private fun resultIntent(kind: String, label: String, id: Int = 0): PendingIntent {
        val intent = Intent(ctx, ResultReceiver::class.java)
            .setAction(kind)
            .putExtra(ResultReceiver.EXTRA_LABEL, label)
        // Mutable: the system adds the status extras to it.
        return PendingIntent.getBroadcast(ctx, id + kind.hashCode(), intent, PendingIntent.FLAG_MUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
    }
}
