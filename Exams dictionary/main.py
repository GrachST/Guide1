import pygame
import sys
import json

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Словарь")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = pygame.Color('dodgerblue2')
HIGHLIGHT = pygame.Color('lightblue')  # Цвет подсветки при наведении курсора

# Шрифты
font = pygame.font.Font(None, 48)

# Загрузка словаря из файла
def load_dictionary(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return {key.lower(): value for key, value in data.items()}

dictionary = load_dictionary('dictionary.json')

# Ввод слова
input_box = pygame.Rect(450, 200, 1400, 50)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
definition = []
cursor_position = 0  # Позиция курсора
suggestions = []  # Подсказки
hovered_index = -1  # Индекс для подсветки подсказки при наведении

def draw_text(surface, text, pos, color=BLACK):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

# Функция для обновления подсказок
def update_suggestions(text):
    global suggestions, hovered_index
    # Показываем подсказки только если введено 2 и более символов
    if len(text) >= 2:
        suggestions = [key for key in dictionary.keys() if key.startswith(text.lower())]
        hovered_index = -1  # Сбрасываем индекс при обновлении
    else:
        suggestions = []
        hovered_index = -1

# Основной цикл
while True:
    mouse_pos = pygame.mouse.get_pos()  # Позиция курсора мыши

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive

            # Обрабатываем выбор подсказки щелчком
            if event.button == 1:  # ЛКМ
                for i, suggestion in enumerate(suggestions):
                    suggestion_rect = pygame.Rect(450, 300 + len(definition) * 50 + i * 30, 400, 30)
                    if suggestion_rect.collidepoint(event.pos):
                        text = suggestion
                        cursor_position = len(text)
                        suggestions = []  # Очищаем подсказки после выбора
                        hovered_index = -1
                        break

        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    if hovered_index >= 0 and hovered_index < len(suggestions):
                        # Если подсказка выбрана, заменяем текст на выбранную подсказку
                        text = suggestions[hovered_index]
                        cursor_position = len(text)
                        suggestions = []
                        hovered_index = -1
                    else:
                        # Поиск слова в словаре
                        entry = dictionary.get(text.lower(), "Формула не найдена.")
                        definition = entry if isinstance(entry, list) else [entry]
                        text = ''
                        cursor_position = 0  # Сброс позиции курсора
                        suggestions = []  # Сброс подсказок
                        hovered_index = -1  # Сброс индекса подсказок
                elif event.key == pygame.K_BACKSPACE:
                    if cursor_position > 0:
                        text = text[:cursor_position - 1] + text[cursor_position:]
                        cursor_position -= 1
                elif event.key == pygame.K_DELETE:
                    if cursor_position < len(text):
                        text = text[:cursor_position] + text[cursor_position + 1:]
                elif event.key == pygame.K_LEFT:
                    if cursor_position > 0:
                        cursor_position -= 1
                elif event.key == pygame.K_RIGHT:
                    if cursor_position < len(text):
                        cursor_position += 1
                elif event.key == pygame.K_DOWN:
                    if suggestions:
                        hovered_index = (hovered_index + 1) % len(suggestions)  # Перемещение вниз
                elif event.key == pygame.K_UP:
                    if suggestions:
                        hovered_index = (hovered_index - 1) % len(suggestions)  # Перемещение вверх
                else:
                    # Ограничение по количеству символов на основании ширины поля ввода
                    new_text = text[:cursor_position] + event.unicode + text[cursor_position:]
                    if font.size(new_text)[0] <= input_box.width - 20:  # 20 - отступ
                        text = new_text
                        cursor_position += 1

            # Обновление подсказок
            update_suggestions(text)

    # Обновление экрана
    screen.fill(WHITE)

    # Отображение заголовка
    draw_text(screen, "Словарь ОГЭ и ЕГЭ", (700, 100), BLACK)
    draw_text(screen, "Поиск формул и констант:", (10, 210), BLACK)

    # Отображение поля ввода с фоном
    pygame.draw.rect(screen, (255, 255, 255, 255), input_box)  # Заливка фона
    pygame.draw.rect(screen, (0, 0, 0, 0), input_box, 2)  # Границы

    # Отображение текста в поле ввода
    draw_text(screen, text, (input_box.x + 10, input_box.y + 10))

    # Отображение курсора
    cursor_x = input_box.x + 10 + font.size(text[:cursor_position])[0]
    cursor_y = input_box.y + 10
    if active:  # Рисуем курсор только когда поле активно
        pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + 30), 2)

    # Отображение определения
    if definition:  # Проверяем, что есть что отображать
        for i, line in enumerate(definition):
            draw_text(screen, line, (400, 300 + i * 50), BLACK)  # Увеличиваем Y-координату для каждой строки

    # Отображение подсказок
    if suggestions:
        for i, suggestion in enumerate(suggestions):
            suggestion_rect = pygame.Rect(450, 300 + len(definition) * 50 + i * 30, 400, 30)
            # Подсветка подсказки, если курсор находится на ней или она выбрана с клавиатуры
            if i == hovered_index:
                pygame.draw.rect(screen, HIGHLIGHT, suggestion_rect)  # Подсветка фона
            draw_text(screen, suggestion, (450, 300 + len(definition) * 50 + i * 30), BLUE if i == hovered_index else BLACK)

    pygame.display.flip()
