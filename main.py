"""Выявление аномалий и очистка ряда забойного давления скважины (вариант А)."""

Z_THRESHOLD = 2  # пороговый коэффициент k для статистического правила k * sigma


def generate_pressure_series(student_n: int) -> tuple[list[float], float, float]:
    """Формирует 12-часовой ряд давления P (атм) и возвращает (ряд, P_min, P_max)."""
    p_base = 160.0 + 2.0 * student_n
    step = float((student_n % 4) + 1)
    offsets = [0.0, 1.0, -1.0, -18.0, 2.0, 0.0, -2.0, 1.0, 22.0, -1.0, 1.0, 2.0]
    series: list[float] = []
    for k in offsets:
        series.append(round(p_base + k * step, 2))
    p_min = round(p_base - 10.0 * step, 2)
    p_max = round(p_base + 10.0 * step, 2)
    return series, p_min, p_max


def calc_mean(series: list[float]) -> float:
    """Вычисляет среднее арифметическое числового ряда."""
    if not series:
        raise ValueError("Пустой массив данных")
    total = 0.0
    for val in series:
        total += val
    return total / len(series)


def calc_median(series: list[float]) -> float:
    """Вычисляет медиану ряда без изменения исходного списка."""
    n = len(series)
    if n == 0:
        raise ValueError("Пустой массив данных")
    ordered = sorted(series)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def calc_std(series: list[float], mean_val: float) -> float:
    """Вычисляет стандартное отклонение (СКО, sigma) числового ряда."""
    if not series:
        raise ValueError("Пустой массив данных")
    sq_diff_sum = 0.0
    for val in series:
        sq_diff_sum += (val - mean_val) ** 2
    variance = sq_diff_sum / len(series)
    return variance ** 0.5


def calc_range(series: list[float]) -> tuple[float, float, float]:
    """Возвращает (минимум, максимум, размах вариации) за один проход."""
    if not series:
        raise ValueError("Пустой массив данных")
    lo = hi = series[0]
    for val in series[1:]:
        if val < lo:
            lo = val
        if val > hi:
            hi = val
    return lo, hi, round(hi - lo, 2)


def filter_anomalies(
    series: list[float],
    low_bound: float,
    high_bound: float,
) -> tuple[list[float], list[tuple[int, float]]]:
    """Разделяет ряд на очищенный список и список кортежей аномалий (час, значение)."""
    cleaned: list[float] = []
    anomalies: list[tuple[int, float]] = []
    for hour, val in enumerate(series, start=1):
        if low_bound <= val <= high_bound:
            cleaned.append(val)
        else:
            anomalies.append((hour, val))
    return cleaned, anomalies

def replace_outliers_with_neighbor_avg(series, low, high):
    new=[]
    for i in range(0,len(series)):
        if series[i]<low or series[i]>high:
            new.append((series[i - 1] + series[i + 1]) / 2)
        else:
             new.append(series[i])
    return new


