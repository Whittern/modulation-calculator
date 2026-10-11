from collections import deque
import streamlit as st

# =====================================================================
# --- БАЗА ДАННЫХ И МУЗЫКАЛЬНАЯ ЛОГИКА (БЕЗ ИЗМЕНЕНИЙ) ---
# =====================================================================

TONALITIES = {
    'C-dur': ('major', 0), 'G-dur': ('major', 1), 'D-dur': ('major', 2), 'A-dur': ('major', 3), 'E-dur': ('major', 4),
    'H-dur': ('major', 5), 'Fis-dur': ('major', 6), 'Cis-dur': ('major', 7),
    'F-dur': ('major', -1), 'B-dur': ('major', -2), 'Es-dur': ('major', -3), 'As-dur': ('major', -4),
    'Des-dur': ('major', -5), 'Ges-dur': ('major', -6), 'Ces-dur': ('major', -7),
    'a-moll': ('minor', 0), 'e-moll': ('minor', 1), 'h-moll': ('minor', 2), 'fis-moll': ('minor', 3),
    'cis-moll': ('minor', 4), 'gis-moll': ('minor', 5), 'dis-moll': ('minor', 6), 'ais-moll': ('minor', 7),
    'd-moll': ('minor', -1), 'g-moll': ('minor', -2), 'c-moll': ('minor', -3), 'f-moll': ('minor', -4),
    'b-moll': ('minor', -5), 'es-moll': ('minor', -6), 'as-moll': ('minor', -7)
}

FIFTHS_ORDER = ['Ces', 'Ges', 'Des', 'As', 'Es', 'B', 'F', 'C', 'G', 'D', 'A', 'E', 'H', 'Fis', 'Cis', 'Gis', 'Dis',
                'Ais']


def get_base_tonic(tonality):
    raw_tonic = tonality.split('-')[0]
    if raw_tonic.lower() == 'b': return 'B'
    if raw_tonic.lower() == 'h': return 'H'
    return raw_tonic[0].upper() + raw_tonic[1:] if len(raw_tonic) > 1 else raw_tonic.upper()


def get_fifth_index(tonality):
    tonic = get_base_tonic(tonality)
    try:
        return FIFTHS_ORDER.index(tonic)
    except ValueError:
        return -1


def get_relatives_exact(ton):
    mode, sharps = TONALITIES[ton]
    relatives = []
    for t, (m, s) in TONALITIES.items():
        if t == ton: continue
        if s == sharps and m != mode:
            relatives.append(t)
        elif s == sharps - 1:
            relatives.append(t)
        elif s == sharps + 1:
            relatives.append(t)

    tonic_name = ton.split('-')[0]
    if mode == 'major':
        s_map = {'C': 'f-moll', 'G': 'c-moll', 'D': 'g-moll', 'A': 'd-moll', 'E': 'a-moll', 'H': 'e-moll',
                 'Fis': 'h-moll', 'F': 'b-moll', 'B': 'es-moll', 'Es': 'as-moll'}
        if tonic_name in s_map: relatives.append(s_map[tonic_name])
    else:
        d_map = {'a': 'E-dur', 'e': 'H-dur', 'h': 'Fis-dur', 'fis': 'Cis-dur', 'cis': 'Gis-dur', 'gis': 'Dis-dur',
                 'd': 'A-dur', 'g': 'D-dur', 'c': 'G-dur', 'f': 'C-dur', 'b': 'F-dur', 'es': 'B-dur', 'as': 'Es-dur'}
        if tonic_name in d_map: relatives.append(d_map[tonic_name])

    return list(set([r for r in relatives if r in TONALITIES]))


def is_valid_sequence(path):
    if len(path) < 3: return True
    for i in range(len(path) - 2):
        t1, t2, t3 = path[i], path[i + 1], path[i + 2]
        idx1, idx2, idx3 = get_fifth_index(t1), get_fifth_index(t2), get_fifth_index(t3)
        if idx1 != -1 and idx2 != -1 and idx3 != -1:
            diff1 = idx2 - idx1
            diff2 = idx3 - idx2
            if (diff1 == 1 and diff2 == 1) or (diff1 == -1 and diff2 == -1):
                return False
    return True


