import pandas as pd

# Константы для длины видео 
SHORT_VIDEO_DURATION = 10  # минут
MEDIUM_VIDEO_DURATION = 30  # минут

def evaluate_device_experience(row, device_rules):
    """
    Оценка пользовательского опыта на основе устройства с учётом направления (reverse).
    """
    device = row['device_type']
    metrics = {
        "initial_playback_delay_ms": row['initial_playback_delay_ms'],
        "rebuffer_count": row['rebuffer_count'],
        "average_bitrate_kbps": row['average_bitrate_kbps']
    }
    experience_scores = []
    
    for metric, value in metrics.items():
        thresholds = device_rules[device][metric]
        if thresholds["reverse"]:  # Чем больше значение, тем хуже
            if value <= thresholds['good']:
                experience_scores.append(0)  # Хорошо
            elif value <= thresholds['average']:
                experience_scores.append(1)  # Средне
            elif value <= thresholds['bad']:
                experience_scores.append(2)  # Плохо
            else:
                experience_scores.append(3)  # Критично
        else:  # Чем больше значение, тем лучше
            if value >= thresholds['good']:
                experience_scores.append(0)  # Хорошо
            elif value >= thresholds['average']:
                experience_scores.append(1)  # Средне
            elif value >= thresholds['bad']:
                experience_scores.append(2)  # Плохо
            else:
                experience_scores.append(3)  # Критично

    return max(experience_scores)  # Самое негативное значение

def evaluate_duration_experience(row, duration_rules):
    """
    Оценка пользовательского опыта на основе длины видео с учётом направления (reverse).
    """
    duration_minutes = row['vod_duration_s'] / 60  # переводим секунды в минуты
    if duration_minutes <= SHORT_VIDEO_DURATION:
        category = "short"
    elif duration_minutes <= MEDIUM_VIDEO_DURATION:
        category = "medium"
    else:
        category = "long"

    metrics = {
        "initial_playback_delay_ms": row['initial_playback_delay_ms'],
        "rebuffer_count": row['rebuffer_count'],
        "average_bitrate_kbps": row['average_bitrate_kbps']
    }
    experience_scores = []
    
    for metric, value in metrics.items():
        thresholds = duration_rules[category][metric]
        if thresholds["reverse"]:  # Чем больше значение, тем хуже
            if value <= thresholds['good']:
                experience_scores.append(0)  # Хорошо
            elif value <= thresholds['average']:
                experience_scores.append(1)  # Средне
            elif value <= thresholds['bad']:
                experience_scores.append(2)  # Плохо
            else:
                experience_scores.append(3)  # Критично
        else:  # Чем больше значение, тем лучше
            if value >= thresholds['good']:
                experience_scores.append(0)  # Хорошо
            elif value >= thresholds['average']:
                experience_scores.append(1)  # Средне
            elif value >= thresholds['bad']:
                experience_scores.append(2)  # Плохо
            else:
                experience_scores.append(3)  # Критично

    return max(experience_scores)  # Самое негативное значение


def calculate_weighted_experience(device_exp, duration_exp, memory_coefficient=3):
    """
    Рассчёт итогового пользовательского опыта с учётом коэффициента злопамятности.
    """
    if device_exp == duration_exp:
        k1, k2 = 1, 1
    elif device_exp > duration_exp:
        k1, k2 = memory_coefficient, 1
    else:
        k1, k2 = 1, memory_coefficient

    weighted_experience = (k1 * device_exp + k2 * duration_exp) / (k1 + k2)
    return weighted_experience

def calculate_user_experience(df, device_rules, duration_rules, memory_coefficient=3):
    """
    Добавление итогового пользовательского опыта в DataFrame.
    """
    df['device_experience'] = df.apply(evaluate_device_experience, axis=1, args=(device_rules,))
    df['duration_experience'] = df.apply(evaluate_duration_experience, axis=1, args=(duration_rules,))
    df['user_experience'] = df.apply(
        lambda row: calculate_weighted_experience(
            row['device_experience'],
            row['duration_experience'],
            memory_coefficient
        ),
        axis=1
    )
    return df
