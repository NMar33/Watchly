CREATE MATERIALIZED VIEW monitoring.hourly_metrics
ENGINE = SummingMergeTree()
ORDER BY interval
POPULATE AS
SELECT
    toStartOfInterval(timestamp, INTERVAL 1 hour) AS interval,
    region,
    device_type,
    AVG(initial_playback_delay_ms) AS avg_delay,
    SUM(rebuffer_count) AS total_rebuffers,
    AVG(total_stall_duration_ms) AS avg_stall_duration,
    AVG(average_bitrate_kbps) AS avg_bitrate,
    AVG(cdn_response_time_ms) AS avg_cdn_response,
    COUNT(*) AS total_streams
FROM monitoring.logs
GROUP BY interval, region, device_type;
