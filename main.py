from collections import deque
import flet as ft

# =====================================================================
# --- БАЗА ДАННЫХ И МУЗЫКАЛЬНАЯ ЛОГИКА (МОСКОВСКАЯ ШКОЛА ГАРМОНИИ) ---
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
    raw_tonic = tonality.split('-')
    if raw_tonic[0].lower() == 'b': return 'B'
    if raw_tonic[0].lower() == 'h': return 'H'
    return raw_tonic[0].upper() + raw_tonic[0][1:] if len(raw_tonic[0]) > 1 else raw_tonic[0].upper()


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
# --- МОБИЛЬНЫЙ ИНТЕРФЕЙС FLET ДЛЯ ANDROID ---
# =====================================================================

def build_gui(page: ft.Page):
    page.title = "Калькулятор модуляций"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    tonality_list = sorted(list(TONALITIES.keys()))
    dropdown_options = [ft.dropdown.Option(t) for t in tonality_list]

    title = ft.Text("Планы тональных модуляций", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    combo_start = ft.Dropdown(options=dropdown_options, value="C-dur", width=300, label="Начальная тональность")
    combo_end = ft.Dropdown(options=dropdown_options, value="a-moll", width=300, label="Конечная тональность")

    # Поле вывода результатов, оптимизированное под экран телефона
    text_result = ft.TextField(label="Результаты расчета", multiline=True, min_lines=6, max_lines=12, width=320,
                               read_only=True)

    def calculate_click(e):
        start = combo_start.value
        end = combo_end.value
        text_result.value = ""

        plans_dict = find_modulation_plans(start, end)

        if not plans_dict or isinstance(plans_dict, str):
            text_result.value = f"⚠️ {plans_dict if isinstance(plans_dict, str) else 'План перехода не найден.'}"
            page.update()
            return

        global_degree = get_pair_degree(start, end)
        inter_count = list(plans_dict.keys())[0]
        actual_plans = plans_dict[inter_count]

        output = f"📊 Степень связи: {global_degree}-я степень родства\n"
        output += f"⏱️ Промежуточных тональностей: {inter_count}\n"
        output += f"✨ Вариантов: {len(actual_plans)}\n"
        output += "-" * 35 + "\n\n"

        for idx, plan in enumerate(actual_plans, 1):
            output += f"План №{idx}: " + " -> ".join(plan) + "\n\n"

        text_result.value = output
        page.update()

    btn_calc = ft.ElevatedButton("Рассчитать планы", on_click=calculate_click, width=200)

    page.add(
        ft.Column(
            controls=[
                title,
                ft.Divider(),
                combo_start,
                combo_end,
                ft.Container(content=btn_calc, margin=ft.margin.only(top=10, bottom=10)),
                text_result
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )


if __name__ == "__main__":
    ft.app(target=build_gui)
