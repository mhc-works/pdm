package com.mhc_works.pdm.devicetest

import android.app.Activity
import android.app.AppOpsManager
import android.app.usage.UsageStatsManager
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Typeface
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Process
import android.provider.Settings
import android.text.Editable
import android.text.InputType
import android.text.TextWatcher
import android.text.format.DateUtils
import android.view.View
import android.view.ViewGroup
import android.view.WindowInsets
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.Switch
import android.widget.TextView
import java.time.LocalDate
import java.time.ZoneId

/** One screen: sections of buttons on top, the log below. */
class MainActivity : Activity() {
    private lateinit var actions: Actions
    private lateinit var store: Store
    private lateinit var column: LinearLayout
    private lateinit var logView: TextView
    private lateinit var logScroll: ScrollView
    private lateinit var packageField: EditText
    private lateinit var approvedField: EditText
    private var pendingSmsNumber: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        actions = Actions(this)
        store = Store(this)

        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        root.setOnApplyWindowInsetsListener { view, insets ->
            if (Build.VERSION.SDK_INT >= 30) {
                val bars = insets.getInsets(WindowInsets.Type.systemBars() or WindowInsets.Type.ime())
                view.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            } else {
                @Suppress("DEPRECATION")
                view.setPadding(insets.systemWindowInsetLeft, insets.systemWindowInsetTop,
                    insets.systemWindowInsetRight, insets.systemWindowInsetBottom)
            }
            insets
        }
        column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(16), dp(8), dp(16), dp(8))
        }
        root.addView(ScrollView(this).apply { addView(column) }, LinearLayout.LayoutParams(MATCH, 0, 3f))
        logView = TextView(this).apply {
            typeface = Typeface.MONOSPACE
            textSize = 11f
            setTextIsSelectable(true)
            setPadding(dp(16), dp(8), dp(16), dp(8))
        }
        logScroll = ScrollView(this).apply { addView(logView) }
        root.addView(logScroll, LinearLayout.LayoutParams(MATCH, 0, 2f))
        setContentView(root)

        buildSections()
    }

    private fun buildSections() {
        section(R.string.status_title)
        button(R.string.status_button) { actions.status() }

        section(R.string.way_out_title)
        button(R.string.way_out_button) { actions.wayOut() }

        section(R.string.play_store_title)
        row(
            R.string.play_store_suspend to { actions.suspend(PLAY_STORE, true) },
            R.string.play_store_unsuspend to { actions.suspend(PLAY_STORE, false) },
        )

        section(R.string.restriction_title)
        val restrictionField = field(R.string.restriction_hint, "no_install_unknown_sources")
        row(
            R.string.restriction_add to { actions.setRestriction(restrictionField.text.toString().trim(), true) },
            R.string.restriction_clear to { actions.setRestriction(restrictionField.text.toString().trim(), false) },
        )

        section(R.string.any_app_title)
        // Samsung Notes: harmless to suspend or hide, preinstalled on the test tablets.
        packageField = field(R.string.package_hint, "com.samsung.android.app.notes")
        row(
            R.string.suspend to { actions.suspend(pkg(), true) },
            R.string.unsuspend to { actions.suspend(pkg(), false) },
            R.string.uninstall to { actions.uninstall(pkg()) },
        )
        row(
            R.string.hide to { actions.hide(pkg(), true) },
            R.string.unhide to { actions.hide(pkg(), false) },
        )

        section(R.string.pin_title)
        val pinField = field(R.string.pin_hint, "").apply {
            inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_VARIATION_PASSWORD
        }
        row(
            R.string.pin_set to { actions.setPin(pinField.text.toString()); pinField.setText("") },
            R.string.pin_release to { actions.releaseWithPin(pinField.text.toString(), pkg()); pinField.setText("") },
        )

        section(R.string.watch_title)
        column.addView(Switch(this).apply {
            setText(R.string.watch_switch)
            isChecked = store.watchNewInstalls
            setOnCheckedChangeListener { _, on ->
                store.watchNewInstalls = on
                AppLog.log("watch new installs: $on")
                if (on) actions.watchOn()
                approvedField.setText(store.approvedText)
            }
        })
        approvedField = field(R.string.approved_hint, store.approvedText).apply {
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE
            minLines = 3
            addTextChangedListener(object : TextWatcher {
                override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) = Unit
                override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) = Unit
                override fun afterTextChanged(s: Editable?) {
                    store.approvedText = s.toString()
                }
            })
        }
        button(R.string.approve) {
            actions.approve(pkg())
            approvedField.setText(store.approvedText)
        }

        section(R.string.install_title)
        button(R.string.install_button) {
            val pick = Intent(Intent.ACTION_OPEN_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType("*/*")
            try {
                @Suppress("DEPRECATION")
                startActivityForResult(pick, REQ_APK)
            } catch (t: Throwable) {
                AppLog.error("file picker", t)
            }
        }

        section(R.string.usage_title)
        button(R.string.usage_check) { AppLog.log("usage access granted: ${usageGranted()}") }
        button(R.string.usage_open) {
            try {
                startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS))
            } catch (t: Throwable) {
                AppLog.error("usage access settings", t)
            }
        }
        button(R.string.usage_list) { listUsage() }

        section(R.string.remote_title)
        button(R.string.remote_button) { remoteHelp() }

        section(R.string.sms_title)
        val numberField = field(R.string.sms_number_hint, "").apply { inputType = InputType.TYPE_CLASS_PHONE }
        button(R.string.sms_send) { sendSms(numberField.text.toString().trim()) }
    }

    override fun onResume() {
        super.onResume()
        AppLog.onChange = { refreshLog() }
        refreshLog()
    }

    override fun onPause() {
        AppLog.onChange = null
        super.onPause()
    }

    @Deprecated("Framework Activity result API, enough for one screen")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val uri = data?.data
        if (requestCode != REQ_APK || resultCode != RESULT_OK || uri == null) {
            AppLog.log("no APK picked (result code $resultCode)")
            return
        }
        AppLog.log("APK picked, copying it into an install session")
        // Copying can take seconds: off the main thread.
        Thread {
            try {
                actions.install(contentResolver.openInputStream(uri) ?: error("cannot open the picked file"), "picked file")
            } catch (t: Throwable) {
                AppLog.error("install", t)
            }
        }.start()
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode != REQ_SMS) return
        val number = pendingSmsNumber
        if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED && number != null) {
            actions.sendTestSms(number, getString(R.string.sms_test_text))
        } else {
            AppLog.log("SEND_SMS was not granted")
        }
    }

    private fun sendSms(number: String) {
        if (number.isEmpty()) {
            AppLog.log("sms: type a number first")
        } else if (checkSelfPermission(android.Manifest.permission.SEND_SMS) == PackageManager.PERMISSION_GRANTED) {
            actions.sendTestSms(number, getString(R.string.sms_test_text))
        } else {
            pendingSmsNumber = number
            requestPermissions(arrayOf(android.Manifest.permission.SEND_SMS), REQ_SMS)
        }
    }

    private fun remoteHelp() {
        // The timestamp the log puts in front of this line is what to count by hand.
        AppLog.log("remote help button tapped")
        val launch = packageManager.getLaunchIntentForPackage(RUSTDESK)
        if (launch == null) {
            AppLog.log("remote help: $RUSTDESK is not installed")
            return
        }
        // Remote help is PDM's own tool: the watch must not keep it suspended.
        actions.approve(RUSTDESK)
        try {
            startActivity(launch)
            AppLog.log("remote help: RustDesk started")
        } catch (t: Throwable) {
            AppLog.error("start RustDesk", t)
        }
    }

    @Suppress("DEPRECATION") // unsafeCheckOpNoThrow is the call that exists on API 29 up to 36
    private fun usageGranted(): Boolean = try {
        val ops = getSystemService(AppOpsManager::class.java)
        ops.unsafeCheckOpNoThrow(AppOpsManager.OPSTR_GET_USAGE_STATS, Process.myUid(), packageName) == AppOpsManager.MODE_ALLOWED
    } catch (t: Throwable) {
        AppLog.error("usage access check", t)
        false
    }

    private fun listUsage() {
        try {
            if (!usageGranted()) {
                AppLog.log("usage access is not granted, open the settings first")
                return
            }
            val start = LocalDate.now().atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
            val stats = getSystemService(UsageStatsManager::class.java)
                .queryAndAggregateUsageStats(start, System.currentTimeMillis())
            val top = topForeground(stats.mapValues { it.value.totalTimeInForeground }, 15)
            AppLog.log("foreground time today, ${top.size} of ${stats.size} packages:")
            top.forEach { (pkg, ms) -> AppLog.log("  ${DateUtils.formatElapsedTime(ms / 1000)}  $pkg") }
        } catch (t: Throwable) {
            AppLog.error("usage list", t)
        }
    }

    private fun refreshLog() {
        logView.text = AppLog.text()
        logScroll.post { logScroll.fullScroll(View.FOCUS_DOWN) }
    }

    private fun pkg() = packageField.text.toString().trim()

    private fun section(title: Int) {
        column.addView(TextView(this).apply {
            setText(title)
            setTypeface(typeface, Typeface.BOLD)
            setPadding(0, dp(16), 0, dp(4))
        })
    }

    private fun button(label: Int, onClick: () -> Unit) {
        column.addView(makeButton(label, onClick), LinearLayout.LayoutParams(MATCH, ViewGroup.LayoutParams.WRAP_CONTENT))
    }

    private fun row(vararg buttons: Pair<Int, () -> Unit>) {
        column.addView(LinearLayout(this).apply {
            for ((label, onClick) in buttons) {
                addView(makeButton(label, onClick), LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
            }
        })
    }

    private fun makeButton(label: Int, onClick: () -> Unit) = Button(this).apply {
        setText(label)
        setOnClickListener { onClick() }
    }

    private fun field(hintRes: Int, initial: String) = EditText(this).apply {
        setHint(hintRes)
        setText(initial)
        inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS
        column.addView(this, LinearLayout.LayoutParams(MATCH, ViewGroup.LayoutParams.WRAP_CONTENT))
    }

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()

    private companion object {
        const val MATCH = ViewGroup.LayoutParams.MATCH_PARENT
        const val REQ_APK = 1
        const val REQ_SMS = 2
    }
}
