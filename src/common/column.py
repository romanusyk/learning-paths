from dataclasses import dataclass
from typing import List, Dict


class ColType:
    """Semantic column types used in preprocessing."""

    string = "string"
    category = "category"
    likert = "likert"


@dataclass
class Column:
    name: str
    raw_name: str
    raw_name_eng: str
    type_: str
    nullable: bool = False


# NOTE: Exclude PII columns like timestamp, email, first name, last name.
# Add demographic/context columns that exist in the form but were missing in the notebook.
columns: List[Column] = [
    Column(
        name="position",
        raw_name="Яка ваша спеціалізація в ІТ?",
        raw_name_eng="What is your IT specialization?",
        type_=ColType.category,
    ),
    Column(
        name="age_group",
        raw_name="Вікова група",
        raw_name_eng="Age group",
        type_=ColType.category,
    ),
    Column(
        name="years_experience",
        raw_name="Скільки років досвіду в ІТ ви маєте?",
        raw_name_eng="How many years of experience in IT do you have?",
        type_=ColType.category,
    ),
    # --- Level (self-assessed skills) ---
    Column(
        name="level:reading",
        raw_name="Наскільки впевнено ви почуваєтесь, використовуючи англійську для: [Читання]",
        raw_name_eng="How confident do you feel using English for: [Reading]",
        type_=ColType.likert,
    ),
    Column(
        name="level:writing",
        raw_name="Наскільки впевнено ви почуваєтесь, використовуючи англійську для: [Письма]",
        raw_name_eng="How confident do you feel using English for: [Writing]",
        type_=ColType.likert,
    ),
    Column(
        name="level:listening",
        raw_name="Наскільки впевнено ви почуваєтесь, використовуючи англійську для: [Слухання]",
        raw_name_eng="How confident do you feel using English for: [Listening]",
        type_=ColType.likert,
    ),
    Column(
        name="level:speaking",
        raw_name="Наскільки впевнено ви почуваєтесь, використовуючи англійську для: [Говоріння]",
        raw_name_eng="How confident do you feel using English for: [Speaking]",
        type_=ColType.likert,
    ),
    # --- Method effectiveness (0%-100% scale mapped to 1..5) ---
    Column(
        name="method_effectiveness:online_courses",
        raw_name="Оцініть ефективність наведених методів для вдосконалення рівня вашої англійської [Онлайн курси та додатки (такі як Duolingo, Coursera тощо)]",
        raw_name_eng="Rate effectiveness of methods to improve English [Online courses and apps (Duolingo, Coursera, etc.)]",
        type_=ColType.likert,
    ),
    Column(
        name="method_effectiveness:private_lessons",
        raw_name="Оцініть ефективність наведених методів для вдосконалення рівня вашої англійської [Заняття з викладачем]",
        raw_name_eng="Rate effectiveness of methods to improve English [Lessons with a teacher]",
        type_=ColType.likert,
    ),
    Column(
        name="method_effectiveness:textbooks",
        raw_name="Оцініть ефективність наведених методів для вдосконалення рівня вашої англійської [Самостійна робота з книгами та підручниками]",
        raw_name_eng="Rate effectiveness of methods to improve English [Self-study with books and textbooks]",
        type_=ColType.likert,
    ),
    Column(
        name="method_effectiveness:watching_movies",
        raw_name="Оцініть ефективність наведених методів для вдосконалення рівня вашої англійської [Перегляд фільмів та телепередач англійською]",
        raw_name_eng="Rate effectiveness of methods to improve English [Watching movies and TV in English]",
        type_=ColType.likert,
    ),
    Column(
        name="method_effectiveness:audio",
        raw_name="Оцініть ефективність наведених методів для вдосконалення рівня вашої англійської [Прослуховування англомовних пісень та подкастів]",
        raw_name_eng="Rate effectiveness of methods to improve English [Listening to English songs and podcasts]",
        type_=ColType.likert,
    ),
    Column(
        name="method_effectiveness:speaking_club",
        raw_name="Оцініть ефективність наведених методів для вдосконалення рівня вашої англійської [Розмовні клуби з носієм англійської]",
        raw_name_eng="Rate effectiveness of methods to improve English [Speaking clubs with native speaker]",
        type_=ColType.likert,
    ),
    Column(
        name="method_effectiveness:reading_books",
        raw_name="Оцініть ефективність наведених методів для вдосконалення рівня вашої англійської [Читання англомовних книжок та статей]",
        raw_name_eng="Rate effectiveness of methods to improve English [Reading English books and articles]",
        type_=ColType.likert,
    ),
    Column(
        name="method_effectiveness:work_tasks",
        raw_name="Оцініть ефективність наведених методів для вдосконалення рівня вашої англійської [Використання англійської у роботі (наприклад, ділове листування та зустрічі)]",
        raw_name_eng="Rate effectiveness of methods to improve English [Using English at work (emails, meetings)]",
        type_=ColType.likert,
    ),
    # --- Motivational activities ---
    Column(
        name="motives:online_exercises",
        raw_name="Наскільки вас зацікавлюють та мотивують такі активності: [Інтерактивні вправи онлайн]",
        raw_name_eng="How motivating are these activities: [Interactive online exercises]",
        type_=ColType.likert,
    ),
    Column(
        name="motives:speaking_club",
        raw_name="Наскільки вас зацікавлюють та мотивують такі активності: [Спілкування в групі]",
        raw_name_eng="How motivating are these activities: [Group communication]",
        type_=ColType.likert,
    ),
    Column(
        name="motives:watching_movies",
        raw_name="Наскільки вас зацікавлюють та мотивують такі активності: [Перегляд фільмів та іншого відео контенту англійською]",
        raw_name_eng="How motivating are these activities: [Watching movies and other video content in English]",
        type_=ColType.likert,
    ),
    Column(
        name="motives:reading_books",
        raw_name="Наскільки вас зацікавлюють та мотивують такі активності: [Читання статей та книг англійською]",
        raw_name_eng="How motivating are these activities: [Reading articles and books in English]",
        type_=ColType.likert,
    ),
    Column(
        name="motives:work_tasks",
        raw_name="Наскільки вас зацікавлюють та мотивують такі активності: [Виконання робочих задач із використанням англійської]",
        raw_name_eng="How motivating are these activities: [Completing work tasks using English]",
        type_=ColType.likert,
    ),
    Column(
        name="motives:gamified_learning",
        raw_name="Наскільки вас зацікавлюють та мотивують такі активності: [Навчання в ігровій формі]",
        raw_name_eng="How motivating are these activities: [Gamified learning]",
        type_=ColType.likert,
    ),
    Column(
        name="motives:personalised_feedback",
        raw_name="Наскільки вас зацікавлюють та мотивують такі активності: [Персоналізований зворотній звʼязок від викладача]",
        raw_name_eng="How motivating are these activities: [Personalized feedback from a teacher]",
        type_=ColType.likert,
    ),
    # --- Statements (Likert) ---
    Column(
        name="enjoyed_school_classes",
        raw_name="Уроки англійської в школі приносили мені задоволення.",
        raw_name_eng="I enjoyed English classes at school.",
        type_=ColType.likert,
    ),
    Column(
        name="felt_pressure",
        raw_name="Я можу пригадати значний тиск до вивчення англійської з боку моїх батьків чи через атмосферу на роботі.",
        raw_name_eng="I recall significant pressure to learn English from parents or workplace.",
        type_=ColType.likert,
    ),
    Column(
        name="grown_since_native_talk",
        raw_name="Від моменту моєї найпершої розмови з носієм англійської мови, рівень моєї англійської значно виріс. (Якщо ви ніколи не спілкувалися з носіями англійської, пропустить це питання)",
        raw_name_eng="Since my first conversation with a native speaker, my English has significantly improved. (Skip if never spoken with natives)",
        type_=ColType.likert,
        nullable=True,
    ),
    Column(
        name="perfection_is_key_to_career",
        raw_name="Досконале знання англійської є запорукою успіху у моїй професії.",
        raw_name_eng="Perfect English is key to success in my profession.",
        type_=ColType.likert,
    ),
    Column(
        name="i_know_all_i_need",
        raw_name="Мій поточний рівень англійської покриває усі мої потреби.",
        raw_name_eng="My current level of English covers all my needs.",
        type_=ColType.likert,
    ),
    Column(
        name="english_is_not_so_important",
        raw_name="Знання англійської виявилось не таким важливим, як я вважав(-ла) спочатку.",
        raw_name_eng="Knowing English turned out less important than I initially thought.",
        type_=ColType.likert,
    ),
    Column(
        name="learning_is_demaning",
        raw_name="Вивчення англійської потребує забагато часу та зусиль.",
        raw_name_eng="Learning English requires too much time and effort.",
        type_=ColType.likert,
    ),
    Column(
        name="need_english_for_work_docs",
        raw_name="Англійська мені необхідна для технічної документації та інших ресурсів, що стосуються моєї роботи.",
        raw_name_eng="I need English for technical documentation and other work-related resources.",
        type_=ColType.likert,
    ),
    Column(
        name="curious_about_english_colleagues",
        raw_name="Мені цікаво дізнатися більше про моїх англомовних колег та друзів.",
        raw_name_eng="I am curious to learn more about my English-speaking colleagues and friends.",
        type_=ColType.likert,
    ),
    Column(
        name="learning_is_exhausting",
        raw_name="Вивчення англійської нудне та виснажливе.",
        raw_name_eng="Learning English is boring and exhausting.",
        type_=ColType.likert,
    ),
    Column(
        name="speaking_is_key_to_career",
        raw_name="Якість спілкування з моїми англомовними колегами є запорукою мого карʼєрного росту.",
        raw_name_eng="Quality of communication with English-speaking colleagues is key to career growth.",
        type_=ColType.likert,
    ),
    Column(
        name="need_to_feel_progress",
        raw_name="Я засмучуюсь, коли не відчуваю прогресу у вивченні англійської.",
        raw_name_eng="I get upset when I do not feel progress in learning English.",
        type_=ColType.likert,
    ),
    Column(
        name="like_colleagues",
        raw_name="Мої англомовні колеги -- товариські, сердечні та творчі люди. (Пропустіть це питання, якщо ніколи не працювали з англомовними колегами)",
        raw_name_eng="My English-speaking colleagues are friendly, warm and creative. (Skip if you have never worked with English-speaking colleagues)",
        type_=ColType.likert,
        nullable=True,
    ),
    Column(
        name="glad_to_feel_progress",
        raw_name="Я тішуся, коли помічаю, як покращуються мої навички англійської.",
        raw_name_eng="I am glad when I notice improvements in my English skills.",
        type_=ColType.likert,
    ),
    Column(
        name="must_learn",
        raw_name="Від ІТ спеціалістів в Україні очікується високий рівень знання англійської.",
        raw_name_eng="IT specialists in Ukraine are expected to have a high level of English.",
        type_=ColType.likert,
    ),
    Column(
        name="was_ok_with_native",
        raw_name="Мені було комфортно під час останньої розмови з носієм англійської. (Пропустіть питання, якщо ніколи не мали розмови з носіями англійської)",
        raw_name_eng="I felt comfortable during my last conversation with a native English speaker. (Skip if never had a conversation with natives)",
        type_=ColType.likert,
        nullable=True,
    ),
    Column(
        name="was_ok_with_non_native",
        raw_name="Мені було комфортно під час останньої розмови англійською з НЕ-носієм англійської (колегою, викладачем, другом тощо).",
        raw_name_eng="I felt comfortable during my last conversation in English with a non-native speaker (colleague, teacher, friend, etc.).",
        type_=ColType.likert,
    ),
    Column(
        name="english_is_not_applicable",
        raw_name="Мені рідко зустрічаються нагоди застосувати мої навички англійської.",
        raw_name_eng="I rarely encounter opportunities to apply my English skills.",
        type_=ColType.likert,
    ),
    Column(
        name="value_original_movies",
        raw_name="Я пропускаю багато деталей, переглядаючи англомовні фільми у перекладі або з субтитрами.",
        raw_name_eng="I miss many details when watching English-language movies in translation or with subtitles.",
        type_=ColType.likert,
    ),
    Column(
        name="value_original_books",
        raw_name="Я пропускаю багато деталей, читаючи англомовну літературу у перекладі.",
        raw_name_eng="I miss many details when reading English literature in translation.",
        type_=ColType.likert,
    ),
    Column(
        name="learning_is_fun",
        raw_name="Вивчення англійської -- приємне та захоплююче.",
        raw_name_eng="Learning English is pleasant and exciting.",
        type_=ColType.likert,
    ),
    Column(
        name="want_to_improve",
        raw_name="Я хочу покращувати мої навички англійської.",
        raw_name_eng="I want to improve my English skills.",
        type_=ColType.likert,
    ),
    Column(
        name="curious_about_english_culture",
        raw_name="Мені цікаво дізнаватися нове про культуру англомовних країн.",
        raw_name_eng="I am curious to learn more about the culture of English-speaking countries.",
        type_=ColType.likert,
    ),
    Column(
        name="curious_about_english_system",
        raw_name="Мені цікаво, чому англійська мова влаштована саме за такими структурою та правилами, а не інакше.",
        raw_name_eng="I am curious why English is structured and ruled the way it is.",
        type_=ColType.likert,
    ),
    # --- Free text ---
    Column(
        name="extra_methods",
        raw_name="Чи можете ви навести інші способи вивчення англійської, які ви знайшли для себе особливо ефективними чи неефективними? Якщо так, опишіть їх.",
        raw_name_eng="Other methods of learning English you found effective or ineffective (describe).",
        type_=ColType.string,
        nullable=True,
    ),
    Column(
        name="obstacles",
        raw_name="Чи припиняли ви вивчення англійської принаймні один раз? Якщо так, опишіть основні причини.",
        raw_name_eng="Have you stopped learning English at least once? If yes, describe the main reasons.",
        type_=ColType.string,
        nullable=True,
    ),
]


