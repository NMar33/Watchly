from clickhouse_driver import Client
import json
from datetime import datetime

LOGS_PATH = "data/raw/logs.json"

# Подключение к ClickHouse
client = Client(host='localhost')

# Загрузка JSON-файла
with open(LOGS_PATH, 'r') as file:
    logs = json.load(file)

# Подготовка данных для вставки
rows = [
    (
        datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")),
        log["user_id"],
        log["region"],
        log["device_type"],
        log["content_id"],
        log["initial_playback_delay_ms"],
        log["rebuffer_count"],
        log["total_stall_duration_ms"],
        log["average_bitrate_kbps"],
        log["cdn_response_time_ms"],
        log["segment_download_time_ms"],
        log["final_resolution"],
        log["vod_duration_s"],
        log["vod_variant_name"],
        log["vod_bitrate"],
        log["vod_audio_codec"],
        log["vod_video_codec"],
        log["vod_width"],
        log["vod_height"],
        log["vod_seek"],
        log["vod_error"],
    )
    for log in logs
]

# Вставка данных
client.execute(
    'INSERT INTO monitoring.logs VALUES',
    rows
)

print("Данные успешно загружены!")

