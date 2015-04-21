#!/usr/bin/python3.4

from sfml import sf

import math

PADDLE_SIZE = sf.Vector2(140, 30)
PADDLE_SPEED = 750
PADDLE_COLOR = sf.Color.WHITE
BRICK_SIZE = sf.Vector2(50, 25)
BRICK_TYPES = {
  0: sf.Color.RED,
  1: sf.Color.BLUE,
  2: sf.Color.GREEN,
  3: sf.Color.WHITE,
}
BRICK_GAP_WIDTH = 12
CLEAR_COLOR = sf.Color(0, 128, 128)
LEVEL_SIZE = sf.Vector2(10, 8)
BALL_RADIUS = 10.0
BALL_COLOR = sf.Color.WHITE
BALL_SPEED = 500.0

def vector_length(vector):
  return math.sqrt(vector.x * vector.x + vector.y * vector.y)

def normalized_vector(vector):
  return vector / vector_length(vector)

def get_line_intersection(line0, line1):
  """
  line0 and line1 are tuples with 2 sf.Vector2 each.

  Implemented this formula:
  http://de.wikipedia.org/wiki/Schnittpunkt#Schnittpunkt_zweier_Geraden
  """

  x1, y1 = line0[0]
  x2, y2 = line0[1]
  x3, y3 = line1[0]
  x4, y4 = line1[1]

  return sf.Vector2(
    (
      ((x4 - x3) * (x2 * y1 - x1 * y2) - (x2 - x1) * (x4 * y3 - x3 * y4)) /
      ((y4 - y3) * (x2 - x1) - (y2 - y1) * (x4 - x3))
    ),
    (
      ((y1 - y2) * (x4 * y3 - x3 * y4) - (y3 - y4) * (x2 * y1 - x1 * y2)) /
      ((y4 - y3) * (x2 - x1) - (y2 - y1) * (x4 - x3))
    ),
  )

def test_circle_rect_collision(circle_position, radius, rect, translation):
  from collections import namedtuple

  collision = None

  # Test if circle's bounding box is intersecting with the target rect (broad
  # phase)
  bounding_box = sf.Rectangle(
    circle_position - sf.Vector2(radius, radius),
    sf.Vector2(2 * radius, 2 * radius),
  )

  if bounding_box.intersects(rect) is not None:
    Response = namedtuple("Response", ("position", "side"))

    translation_line = (circle_position, circle_position + translation)

    if translation.x > 0: # Left
      rect_line = (
        sf.Vector2(rect.left, rect.top),
        sf.Vector2(rect.left, rect.bottom),
      )
      intersection = get_line_intersection(translation_line, rect_line)
      collision = Response(intersection, "left")

    elif translation.x < 0: # Right
      rect_line = (
        sf.Vector2(rect.right, rect.top),
        sf.Vector2(rect.right, rect.bottom),
      )
      intersection = get_line_intersection(translation_line, rect_line)
      collision = Response(intersection, "right")

    if translation.y > 0: # Top
      rect_line = (
        sf.Vector2(rect.left, rect.top),
        sf.Vector2(rect.right, rect.top),
      )
      intersection = get_line_intersection(translation_line, rect_line)
      use = True

      if collision is not None:
        other_distance = vector_length(collision.position - circle_position)
        my_distance = vector_length(intersection - circle_position)

        if my_distance > other_distance:
          use = False

      if use is True:
        collision = Response(intersection, "top")

    elif translation.y < 0: # Bottom
      rect_line = (
        sf.Vector2(rect.left, rect.bottom),
        sf.Vector2(rect.right, rect.bottom),
      )
      intersection = get_line_intersection(translation_line, rect_line)
      use = True

      if collision is not None:
        other_distance = vector_length(collision.position - circle_position)
        my_distance = vector_length(intersection - circle_position)

        if my_distance > other_distance:
          use = False

      if use is True:
        collision = Response(intersection, "bottom")

  return collision

def create_shadow(shape, distance=3):
  if type(shape) is sf.RectangleShape:
    shadow = sf.RectangleShape(shape.global_bounds.size)
  elif type(shape) is sf.CircleShape:
    shadow = sf.CircleShape(shape.radius)
  else:
    assert(False and "Invalid shape type.")

  shadow.position = shape.position + sf.Vector2(distance, distance)
  shadow.origin = shape.origin
  shadow.fill_color = sf.Color(0, 0, 0, 50)

  return shadow

