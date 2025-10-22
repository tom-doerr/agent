package com.nlco.mobile.util

import okhttp3.HttpUrl.Companion.toHttpUrl
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SessionCookieJarTest {

    @Test
    fun `cookies round trip through storage`() {
        val storage = InMemorySessionStorage()
        val jar = SessionCookieJar(storage)
        val url = "https://example.com".toHttpUrl()

        jar.saveFromResponse(url, listOf(okhttp3.Cookie.Builder().domain("example.com").path("/").name("nlco").value("abc").build()))

        val loaded = jar.loadForRequest(url)
        assertEquals(1, loaded.size)
        assertEquals("nlco", loaded.first().name)
        val persisted = storage.load().first()
        assertTrue(persisted.contains("nlco=abc"))
    }

    @Test
    fun `clear removes stored cookies`() {
        val storage = InMemorySessionStorage()
        val jar = SessionCookieJar(storage)
        val url = "https://example.com".toHttpUrl()
        jar.saveFromResponse(url, listOf(okhttp3.Cookie.Builder().domain("example.com").path("/").name("nlco").value("abc").build()))
        jar.clear()
        assertTrue(jar.loadForRequest(url).isEmpty())
    }
}