def main() -> None:
    print("ПОИСК АНОМАЛИЙ И ОЧИСТКА РЯДА ЗАБОЙНОГО ДАВЛЕНИЯ (ВАРИАНТ А)")
    print("=" * 68)
    raw_n = input("Введите ваш номер по журналу N: ").strip()
    pressures = [170.0] * 12          # тест: заливание датчика
    tech_min, tech_max = 160.0, 180.0




    # Статистики сырого ("грязного") ряда
    raw_mean = calc_mean(pressures)
    raw_med = calc_median(pressures)
    raw_std = calc_std(pressures, raw_mean)
    raw_min, raw_max, raw_rng = calc_range(pressures)
    z_score = abs(diff) / raw_std if raw_std > 0 else 0.0
    # Статистические границы по правилу k * sigma
    stat_low = round(raw_mean - Z_THRESHOLD * raw_std, 2)
    stat_high = round(raw_mean + Z_THRESHOLD * raw_std, 2)

    print(f"\nИсходный ряд (12 ч): {pressures}")
    print(f"Тех. регламент: [{tech_min:.2f}; {tech_max:.2f}] атм")
    print(f"Границы {Z_THRESHOLD:.1f}*sigma: [{stat_low:.2f}; {stat_high:.2f}] атм")

    print("\nДЕТАЛЬНАЯ ТАБЛИЦА КОНТРОЛЯ ИЗМЕРЕНИЙ")
    print("-" * 68)
    print(f"{'Час':<5}{'P, атм':>10}{'Откл. от ср.':>14}{'Z-оценка':>11}{'Тех. коридор':>15}{'Статус точки':>13}")
    print("-" * 68)
    for hour, val in enumerate(pressures, start=1):
        diff = val - raw_mean
        z_score = abs(diff) / raw_std if raw_std > 0 else 0.0
        in_tech = "ОК" if tech_min <= val <= tech_max else "НАРУШЕН"
        is_outlier = (val < stat_low or val > stat_high) or (in_tech == "НАРУШЕН")
        status = "ВЫБРОС!" if is_outlier else "Норма"
        print(f"{hour:<5}{val:>10.2f}{diff:>+14.2f}{z_score:>11.2f}{in_tech:>15}{status:>13}")

    # Фильтрация ряда по статистическим границам
    cleaned_series, found_anomalies = filter_anomalies(pressures, stat_low, stat_high)

    # Статистики очищенного ряда
    cln_mean = calc_mean(cleaned_series)
    cln_med = calc_median(cleaned_series)
    cln_std = calc_std(cleaned_series, cln_mean)
    _, _, cln_rng = calc_range(cleaned_series)

    print("\nРЕЗУЛЬТАТ ФИЛЬТРАЦИИ АНОМАЛИЙ")
    print("-" * 68)
    print(f"Обнаружено выбросов: {len(found_anomalies)} шт. -> {found_anomalies}")
    print(f"Очищенный ряд ({len(cleaned_series)} ч): {cleaned_series}")

    print("\nСРАВНЕНИЕ СТАТИСТИК ДО И ПОСЛЕ ОЧИСТКИ")
    print("-" * 68)
    print(f"{'Показатель':<28}{'До очистки':>14}{'После очистки':>16}{'Изменение':>10}")
    print("-" * 68)
    print(f"{'Среднее арифметическое, атм':<28}{raw_mean:>14.2f}{cln_mean:>16.2f}{cln_mean - raw_mean:>+10.2f}")
    print(f"{'Медиана ряда, атм':<28}{raw_med:>14.2f}{cln_med:>16.2f}{cln_med - raw_med:>+10.2f}")
    print(f"{'Стандартное отклонение, атм':<28}{raw_std:>14.2f}{cln_std:>16.2f}{cln_std - raw_std:>+10.2f}")
    print(f"{'Размах вариации R, атм':<28}{raw_rng:>14.2f}{cln_rng:>16.2f}{cln_rng - raw_rng:>+10.2f}")

    print("Доля бракованной телеметрии (Процент потерь данных)(упражнение 6)")
    anomaly_rate= len(found_anomalies) / len(pressures) * 100
    if anomaly_rate<=10:
        print("Канал исправен")
    elif 10<anomaly_rate<25:
        print("Требуется калибровка датчика")
    else:
        print("Авария телеметрии")

    
    print("\nИмпутация (замещение) аномалий вместо удаления(упражнение 5)")
    print(replace_outliers_with_neighbor_avg(pressures, tech_min, tech_max))

    print("\nПовторная фильтрация чтобы найти еще аномалии(упржнение 2)")
    print("-" * 68)
    print(f"\nИсходный ряд (11 ч): {cleaned_series}")
    raww_mean = calc_mean(cleaned_series)
    raww_med = calc_median(cleaned_series)
    raww_std = calc_std(cleaned_series, raww_mean)
    raww_min, raww_max, raww_rng = calc_range(cleaned_series)
    statt_low = round(raww_mean - Z_THRESHOLD * raww_std, 2)
    statt_high = round(raww_mean + Z_THRESHOLD * raww_std, 2)
    cleanedd_series, foundd_anomalies = filter_anomalies(cleaned_series, statt_low, statt_high)
    clnn_mean = calc_mean(cleanedd_series)
    clnn_med = calc_median(cleanedd_series)
    clnn_std = calc_std(cleanedd_series, clnn_mean)
    _, _, clnn_rng = calc_range(cleanedd_series)
    print(f"Новые выбросы:{foundd_anomalies}")
    print(f"Новый обновленный список давления(10ч) :{cleanedd_series}")
    print(f"{'Среднее арифметическое, атм':<28}{raww_mean:>14.2f}{clnn_mean:>16.2f}{clnn_mean - raww_mean:>+10.2f}")
    print(f"{'Стандартное отклонение, атм':<28}{raww_std:>14.2f}{clnn_std:>16.2f}{clnn_std - raww_std:>+10.2f}")
if __name__ == "__main__":
    main()