def load_bricks(path, size, brick_type_pool, brick_size, gap_width,):
  with open(path, "r") as f:
    lines = f.read().splitlines()

  if len(lines) != size.y:
    raise RuntimeError(
      "Row count must be " + str(size.y) + ", is " + str(len(lines))
    )

  bricks = []

  for row_idx, line in enumerate(lines):
    if len(line) != size.x:
      raise RuntimeError(
        "Column count must be " + str(size.x) + ". At row: " +
        str(row_idx)
      )

    for col_idx, brick_type in enumerate(line):
      if brick_type < "0" or brick_type > "9":
        raise RuntimeError("Invalid brick type: " + brick_type)

      int_brick_type = int(brick_type)
      if int_brick_type not in brick_type_pool:
        raise RuntimeError("Brick type not in pool: " + brick_type)

      brick = sf.RectangleShape(brick_size)
      brick.fill_color = brick_type_pool[int_brick_type]
      brick.origin = brick.size / 2
      brick.position = sf.Vector2(
        (col_idx * (brick_size.x + gap_width)) + brick.origin.x,
        (row_idx * (brick_size.y + gap_width)) + brick.origin.y,
      )
      bricks.append(brick)

  return bricks

window = sf.RenderWindow(sf.VideoMode(1024, 768), "Tankoid (Python)", 0)
run = True

# Load bricks and center them.
bricks = load_bricks(
  "resources/levels/0000.lvl", LEVEL_SIZE, BRICK_TYPES, BRICK_SIZE,
  BRICK_GAP_WIDTH
)

shift = sf.Vector2(
  (
    window.size.x / 2 -
    LEVEL_SIZE.x / 2 * (BRICK_SIZE.x + BRICK_GAP_WIDTH) +
    BRICK_GAP_WIDTH / 2
  ),
  50
)

for brick in bricks:
  brick.position += shift

del shift

paddle = sf.RectangleShape(PADDLE_SIZE)
paddle.fill_color = PADDLE_COLOR
paddle.origin = paddle.size / 2
paddle.position = sf.Vector2(
  (window.size.x / 2) + paddle.origin.x - (paddle.size.x / 2),
  window.size.y - (paddle.size.y - paddle.origin.y) - 20,
)

ball = sf.CircleShape(BALL_RADIUS)
ball.origin = ball.global_bounds.size / 2
ball.fill_color = BALL_COLOR
ball.position = paddle.position - sf.Vector2(0, paddle.size.y)

ball_velocity = sf.Vector2(0, 0)
ball_attached_to_paddle = True

# Create border collision shapes.
left_border = sf.Rectangle((-500, -500), (500, 500 + window.size.y))
right_border = sf.Rectangle((window.size.x, -500), (500, 500 + window.size.y))
top_border = sf.Rectangle((-500, -500), (500 + window.size.x, 500))
bottom_border = sf.Rectangle((-500, window.size.y), (500 + window.size.x, 500))
borders = (left_border, right_border, top_border, bottom_border)

frame_timer = sf.Clock()

while run is True:
  for event in window.events:
    if type(event) is sf.KeyEvent:
      if event.code == sf.Keyboard.ESCAPE:
        run = False

      elif event.code == sf.Keyboard.SPACE:
        if ball_attached_to_paddle is True:
          ball_attached_to_paddle = False
          ball_velocity = normalized_vector(sf.Vector2(1, -1)) * BALL_SPEED

  frametime = frame_timer.restart()

  # Paddle velocity.
  move_left = (
    sf.Keyboard.is_key_pressed(sf.Keyboard.LEFT) |
    sf.Keyboard.is_key_pressed(sf.Keyboard.A)
  )
  move_right = (
    sf.Keyboard.is_key_pressed(sf.Keyboard.RIGHT) |
    sf.Keyboard.is_key_pressed(sf.Keyboard.D)
  )
  paddle_velocity = sf.Vector2((move_left and -1) + (move_right and 1), 0)
  paddle_velocity *= PADDLE_SPEED
  paddle.position += paddle_velocity * frametime.seconds

  if ball_attached_to_paddle is True:
    ball.position = paddle.position - sf.Vector2(0, paddle.size.y)
  else:
    ball_translation = ball_velocity * frametime.seconds
    new_ball_position = ball.position + ball_translation

    # Collision test & response.
    for border in borders:
      collision = test_circle_rect_collision(
        new_ball_position, BALL_RADIUS, border, ball_translation
      )

      if collision is not None:
        translation_direction = normalized_vector(ball_translation)
        max_distance = max(
          abs(BALL_RADIUS / translation_direction.x),
          abs(BALL_RADIUS / translation_direction.y),
        )
        new_ball_position = (
          collision.position - translation_direction * max_distance
        )

        if collision.side == "left":
          ball_velocity = sf.Vector2(-abs(ball_velocity.x), ball_velocity.y)
        elif collision.side == "bottom":
          ball_velocity = sf.Vector2(ball_velocity.x, abs(ball_velocity.y))
        elif collision.side == "right":
          ball_velocity = sf.Vector2(abs(ball_velocity.x), ball_velocity.y)
        elif collision.side == "top":
          ball_velocity = sf.Vector2(ball_velocity.x, -abs(ball_velocity.y))

        break # No more tests.

    ball.position = new_ball_position

  window.clear(CLEAR_COLOR)

  for brick in bricks:
    window.draw(create_shadow(brick))
    window.draw(brick)

  window.draw(create_shadow(paddle))
  window.draw(paddle)

  window.draw(create_shadow(ball))
  window.draw(ball)

  window.display()
