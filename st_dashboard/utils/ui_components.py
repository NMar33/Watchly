
import streamlit as st
import plotly.express as px
import pandas as pd

def display_summary_statistics(df):
    """Отображение общей статистики данных."""
    st.header("Общая статистика")
    st.write(f"Общее количество записей: **{len(df):,}**")
    st.write(f"Уникальные пользователи: **{df['user_id'].nunique():,}**")
    st.write(f"Уникальные регионы: **{df['region'].nunique():,}**")
    st.write(f"Диапазон дат: **{df['timestamp'].min()}** — **{df['timestamp'].max()}**")

def apply_filters(df):
    """Применение фильтров для данных."""
    st.sidebar.title("⚙️ Фильтры")
    region_filter = st.sidebar.multiselect("Выберите регионы", df['region'].unique(), default=df['region'].unique())
    device_filter = st.sidebar.multiselect("Выберите устройства", df['device_type'].unique(), default=df['device_type'].unique())
    date_range = st.sidebar.date_input("Выберите диапазон дат", [df['timestamp'].min(), df['timestamp'].max()])

    filtered_df = df[
        (df['region'].isin(region_filter)) &
        (df['device_type'].isin(device_filter)) &
        (df['timestamp'].dt.date.between(date_range[0], date_range[1]))
    ]
    st.sidebar.write(f"🔍 Найдено записей: {len(filtered_df):,}")
    return filtered_df

def render_region_analysis(filtered_df):
    """Анализ распределения записей по регионам."""
    st.header("Анализ регионов")
    region_counts = filtered_df['region'].value_counts()
    fig_region = px.bar(region_counts, x=region_counts.index, y=region_counts.values,
                        labels={'x': 'Регион', 'y': 'Количество записей'},
                        title="Распределение записей по регионам")
    st.plotly_chart(fig_region)

def render_qoe_metrics(filtered_df):
    """Отображение ключевых метрик QoE."""
    st.header("Метрики QoE (Качество опыта)")
    qoe_metrics = {
        "Средняя задержка воспроизведения (мс)": filtered_df['initial_playback_delay_ms'].mean(),
        "Среднее количество рибуферов": filtered_df['rebuffer_count'].mean(),
        "Общее время остановок (мс)": filtered_df['total_stall_duration_ms'].mean(),
        "Средний битрейт (Кбит/с)": filtered_df['average_bitrate_kbps'].mean(),
    }
    for metric, value in qoe_metrics.items():
        st.write(f"**{metric}:** {value:.2f}")

def render_playback_delay_histogram(filtered_df):
    """Гистограмма задержки воспроизведения."""
    st.subheader("Распределение задержки воспроизведения")
    fig_delay = px.histogram(filtered_df, x='initial_playback_delay_ms', nbins=30,
                             title="Гистограмма задержки воспроизведения (мс)",
                             labels={'initial_playback_delay_ms': 'Задержка воспроизведения (мс)'})
    st.plotly_chart(fig_delay)

def render_time_series_analysis(filtered_df, time_group):
    """Временные ряды анализа пользовательского опыта."""
    time_metrics = filtered_df.groupby('time_group').agg({
        'initial_playback_delay_ms': 'mean',
        'rebuffer_count': 'mean',
        'average_bitrate_kbps': 'mean'
    }).reset_index()

    st.subheader("Средняя задержка воспроизведения (мс) во времени")
    fig_delay_time = px.line(time_metrics, x='time_group', y='initial_playback_delay_ms',
                             title="Средняя задержка воспроизведения во времени",
                             labels={'time_group': 'Время', 'initial_playback_delay_ms': 'Задержка (мс)'})
    st.plotly_chart(fig_delay_time)

    st.subheader("Среднее количество рибуферов во времени")
    fig_rebuffer_time = px.line(time_metrics, x='time_group', y='rebuffer_count',
                                title="Среднее количество рибуферов во времени",
                                labels={'time_group': 'Время', 'rebuffer_count': 'Рибуферы'})
    st.plotly_chart(fig_rebuffer_time)

    st.subheader("Средний битрейт (Кбит/с) во времени")
    fig_bitrate_time = px.line(time_metrics, x='time_group', y='average_bitrate_kbps',
                               title="Средний битрейт во времени",
                               labels={'time_group': 'Время', 'average_bitrate_kbps': 'Битрейт (Кбит/с)'})
    st.plotly_chart(fig_bitrate_time)

