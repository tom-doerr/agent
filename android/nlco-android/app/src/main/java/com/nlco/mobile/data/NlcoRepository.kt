package com.nlco.mobile.data

import com.nlco.mobile.network.HistoryEntryDto
import com.nlco.mobile.network.MessageRequestDto
import com.nlco.mobile.network.NlcoApiService
import com.nlco.mobile.network.StatusResponseDto
import com.nlco.mobile.network.TextSnapshotDto
import com.nlco.mobile.util.SessionCookieJar
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.HttpUrl
import retrofit2.HttpException

data class TextSnapshot(
    val text: String,
    val lastUpdatedIso: String?,
    val ageLabel: String,
)

data class HistoryEntry(
    val date: String,
    val entries: List<String>,
)

data class StatusSnapshot(
    val artifact: TextSnapshot,
    val memory: TextSnapshot,
    val shortTermMemory: TextSnapshot?,
    val history: List<HistoryEntry>,
)

interface NlcoRepositoryContract {
    suspend fun login(email: String, password: String)
    suspend fun logout()
    suspend fun fetchStatus(): StatusSnapshot
    suspend fun submitConstraint(message: String): StatusSnapshot
}

class NlcoRepository(
    private val api: NlcoApiService,
    private val cookieJar: SessionCookieJar,
) : NlcoRepositoryContract {
    override suspend fun login(email: String, password: String) {
        val response = withContext(Dispatchers.IO) {
            api.login(email, password)
        }
        if (!response.isSuccessful) {
            throw HttpException(response)
        }
    }

    override suspend fun logout() {
        withContext(Dispatchers.IO) {
            api.logout()
        }
        cookieJar.clear()
    }

    override suspend fun fetchStatus(): StatusSnapshot = withContext(Dispatchers.IO) {
        api.getStatus().toDomain()
    }

    override suspend fun submitConstraint(message: String): StatusSnapshot = withContext(Dispatchers.IO) {
        api.postMessage(MessageRequestDto(message)).toDomain()
    }

    fun hasSessionFor(host: HttpUrl): Boolean {
        return cookieJar.loadForRequest(host).isNotEmpty()
    }

    private fun StatusResponseDto.toDomain(): StatusSnapshot {
        return StatusSnapshot(
            artifact = artifact.toDomain(),
            memory = memory.toDomain(),
            shortTermMemory = shortTermMemory?.toDomain(),
            history = history.map { it.toDomain() },
        )
    }

    private fun TextSnapshotDto.toDomain(): TextSnapshot {
        return TextSnapshot(
            text = text,
            lastUpdatedIso = lastUpdated,
            ageLabel = ageLabel,
        )
    }

    private fun HistoryEntryDto.toDomain(): HistoryEntry {
        return HistoryEntry(date = date, entries = entries)
    }
}
