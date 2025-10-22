package com.nlco.mobile.app

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import com.nlco.mobile.BuildConfig
import com.nlco.mobile.data.NlcoRepository
import com.nlco.mobile.network.NlcoApiService
import com.nlco.mobile.ui.MainViewModel
import com.nlco.mobile.ui.screens.DashboardScreen
import com.nlco.mobile.ui.screens.LoginScreen
import com.nlco.mobile.util.SessionCookieJar
import com.nlco.mobile.util.SharedPreferencesSessionStorage
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.create

class MainActivity : ComponentActivity() {

    private val repository by lazy { createRepository() }

    private val viewModel: MainViewModel by viewModels {
        viewModelFactory {
            initializer { MainViewModel(repository) }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            NLCOTheme {
                val state by viewModel.state.collectAsStateWithLifecycle()
                LaunchedEffect(Unit) {
                    viewModel.loadInitial()
                }
                if (state.isAuthenticated) {
                    DashboardScreen(
                        state = state,
                        onRefresh = { viewModel.refresh() },
                        onSubmit = { message -> viewModel.submit(message) },
                        onLogout = { viewModel.logout() },
                        onErrorConsumed = { viewModel.setErrorHandled() },
                        modifier = Modifier,
                    )
                } else {
                    LoginScreen(
                        state = state,
                        onSubmit = { email, password -> viewModel.login(email, password) },
                        onErrorConsumed = { viewModel.setErrorHandled() },
                        modifier = Modifier,
                    )
                }
            }
        }
    }

    private fun createRepository(): NlcoRepository {
        val json = Json {
            ignoreUnknownKeys = true
            coerceInputValues = true
        }
        val contentType = "application/json".toMediaType()
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }
        val sessionStorage = SharedPreferencesSessionStorage(
            preferences = getSharedPreferences("nlco_session", Context.MODE_PRIVATE)
        )
        val cookieJar = SessionCookieJar(sessionStorage)
        val client = OkHttpClient.Builder()
            .cookieJar(cookieJar)
            .addInterceptor(logging)
            .build()
        val retrofit = Retrofit.Builder()
            .baseUrl(BuildConfig.NLCO_BASE_URL)
            .client(client)
            .addConverterFactory(json.asConverterFactory(contentType))
            .build()
        val api = retrofit.create<NlcoApiService>()
        return NlcoRepository(api, cookieJar)
    }
}

private val LightColors = lightColorScheme()
private val DarkColors = darkColorScheme()

@Composable
fun NLCOTheme(content: @Composable () -> Unit) {
    val colors = if (isSystemInDarkTheme()) DarkColors else LightColors
    MaterialTheme(
        colorScheme = colors,
        typography = MaterialTheme.typography,
        content = content,
    )
}
