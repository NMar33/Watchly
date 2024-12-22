CREATE TABLE logs (
    timestamp DateTime,
    user_id String,
    region String,
    device_type String,
    content_id String,
    initial_playback_delay_ms Int32,
    rebuffer_count Int32,
    total_stall_duration_ms Int32,
    average_bitrate_kbps Int32,
    cdn_response_time_ms Int32,
    segment_download_time_ms Array(Int32),
    final_resolution String,
    vod_duration_s Int32,
    vod_variant_name String,
    vod_bitrate Int32,
    vod_audio_codec String,
    vod_video_codec String,
    vod_width Int32,
    vod_height Int32,
    vod_seek Bool,
    vod_error Nullable(String)
) ENGINE = MergeTree()
ORDER BY timestamp;