package com.nlco.mobile.network

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.FormUrlEncoded
import retrofit2.http.Field
import retrofit2.http.GET
import retrofit2.http.POST

@Serializable
data class TextSnapshotDto(
    val text: String,
    @SerialName("last_updated") val lastUpdated: String? = null,
    @SerialName("age_label") val ageLabel: String,
)

@Serializable
data class HistoryEntryDto(
    val date: String,
    val entries: List<String>,
)

@Serializable
data class StatusResponseDto(
    val artifact: TextSnapshotDto,
    val memory: TextSnapshotDto,
    @SerialName("short_term_memory") val shortTermMemory: TextSnapshotDto? = null,
    val history: List<HistoryEntryDto>,
)

@Serializable
data class MessageRequestDto(
    val message: String,
)

interface NlcoApiService {
    @GET("api/v1/status")
    suspend fun getStatus(): StatusResponseDto

    @POST("api/v1/messages")
    suspend fun postMessage(@Body payload: MessageRequestDto): StatusResponseDto

    @FormUrlEncoded
    @POST("auth/jwt/login")
    suspend fun login(
        @Field("username") email: String,
        @Field("password") password: String,
    ): Response<Unit>

    @POST("auth/jwt/logout")
    suspend fun logout(): Response<Unit>
}
