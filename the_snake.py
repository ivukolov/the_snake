from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE


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

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Родительский класс
    для всех объектов
    """

    def __init__(self) -> None:
        # Позиция по умолчанию -  посередине экрана.
        self.position = (SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)
        # Цвет по умолчанию в родительском классе
        self.body_color = None

    def draw(self) -> None:
        """Функция заглушка
        для дочерних классов
        """
        pass


class Apple(GameObject):
    """Яблоко — это просто квадрат размером в одну ячейку игрового поля.
    При создании яблока координаты для него определяются случайным образом
    и сохраняются до тех пор, пока змейка не «съест» яблоко.
    После этого для яблока вновь задаются случайные координаты.
    """

    def __init__(self) -> None:
        super().__init__()
        self.body_color = APPLE_COLOR
        self.position = self.randomize_position()

    def draw(self) -> None:
        """Функция отрисовки яблока"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self) -> tuple:
        """Функция для переопределения позиция яблока на поле"""
        position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )
        return position

    def update_position(self):
        self.position = self.randomize_position()


class Snake(GameObject):
    """Змейка изначально состоит из одной головы — из одной ячейки
    на игровом поле. Змейка постоянно куда-то ползёт и после того,
    как «съест» яблоко, вырастает на один сегмент.
    При запуске игры змейка сразу же начинает движение вправо по игровому полю.
    """

    def __init__(self, apple) -> None:
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.apple_obj = apple
        self.length = None
        self.direction = RIGHT
        self.next_direction = None
        self.positions = [(300, 300 + x) for x in range(1, 400, 20)]
        self.last = None

    def update_direction(self):
        """обновляет направление движения змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions и удаляя
        последний элемент, если длина змейки не увеличилась.
        """

        # Получение текущих координат головы змеи.
        width_coord, height_coord = self.get_head_position()
        # Определение вектора движения.
        width_move = GRID_SIZE * self.direction[0] \
            if self.direction[0] != 0 else 0
        height_move = GRID_SIZE * self.direction[1] \
            if self.direction[1] != 0 else 0
        # Отзеркаливание змейки.
        # Определение правого края экрана
        if width_coord >= SCREEN_WIDTH:
            width_coord = 0
            width_move = 0
        # Определение левого края экрана.
        elif width_coord < 0:
            width_coord = SCREEN_WIDTH
        # Определение нижнего края.
        elif height_coord >= SCREEN_HEIGHT:
            height_coord = 0
            height_move = 0
        # Определение верхнего края.
        elif height_coord < 0:
            height_coord = SCREEN_HEIGHT
        # Движение змейки
        self.positions.insert(
            0, (width_coord + width_move, height_coord + height_move))
        self.last = self.positions.pop()
        # Сравнение координат головы змеи и яблока,
        # если сошлись увеличиваем длинну змеи.
        if self.get_head_position() == self.apple_obj.position:
            self.positions.insert(0, self.apple_obj.position)
            self.apple_obj.update_position()
        if self.chek_collapse():
            self.reset()

    def draw(self) -> None:
        """отрисовывает змейку на экране, затирая след"""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
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
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.positions.clear
        self.positions = [self.position]
        self.direction = RIGHT

    def chek_collapse(self):
        """Проверка на столкновении змейки с самой собой"""
        return any(self.get_head_position() == coords
                   for coords in self.positions[2:])


def handle_keys(game_object):
    """обрабатывает нажатия клавиш,
    чтобы изменить направление движения змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Инициализация PyGame:"""
    pygame.init()
    # Экземпляры классов.
    apple = Apple()
    # Объект apple передаётся при инициализации классу Snake
    # Для определения координат яблока
    snake = Snake(apple)
    # Основная логика игры.
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        apple.draw()
        snake.draw()
        snake.move()
        snake.update_direction()
        pygame.display.update()


if __name__ == '__main__':
    main()


# Метод draw класса Apple
# def draw(self):
#     rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
#     pygame.draw.rect(screen, self.body_color, rect)
#     pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

# # Метод draw класса Snake
# def draw(self):
#     for position in self.positions[:-1]:
#         rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
#         pygame.draw.rect(screen, self.body_color, rect)
#         pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

#     # Отрисовка головы змейки
#     head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
#     pygame.draw.rect(screen, self.body_color, head_rect)
#     pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

#     # Затирание последнего сегмента
#     if self.last:
#         last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
#         pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

# Функция обработки действий пользователя
# def handle_keys(game_object):
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             raise SystemExit
#         elif event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_UP and game_object.direction != DOWN:
#                 game_object.next_direction = UP
#             elif event.key == pygame.K_DOWN and game_object.direction != UP:
#                 game_object.next_direction = DOWN
#             elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
#                 game_object.next_direction = LEFT
#             elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
#                 game_object.next_direction = RIGHT

# Метод обновления направления после нажатия на кнопку
# def update_direction(self):
#     if self.next_direction:
#         self.direction = self.next_direction
#         self.next_direction = None
