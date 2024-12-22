import pandas as pd
from clickhouse_driver import Client
import streamlit as st

# Подключение к ClickHouse
client = Client(host='localhost')

@st.cache_data
def load_data():
    """
    Загрузка данных из ClickHouse.

    Возвращает:
        pd.DataFrame: Данные из таблицы monitoring.logs.
    """
    query = """
    SELECT * FROM monitoring.logs
    """
    data = client.execute(query, with_column_types=True)
    df = pd.DataFrame(data[0], columns=[col[0] for col in data[1]])
    
    # Преобразование timestamp в datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df
