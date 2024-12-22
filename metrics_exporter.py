from clickhouse_driver import Client
from flask import Flask, Response, request

# Инициализация ClickHouse-клиента и Flask-приложения
client = Client(host='localhost', port=9000, database='monitoring')
app = Flask(__name__)

@app.route('/metrics')
def metrics():
    # Получение параметров временного интервала и фильтров
    hours = request.args.get("hours", default=1, type=int)
    region_filter = request.args.get("region", default=None, type=str)
    device_filter = request.args.get("device", default=None, type=str)
    
    # Фильтрация по региону и устройству
    where_clauses = [f"interval >= now() - INTERVAL {hours} HOUR"]
    if region_filter:
        where_clauses.append(f"region = '{region_filter}'")
    if device_filter:
        where_clauses.append(f"device_type = '{device_filter}'")
    
    where_clause = " AND ".join(where_clauses)

    # Основной запрос к ClickHouse
    query = f"""
    SELECT
        region,
        device_type,
        AVG(avg_delay) AS avg_start_delay,
        SUM(total_rebuffers) AS total_rebuffers,
        AVG(avg_stall_duration) AS avg_stall_duration,
        AVG(avg_bitrate) AS avg_bitrate,
        AVG(avg_cdn_response) AS avg_cdn_response,
        SUM(total_streams) AS total_streams
    FROM hourly_metrics
    WHERE {where_clause}
    GROUP BY region, device_type
    """
    results = client.execute(query)

    # Форматирование данных для Prometheus
    metrics_data = [
        f"# HELP avg_start_delay Среднее время старта воспроизведения",
        f"# HELP total_rebuffers Общее количество ребуферингов",
        f"# HELP avg_stall_duration Средняя длительность пауз",
        f"# HELP avg_bitrate Средний битрейт воспроизведения",
        f"# HELP avg_cdn_response Среднее время отклика CDN",
        f"# HELP total_streams Общее количество потоков"
    ]

    for row in results:
        region, device_type, avg_start_delay, total_rebuffers, avg_stall_duration, avg_bitrate, avg_cdn_response, total_streams = row
        metrics_data.append(f'avg_start_delay{{region="{region}",device_type="{device_type}"}} {avg_start_delay:.2f}')
        metrics_data.append(f'total_rebuffers{{region="{region}",device_type="{device_type}"}} {total_rebuffers}')
        metrics_data.append(f'avg_stall_duration{{region="{region}",device_type="{device_type}"}} {avg_stall_duration:.2f}')
        metrics_data.append(f'avg_bitrate{{region="{region}",device_type="{device_type}"}} {avg_bitrate:.2f}')
        metrics_data.append(f'avg_cdn_response{{region="{region}",device_type="{device_type}"}} {avg_cdn_response:.2f}')
        metrics_data.append(f'total_streams{{region="{region}",device_type="{device_type}"}} {total_streams}')

    return Response("\n".join(metrics_data), content_type="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
