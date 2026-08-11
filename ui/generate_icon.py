from PIL import Image, ImageDraw, ImageFont


# Размер иконки
SIZE = 64

# Цвета
BACKGROUND = '#3ec1d3'
TEXT = '#2b2e4a'

# Создаём изображение
img = Image.new('RGB', (SIZE, SIZE), color=BACKGROUND)
draw = ImageDraw.Draw(img)

# Жирный шрифт
font = ImageFont.truetype(
    'C:/Windows/Fonts/arialbd.ttf',
    38
)

# Текст
text = "DI"

# Получаем размеры текста
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Центрируем текст
x = (SIZE - text_width) // 2
y = (SIZE - text_height) // 2 - bbox[1]

# Рисуем DI
draw.text(
    (x, y),
    text,
    font=font,
    fill=TEXT
)

# Сохраняем как ICO
img.save(
    'icon.ico',
    format='ICO',
    sizes=[
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64)
    ]
)