def render_comparison_chart(time_metrics, metrics_to_compare):
    """Сравнение метрик во времени."""
    st.header("📊 Сравнение метрик во времени")
    if metrics_to_compare:
        fig_compare = px.line(
            time_metrics,
            x='time_group',
            y=metrics_to_compare,
            title="Сравнение метрик во времени",
            labels={'time_group': 'Время', 'value': 'Значение', 'variable': 'Метрика'},
            markers=True
        )
        fig_compare.update_traces(mode="lines+markers")
        st.plotly_chart(fig_compare)
    else:
        st.warning("Выберите хотя бы одну метрику для сравнения.")

def format_ranges(thresholds, reverse=False):
    if reverse:
        return f"< {thresholds['good']}", f"{thresholds['good']}–{thresholds['average']}", f"{thresholds['average']}–{thresholds['bad']}", f"> {thresholds['bad']}"
    else:
        return f"> {thresholds['good']}", f"{thresholds['average']}–{thresholds['good']}", f"{thresholds['bad']}–{thresholds['average']}", f"< {thresholds['bad']}"

def display_settings_tables(settings, params_translation):
    """Отображение текущих настроек в виде группированных таблиц."""
    st.write("### Текущие настройки")

    # Отображение настроек по устройствам
    st.subheader("По устройствам:")
    for device, params in settings["device"].items():
        st.markdown(f"#### **{device}**")
        device_data = []
        for param, thresholds in params.items():
            device_data.append(
                [params_translation[param], *format_ranges(thresholds, reverse=(param != "average_bitrate_kbps"))]
            )
        device_df = pd.DataFrame(
            device_data, columns=["Параметр", "Хорошо", "Средне", "Плохо", "Критично"]
        )
        st.table(device_df)

    # Отображение настроек по продолжительности контента
    st.subheader("По продолжительности:")
    for duration, params in settings["duration"].items():
        st.markdown(f"#### **{duration.capitalize()}**")
        duration_data = []
        for param, thresholds in params.items():
            duration_data.append(
                [params_translation[param], *format_ranges(thresholds, reverse=(param != "average_bitrate_kbps"))]
            )
        duration_df = pd.DataFrame(
            duration_data, columns=["Параметр", "Хорошо", "Средне", "Плохо", "Критично"]
        )
        st.table(duration_df)


def display_settings_editor(settings, params_translation, tab_name):
    """Редактирование настроек через Streamlit с использованием формы."""
    st.header(f"Настройки {tab_name}")
    for category, params in settings[tab_name].items():
        with st.expander(f"{tab_name.capitalize()}: {category}"):
            # Создаем форму для текущей категории
            with st.form(key=f"{tab_name}_{category}_form"):
                for param, thresholds in params.items():
                    STEP = 100 if param != "rebuffer_count" else 1
                    st.write(f"**{params_translation[param]}**:")
                    col1, col2, col3 = st.columns(3)
                    thresholds["good"] = col1.number_input(
                        "Хорошо", value=thresholds["good"], step=STEP, key=f"{category}_{param}_good"
                    )
                    thresholds["average"] = col2.number_input(
                        "Средне", value=thresholds["average"], step=STEP, key=f"{category}_{param}_average"
                    )
                    thresholds["bad"] = col3.number_input(
                        "Плохо", value=thresholds["bad"], step=STEP, key=f"{category}_{param}_bad"
                    )
                # Добавляем кнопку подтверждения в форму
                submitted = st.form_submit_button("Сохранить изменения")
                if submitted:
                    st.success(f"Настройки для {category} сохранены.")
