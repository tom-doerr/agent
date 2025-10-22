package com.nlco.mobile.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nlco.mobile.data.NlcoRepositoryContract
import com.nlco.mobile.data.StatusSnapshot
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException

private const val ERROR_UNAUTHORIZED = "unauthorized"

sealed interface UiEvent {
    data object LoggedOut : UiEvent
}

data class UiState(
    val isAuthenticated: Boolean = false,
    val isLoading: Boolean = false,
    val snapshot: StatusSnapshot? = null,
    val errorMessage: String? = null,
)

class MainViewModel(
    private val repository: NlcoRepositoryContract,
) : ViewModel() {

    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadInitial() {
        if (_state.value.isLoading) return
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, errorMessage = null) }
            try {
                val snapshot = repository.fetchStatus()
                _state.value = UiState(
                    isAuthenticated = true,
                    isLoading = false,
                    snapshot = snapshot,
                    errorMessage = null,
                )
            } catch (http: HttpException) {
                if (http.code() == 401) {
                    _state.value = UiState(isAuthenticated = false, isLoading = false)
                } else {
                    _state.update { it.copy(isLoading = false, errorMessage = http.message()) }
                }
            } catch (t: Throwable) {
                _state.update { it.copy(isLoading = false, errorMessage = t.message ?: ERROR_UNAUTHORIZED) }
            }
        }
    }

    fun login(email: String, password: String) {
        if (email.isBlank() || password.isBlank()) {
            _state.update { it.copy(errorMessage = "Email and password required") }
            return
        }
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, errorMessage = null) }
            try {
                repository.login(email.trim(), password)
                val snapshot = repository.fetchStatus()
                _state.value = UiState(
                    isAuthenticated = true,
                    isLoading = false,
                    snapshot = snapshot,
                )
            } catch (t: Throwable) {
                val message = (t as? HttpException)?.message() ?: t.message ?: "Login failed"
                _state.update { it.copy(isLoading = false, errorMessage = message) }
            }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, errorMessage = null) }
            try {
                val snapshot = repository.fetchStatus()
                _state.update { it.copy(isLoading = false, snapshot = snapshot, isAuthenticated = true) }
            } catch (t: Throwable) {
                if (t is HttpException && t.code() == 401) {
                    _state.value = UiState(isAuthenticated = false, isLoading = false)
                } else {
                    _state.update { it.copy(isLoading = false, errorMessage = t.message ?: "Refresh failed") }
                }
            }
        }
    }

    fun submit(message: String) {
        val trimmed = message.trim()
        if (trimmed.isEmpty()) {
            _state.update { it.copy(errorMessage = "Message required") }
            return
        }
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, errorMessage = null) }
            try {
                val snapshot = repository.submitConstraint(trimmed)
                _state.update { it.copy(isLoading = false, snapshot = snapshot, isAuthenticated = true) }
            } catch (t: Throwable) {
                val messageText = (t as? HttpException)?.message() ?: t.message ?: "Submit failed"
                _state.update { it.copy(isLoading = false, errorMessage = messageText) }
            }
        }
    }

    fun setErrorHandled() {
        _state.update { it.copy(errorMessage = null) }
    }

    fun logout() {
        viewModelScope.launch {
            try {
                repository.logout()
            } catch (_: Throwable) {
                // Ignore logout errors; the cookie is cleared locally.
            }
            _state.value = UiState(isAuthenticated = false)
        }
    }
}
