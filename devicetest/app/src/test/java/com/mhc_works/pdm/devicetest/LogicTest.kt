package com.mhc_works.pdm.devicetest

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class LogicTest {
    private val own = "com.example.own"

    @Test
    fun parseApprovedTrimsAndSkipsBlankAndComments() {
        val text = "  com.example.a \n\n# note\ncom.example.b\r\ncom.example.a\n"
        assertEquals(setOf("com.example.a", "com.example.b"), parseApproved(text))
    }

    @Test
    fun parseApprovedOfEmptyTextIsEmpty() {
        assertTrue(parseApproved("").isEmpty())
    }

    @Test
    fun approvedWithAddsOnlyMissingPackages() {
        assertEquals("com.example.a\ncom.example.b", approvedWith("com.example.a\n", listOf("com.example.a", "com.example.b", "com.example.b")))
        assertEquals("com.example.a", approvedWith("", listOf("com.example.a")))
    }

    @Test
    fun newUnapprovedAppIsSuspended() {
        assertTrue(shouldSuspend("com.example.new", setOf("com.example.a"), own, isSystemApp = false))
    }

    @Test
    fun approvedAppIsNotSuspended() {
        assertFalse(shouldSuspend("com.example.a", setOf("com.example.a"), own, isSystemApp = false))
    }

    @Test
    fun ownPackageIsNeverSuspended() {
        assertFalse(shouldSuspend(own, emptySet(), own, isSystemApp = false))
    }

    @Test
    fun systemAppIsNeverSuspended() {
        assertFalse(shouldSuspend("com.example.sys", emptySet(), own, isSystemApp = true))
    }

    @Test
    fun pinVerifiesOnlyTheRightPin() {
        val salt = byteArrayOf(1, 2, 3)
        val hash = hashPin(salt, "1234")
        assertTrue(verifyPin(salt, hash, "1234"))
        assertFalse(verifyPin(salt, hash, "1235"))
    }

    @Test
    fun topForegroundSortsDropsZeroAndLimits() {
        val input = mapOf("c" to 5L, "a" to 30L, "b" to 30L, "z" to 0L, "d" to 1L)
        assertEquals(listOf("a" to 30L, "b" to 30L, "c" to 5L), topForeground(input, 3))
        assertEquals(4, topForeground(input, 15).size)
    }
}
