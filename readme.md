# **Шаг 1: Установка виртуального окружения и зависимостей**

### **1. Создание виртуального окружения**
```bash
python -m venv demo_venv
```

### **2. Активация виртуального окружения**
- Для Linux/MacOS:
  ```bash
  source demo_venv/bin/activate
  ```
- Для Windows:
  ```bash
  demo_venv\\Scripts\\activate
  ```

### **3. Установка зависимостей**
```bash
pip install -r requirements.txt
```

---


# **Шаг 2: Установка и запуск ClickHouse**

### **1. Создание директорий и копирование конфигурации**
```bash
mkdir -p ./clickhouse_data ./clickhouse_logs ./clickhouse_config

cp clickhouse_files/config.xml ./clickhouse_config/
```

### **2. Запуск контейнера ClickHouse**
Для запуска контейнера выполните следующую команду:
```bash
docker run -d \
    --name demo-clickhouse-server \
    --ulimit nofile=262144:262144 \
    -p 9000:9000 \
    -p 8123:8123 \
    -v ./clickhouse_data:/var/lib/clickhouse/ \
    -v ./clickhouse_logs:/var/log/clickhouse-server/ \
    -v ./clickhouse_config/config.xml:/etc/clickhouse-server/config.xml \
    clickhouse
```

### **3. Проверка конфигурации Prometheus**
Убедитесь, что Prometheus включен. Для этого выполните:
```bash
docker exec -it demo-clickhouse-server cat /etc/clickhouse-server/config.xml | grep -A 30 "<prometheus>"
```
Убедитесь, что блок `<prometheus>` раскомментирован.

### **4. Настройка базы данных Monitoring**
Создайте базу данных и настройте необходимые таблицы:
```bash
docker exec -i demo-clickhouse-server clickhouse-client --query "CREATE DATABASE IF NOT EXISTS monitoring;"

docker exec -i demo-clickhouse-server clickhouse-client --database=monitoring --multiquery < clickhouse_files/create_table.sql

python clickhouse_files/upload_logs.py
```

### **5. Подключение к ClickHouse**
Для подключения выполните:
```bash
docker exec -it demo-clickhouse-server clickhouse-client --database=monitoring
```

### **6. Проверка данных**
Запустите следующие запросы, чтобы убедиться в успешной загрузке данных:
```sql
SELECT COUNT(*) FROM logs;
SELECT * FROM logs LIMIT 10;
```

---

## **Шаг 2: Подключение к Docker-сети**

### **1. Создание пользовательской сети**
Для взаимодействия компонентов системы создайте пользовательскую сеть:
```bash
docker network create demo-monitoring-net
```

### **2. Подключение ClickHouse к сети**
Подключите контейнер ClickHouse к созданной сети:
```bash
docker network connect demo-monitoring-net demo-clickhouse-server
```

---

# **Шаг 3: Запуск дашборда на Streamlit**

### **1. Запустите Streamlit**
Для запуска дашборда выполните следующую команду:
```bash
streamlit run st_dashboard/dashboard.py
```

---

## **Технические детали**

### **1. Основные компоненты**
- **Страница EDA**:
  - Фильтры для исследования данных и динамические визуализации.
  - Отображение таких метрик, как задержка воспроизведения, количество буферизаций и средний битрейт.

- **Страница настроек QoE**:
  - Настройка порогов удовлетворенности для различных типов устройств и длительности видео.
  - Реализация формулы взвешенного опыта с использованием коэффициента злопамятности.

### **2. Формула взвешенного опыта**
Формула оценивает пользовательский опыт, комбинируя оценки из двух таблиц (устройство и длительность):

```
Итоговый опыт = (k1 * Опыт устройства + k2 * Опыт длительности) / (k1 + k2)
```
- Коэффициенты (`k1`, `k2`) динамически настраиваются на основе **коэффициента злопамятности**, что позволяет придавать больше значения негативному опыту.

### **3. Модульная кодовая база**
- `data_loader.py`: Загрузка данных из ClickHouse.
- `ui_components.py`: Модульные компоненты для визуализации данных.
- `formulas.py`: Реализация формулы взвешенного опыта.
- `settings_manager.py`: Управление настройками.

---

## **Уникальные особенности**
1. **Динамическая формула QoE**:
   - Коэффициент злопамятности усиливает влияние негативного опыта на общую оценку.

2. **Инсайты по устройствам и длительности**:
   - Индивидуальные пороги для различных устройств и длительности видео обеспечивают точный анализ.

3. **Интерактивные визуализации**:
   - Анализ пользовательского опыта во времени с опциями почасовой или ежедневной агрегации.

4. **Полная кастомизация**:
   - Все настройки хранятся в одном JSON-файле для удобного обновления и повторного использования.


---

# **Шаг 4: Настройка экспортера и Prometheus**

### **1. Настройка метрик ClickHouse**
Для выполнения SQL-запросов и настройки метрик выполните:
```bash
docker exec -i demo-clickhouse-server clickhouse-client --database=monitoring --multiquery < clickhouse_files/create_hourly_metrics.sql

docker exec -i demo-clickhouse-server clickhouse-client --query "SHOW CREATE TABLE monitoring.hourly_metrics;"
docker exec -i demo-clickhouse-server clickhouse-client --query "DESCRIBE TABLE monitoring.hourly_metrics;"
docker exec -i demo-clickhouse-server clickhouse-client --query "SELECT * FROM monitoring.hourly_metrics LIMIT 10;"
```

### **2. Запустите экспортёр метрик**
Выполните команду для запуска экспортера:
```bash
python metrics_exporter.py
```

### **3. Проверьте доступность API экспортера**
Для проверки доступности API выполните:
```bash
curl -X GET "http://localhost:5000/metrics"
```

### **4. Настройка Prometheus**
Запустите контейнер Prometheus с указанным конфигурационным файлом:
```bash
docker run -d \
    --name demo-prometheus \
    --network demo-monitoring-net \
    -p 9090:9090 \
    -v "$(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml" \
    prom/prometheus
```

Откройте Prometheus в браузере по адресу [http://localhost:9090](http://localhost:9090).


### **5. Проверка интерфейса Prometheus**
После запуска Prometheus выполните следующие команды для проверки:

#### Получение всех активных метрик:
```bash
curl -X GET "http://localhost:9090/api/v1/label/__name__/values"
```

#### Выполнение простого запроса через API:
```bash
curl -X GET "http://localhost:9090/api/v1/query?query=up"
```

---

# **Шаг 5: Установка и настройка Grafana**

---

#### **1. Установка Grafana**

1. Запустите контейнер Grafana:
   ```bash
   docker run -d \
       --name grafana \
       --network monitoring-net \
       -p 3000:3000 \
       grafana/grafana
   ```