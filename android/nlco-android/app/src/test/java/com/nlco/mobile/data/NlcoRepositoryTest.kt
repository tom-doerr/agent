package com.nlco.mobile.data

import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import com.nlco.mobile.network.NlcoApiService
import com.nlco.mobile.util.InMemorySessionStorage
import com.nlco.mobile.util.SessionCookieJar
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.create

@OptIn(ExperimentalCoroutinesApi::class)
class NlcoRepositoryTest {

    private lateinit var server: MockWebServer
    private lateinit var repository: NlcoRepository
    private lateinit var cookieJar: SessionCookieJar

    @Before
    fun setUp() {
        server = MockWebServer()
        val storage = InMemorySessionStorage()
        cookieJar = SessionCookieJar(storage)
        val json = Json { ignoreUnknownKeys = true }
        val client = OkHttpClient.Builder()
            .cookieJar(cookieJar)
            .build()
        val retrofit = Retrofit.Builder()
            .baseUrl(server.url("/"))
            .client(client)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
        val api = retrofit.create<NlcoApiService>()
        repository = NlcoRepository(api, cookieJar)
    }

    @After
    fun tearDown() {
        server.shutdown()
    }

    @Test
    fun `login stores session cookie`() = runTest {
        server.enqueue(MockResponse().setResponseCode(204).addHeader("Set-Cookie", "nlco=token; Path=/"))
        repository.login("user@example.com", "secret")
        val cookies = cookieJar.loadForRequest(server.url("/api/v1/status"))
        assertTrue(cookies.isNotEmpty())
        assertEquals("nlco", cookies.first().name)
    }

    @Test
    fun `fetchStatus parses payload`() = runTest {
        server.enqueue(MockResponse().setResponseCode(204).addHeader("Set-Cookie", "nlco=token; Path=/"))
        repository.login("user@example.com", "secret")

        val body = """
            {
              "artifact": {"text": "Artifact", "last_updated": "2025-10-05T20:00:00", "age_label": "1m ago"},
              "memory": {"text": "Memory", "last_updated": null, "age_label": "never"},
              "short_term_memory": {"text": "Short", "last_updated": "2025-10-05T19:59:00", "age_label": "2m ago"},
              "history": [
                {"date": "2025-10-05", "entries": ["2000 start"]}
              ]
            }
        """.trimIndent()
        server.enqueue(MockResponse().setBody(body))

        val snapshot = repository.fetchStatus()
        assertEquals("Artifact", snapshot.artifact.text)
        assertEquals("Memory", snapshot.memory.text)
        assertEquals("Short", snapshot.shortTermMemory?.text)
        assertEquals(1, snapshot.history.size)
        assertEquals("2000 start", snapshot.history.first().entries.first())
    }

    @Test
    fun `submitConstraint sends payload`() = runTest {
        server.enqueue(MockResponse().setResponseCode(204).addHeader("Set-Cookie", "nlco=token; Path=/"))
        repository.login("user@example.com", "secret")

        val responseBody = """
            {
              "artifact": {"text": "Artifact", "last_updated": null, "age_label": "just now"},
              "memory": {"text": "Memory", "last_updated": null, "age_label": "never"},
              "short_term_memory": null,
              "history": [
                {"date": "2025-10-05", "entries": ["2130 android"]}
              ]
            }
        """.trimIndent()
        server.enqueue(MockResponse().setBody(responseBody))

        val status = repository.submitConstraint("android")
        val request = server.takeRequest()
        assertEquals("auth/jwt/login", request.path?.substring(1))
        val postRequest = server.takeRequest()
        assertEquals("/api/v1/messages", postRequest.path)
        assertTrue(postRequest.body.readUtf8().contains("android"))
        assertEquals("2130 android", status.history.first().entries.first())
    }
}
