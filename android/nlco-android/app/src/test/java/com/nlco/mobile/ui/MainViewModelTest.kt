package com.nlco.mobile.ui

import com.nlco.mobile.data.HistoryEntry
import com.nlco.mobile.data.NlcoRepositoryContract
import com.nlco.mobile.data.StatusSnapshot
import com.nlco.mobile.data.TextSnapshot
import kotlinx.coroutines.ExperimentalCoroutinesApi
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.ResponseBody
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import retrofit2.HttpException
import retrofit2.Response

@OptIn(ExperimentalCoroutinesApi::class)
class MainViewModelTest {

    @get:Rule
    val dispatcherRule = MainDispatcherRule()

    private val snapshot = StatusSnapshot(
        artifact = TextSnapshot("Artifact", null, "just now"),
        memory = TextSnapshot("Memory", null, "never"),
        shortTermMemory = null,
        history = listOf(HistoryEntry("2025-10-05", listOf("2100 start"))),
    )

    @Test
    fun `loadInitial success authenticates`() {
        val repository = FakeRepository(snapshot)
        val viewModel = MainViewModel(repository)
        viewModel.loadInitial()
        dispatcherRule.dispatcher.scheduler.advanceUntilIdle()
        val state = viewModel.state.value
        assertTrue(state.isAuthenticated)
        assertEquals("Artifact", state.snapshot?.artifact?.text)
    }

    @Test
    fun `loadInitial unauthorized shows login`() {
        val repository = FakeRepository(snapshot).apply {
            fetchError = unauthorized()
        }
        val viewModel = MainViewModel(repository)
        viewModel.loadInitial()
        dispatcherRule.dispatcher.scheduler.advanceUntilIdle()
        val state = viewModel.state.value
        assertFalse(state.isAuthenticated)
        assertNull(state.snapshot)
    }

    @Test
    fun `login failure surfaces error`() {
        val repository = FakeRepository(snapshot).apply {
            loginError = RuntimeException("Login failed")
        }
        val viewModel = MainViewModel(repository)
        viewModel.login("user@example.com", "badpass")
        dispatcherRule.dispatcher.scheduler.advanceUntilIdle()
        val state = viewModel.state.value
        assertFalse(state.isAuthenticated)
        assertEquals("Login failed", state.errorMessage)
    }

    @Test
    fun `submit blank constraint emits error`() {
        val repository = FakeRepository(snapshot)
        val viewModel = MainViewModel(repository)
        viewModel.submit("   ")
        val state = viewModel.state.value
        assertEquals("Message required", state.errorMessage)
    }

    @Test
    fun `submit success refreshes snapshot`() {
        val repository = FakeRepository(snapshot)
        val viewModel = MainViewModel(repository)
        viewModel.submit("shipped")
        dispatcherRule.dispatcher.scheduler.advanceUntilIdle()
        val state = viewModel.state.value
        assertEquals("2130 shipped", state.snapshot?.history?.first()?.entries?.first())
        assertNull(state.errorMessage)
    }

    @Test
    fun `logout clears state`() {
        val repository = FakeRepository(snapshot)
        val viewModel = MainViewModel(repository)
        viewModel.logout()
        dispatcherRule.dispatcher.scheduler.advanceUntilIdle()
        val state = viewModel.state.value
        assertFalse(state.isAuthenticated)
        assertTrue(repository.logoutCalled)
    }

    private fun unauthorized(): Throwable {
        val response = Response.error<Unit>(
            401,
            ResponseBody.create("application/json".toMediaType(), "{}")
        )
        return HttpException(response)
    }

    private class FakeRepository(initial: StatusSnapshot) : NlcoRepositoryContract {
        var snapshotToReturn: StatusSnapshot = initial
        var fetchError: Throwable? = null
        var submitError: Throwable? = null
        var loginError: Throwable? = null
        var logoutCalled: Boolean = false

        override suspend fun login(email: String, password: String) {
            loginError?.let { throw it }
        }

        override suspend fun logout() {
            logoutCalled = true
        }

        override suspend fun fetchStatus(): StatusSnapshot {
            fetchError?.let { throw it }
            return snapshotToReturn
        }

        override suspend fun submitConstraint(message: String): StatusSnapshot {
            submitError?.let { throw it }
            snapshotToReturn = snapshotToReturn.copy(
                history = listOf(HistoryEntry("2025-10-05", listOf("2130 $message")))
            )
            return snapshotToReturn
        }
    }
}
