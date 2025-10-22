package com.nlco.mobile.util

import okhttp3.Cookie
import okhttp3.CookieJar
import okhttp3.HttpUrl

class SessionCookieJar(
    private val storage: SessionStorage,
) : CookieJar {
    override fun loadForRequest(url: HttpUrl): List<Cookie> {
        return storage.load().mapNotNull { raw -> Cookie.parse(url, raw) }
    }

    override fun saveFromResponse(url: HttpUrl, cookies: List<Cookie>) {
        if (cookies.isEmpty()) return
        val serialized = cookies.map { it.toString() }.toSet()
        storage.save(serialized)
    }

    fun clear() {
        storage.clear()
    }
}