def get_pair_degree(t1, t2):
    if t1.lower().split('-')[0] == t2.lower().split('-')[0]: return 2
    relatives_t1 = set(get_relatives_exact(t1))
    relatives_t2 = set(get_relatives_exact(t2))
    if t2 in relatives_t1: return 1
    if relatives_t1.intersection(relatives_t2): return 2
    return 3


def find_modulation_plans(start, end):
    if start not in TONALITIES or end not in TONALITIES: return "Ошибка: Неверная тональность."
    if start == end: return f"Тональности совпадают."

    if start.split('-')[0].lower() == end.split('-')[0].lower() and TONALITIES[start] != TONALITIES[end]:
        path = [start]
        start_mode, start_signs = TONALITIES[start]
        end_mode, end_signs = TONALITIES[end]
        curr_signs, curr_mode = start_signs, start_mode
        step = 1 if end_signs > start_signs else -1
        while curr_signs != end_signs or curr_mode != end_mode:
            curr_mode = 'minor' if curr_mode == 'major' else 'major'
            curr_signs += step
            for name, (m, s) in TONALITIES.items():
                if m == curr_mode and s == curr_signs:
                    path.append(name)
                    break
        inter_count = len(path) - 2
        return {inter_count: [path]}

    graph = {ton: get_relatives_exact(ton) for ton in TONALITIES}
    queue = deque([[start]])
    all_paths = []
    found_inter_count = None

    while queue:
        current_path = queue.popleft()
        inter_count = len(current_path) - 2
        if found_inter_count is not None and inter_count > found_inter_count: break
        current_node = current_path[-1]

        if current_node == end:
            if is_valid_sequence(current_path):
                if found_inter_count is None: found_inter_count = inter_count
                all_paths.append(current_path)
            continue

        for neighbor in graph[current_node]:
            if neighbor not in current_path:
                queue.append(current_path + [neighbor])

    paths_by_inter = {}
    for p in all_paths:
        inter_count = len(p) - 2
        if inter_count not in paths_by_inter: paths_by_inter[inter_count] = []
        paths_by_inter[inter_count].append(p)

    if 2 in paths_by_inter: return {2: paths_by_inter}
    if 3 in paths_by_inter: return {3: paths_by_inter}
    if paths_by_inter:
        min_inter = min(paths_by_inter.keys())
        return {min_inter: paths_by_inter[min_inter]}
    return {}


# =====================================================================
# --- ЛЕГКИЙ ИНТЕРФЕЙС STREAMLIT ДЛЯ СМАРТФОНОВ ---
# =====================================================================

st.set_page_config(page_title="Модуляции", page_icon="🎵")
st.title("🎼 План тональных модуляций")

tonality_list = sorted(list(TONALITIES.keys()))

# Красивые мобильные выпадающие списки
start_key = st.selectbox("Начальная тональность:", tonality_list, index=tonality_list.index("C-dur"))
end_key = st.selectbox("Конечная тональность:", tonality_list, index=tonality_list.index("a-moll"))

if st.button("Рассчитать планы", type="primary", use_container_width=True):
    plans_dict = find_modulation_plans(start_key, end_key)

    if not plans_dict or isinstance(plans_dict, str):
        st.error(plans_dict if isinstance(plans_dict, str) else "План перехода не найден.")
    else:
        global_degree = get_pair_degree(start_key, end_key)
        inter_count = list(plans_dict.keys())[0]
        actual_plans = plans_dict[inter_count]

        st.success(f"📊 Степень связи: {global_degree}-я степень родства")
        st.info(f"⏱️ Промежуточных тональностей: {inter_count} | Вариантов: {len(actual_plans)}")

        # Вывод результатов красивыми карточками
        for idx, plan in enumerate(actual_plans, 1):
            st.code(f"Вариант №{idx}: " + " ➔ ".join(plan), language="music")
