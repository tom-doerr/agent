package com.nlco.mobile.util

import android.content.SharedPreferences

interface SessionStorage {
    fun load(): Set<String>
    fun save(cookies: Set<String>)
    fun clear()
}

class SharedPreferencesSessionStorage(
    private val preferences: SharedPreferences,
    private val key: String = DEFAULT_KEY,
) : SessionStorage {
    override fun load(): Set<String> = preferences.getStringSet(key, emptySet()) ?: emptySet()

    override fun save(cookies: Set<String>) {
        preferences.edit().putStringSet(key, cookies.toSet()).apply()
    }

    override fun clear() {
        preferences.edit().remove(key).apply()
    }

    private companion object {
        private const val DEFAULT_KEY = "nlco_session_cookies"
    }
}

class InMemorySessionStorage : SessionStorage {
    private var cookies: Set<String> = emptySet()

    override fun load(): Set<String> = cookies

    override fun save(cookies: Set<String>) {
        this.cookies = cookies.toSet()
    }

    override fun clear() {
        cookies = emptySet()
    }
}
