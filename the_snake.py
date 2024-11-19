from random import randint
from typing import Optional

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
GRID_MIDLE = (SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)


# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Словарь с направлениями движения змеи,
# обрабатывается в handle_keys
SNAKE_MOVEMENTS: dict[tuple: tuple] = {
    (DOWN, pygame.K_UP): UP,
    (UP, pygame.K_DOWN): DOWN,
    (RIGHT, pygame.K_LEFT): LEFT,
    (LEFT, pygame.K_RIGHT): RIGHT
}

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Описание игровых классов

class GameObject:
    """Родительский класс
    для всех объектов
    """

    def __init__(self) -> None:
        # Позиция по умолчанию -  посередине экрана.
        self.position: tuple[int, int] = GRID_MIDLE
        # Цвет по умолчанию в родительском классе
        self.body_color: Optional[tuple[int, int, int]] = None

    def draw(self) -> None:
        """Функция заглушка
        для дочерних классов
        """


class Apple(GameObject):
    """Яблоко — это просто квадрат размером в одну ячейку игрового поля.
    При создании яблока координаты для него определяются случайным образом
    и сохраняются до тех пор, пока змейка не «съест» яблоко.
    После этого для яблока вновь задаются случайные координаты.
    self.body_color: Optional[tuple[int, int, int]] Цвет объекта.
    self.snake_positions: list[tuple[int, int] Координаты змеи
    self.position: tuple[int, int] позиция объекта на поле.
    return None
    """

    def __init__(
        self,
        snake_positions: Optional[list[tuple[int, int]]] = None
    ) -> None:
        super().__init__()
        self.body_color: Optional[tuple[int, int, int]] = APPLE_COLOR
        self.snake_positions = snake_positions
        self.position: tuple[int, int] = self.randomize_position()

    def draw(self) -> None:
        """Функция отрисовки яблока."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self) -> tuple[int, int]:
        """Функция для генерации новой позиции яблока"""
        position: tuple[int, int] = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )
        if position in self.snake_positions:
            self.randomize_position()
        return position

    def update_position(self) -> None:
        """Функция для переопределения позиция яблока на поле"""
        self.position = self.randomize_position()


class Snake(GameObject):
    """Змейка изначально состоит из одной головы — из одной ячейки
    на игровом поле. Змейка постоянно куда-то ползёт и после того,
    как «съест» яблоко, вырастает на один сегмент.
    При запуске игры змейка сразу же начинает движение вправо по игровому полю.
    self.body_color: Optional[tuple[int, int, int]] Цвет змеи.
    self.apple_obj: Apple экземпляр класса Apple для получения координат.
    self.direction: tuple[int, int] Направление движения змеи
    self.next_direction: Optional[tuple[int, int]] Промежуточное состояние
    движения змеи.
    self.positions: list[tuple[int, int],] Координаты всех элементов змеи
    на поле.
    self.length: Optional[int] Текущая длинна змеи
    self.last: Optional[tuple[int, int]] Определение хвоста змеи
    return None
    """

    def __init__(self) -> None:
        super().__init__()
        self.body_color: Optional[tuple[int, int, int]] = SNAKE_COLOR
        self.reset()

    def update_direction(self) -> None:
        """обновляет направление движения змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions и удаляя
        последний элемент, если длина змейки не увеличилась.
        """
        # Получение текущих координат головы змеи.
        width_coord, height_coord = self.get_head_position()
        # Распаковка направления движения.
        width_direction, height_direction = self.direction
        # Определение вектора движения.
        # Движение змейки
        position_to_insert = (
            (width_coord + (width_direction * GRID_SIZE)) % SCREEN_WIDTH,
            (height_coord + (height_direction * GRID_SIZE)) % SCREEN_HEIGHT,
        )
        self.positions.insert(
            0, position_to_insert
        )
        self.last = self.positions.pop()

    def draw(self) -> None:
        """отрисовывает змейку на экране, затирая следа"""
        # Перебор элементов без "хвоста" для отрисовки фигур.
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки.
        head_rect = pygame.Rect(
            self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента.
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """возвращает позицию головы змейки
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def reset(self):
        """сбрасывает змейку в начальное состояние."""
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: Optional[tuple[int, int]] = None
        # Параметры для дебага positions:
        # [(300, 300 + x) for x in range(1, 400, 20)].
        self.positions: list[tuple[int, int], ] = [self.position]
        # Длинна змеи.
        self.length: Optional[int] = len(self.positions)
        # Координаты хвоста, по умолчанию его нет
        self.last: Optional[tuple[int, int]] = None


def handle_keys(game_object):
    """обрабатывает нажатия клавиш,
    чтобы изменить направление движения змейки.
    """
    # Словарь параметров движения змейки.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        # Перебор словарей для определения направления движения.
        if event.type == pygame.KEYDOWN:
            for key, value in SNAKE_MOVEMENTS.items():
                vector, button = key
                if event.key == button and game_object.direction != vector:
                    game_object.next_direction = value


def main():
    """Инициализация PyGame:"""
    pygame.init()
    # Экземпляры классов.
    snake = Snake()
    # Передача координат змеи, для генерации позиции яблока
    apple = Apple(snake.positions)
    # Основная логика игры.
    while True:
        # Симуляция задержки.
        clock.tick(SPEED)
        # Передача управления змейке.
        handle_keys(snake)
        # Отрисовка змеи.
        snake.draw()
        # Отрисовка яблока.
        apple.draw()
        # Обновление направления движения.
        snake.update_direction()
        # Движение змейки
        snake.move()
        # Проверка - съела ли змея яблоко.
        if snake.get_head_position() == apple.position:
            snake.positions.insert(0, apple.position)
            apple.update_position()
        # Проверка на столкновении с телом.
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.update_position()
            screen.fill(BOARD_BACKGROUND_COLOR)
        # Отрисовка объектов на экране.
        pygame.display.update()


if __name__ == '__main__':
    main()