col_mapping: Dict[str, str] = {col.raw_name: col.name for col in columns}
rev_col_mapping: Dict[str, str] = {col.name: col.raw_name for col in columns}

all_col_names: List[str] = [col.name for col in columns]

likert_col_names: List[str] = [
    col.name for col in columns if col.type_ == ColType.likert
]

level_col_names: List[str] = [
    col.name for col in columns if col.name.startswith("level:")
]

motives_col_names: List[str] = [
    col.name for col in columns if col.name.startswith("motives:")
]

method_effectiveness_col_names: List[str] = [
    col.name for col in columns if col.name.startswith("method_effectiveness:")
]

# For analytics convenience (same as in the notebook)
instrumental_col_names: List[str] = [
    "perfection_is_key_to_career",
    "need_english_for_work_docs",
    "speaking_is_key_to_career",
    "must_learn",
]

integrative_col_names: List[str] = [
    "curious_about_english_colleagues",
    # "like_colleagues",
    "value_original_movies",
    "value_original_books",
    "curious_about_english_culture",
    "curious_about_english_system",
]

# Value mappings for Likert-like questions, derived from the notebook
MOTIVES_MAPPING: Dict[str, int] = {
    "Геть не цікаво": 1,
    "Трохи нудно": 2,
    "Нейтрально": 3,
    "Чудово": 4,
    "Обожнюю": 5,
}

METHOD_EFFECTIVENESS_MAPPING: Dict[str, int] = {
    "0%": 1,
    "25%": 2,
    "50%": 3,
    "75%": 4,
    "100%": 5,
}


