package com.mhc_works.pdm.devicetest

import android.app.admin.DeviceAdminService

/** Bound by the system while this app is Device Owner: keeps the process, and with it the runtime PACKAGE_ADDED receiver of App, alive. */
class WatchService : DeviceAdminService()
