from datetime import datetime, timedelta, timezone

# Получаем текущее время в UTC (лучшая практика для бэкенда)
now = datetime.now(timezone.utc)

# Прибавляем 3 дня
trial_expires_at = now + timedelta(days=3)