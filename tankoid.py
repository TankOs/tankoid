#!/usr/bin/python3.4

from sfml import sf

from collections import namedtuple
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
BALL_SPEED = 600.0
FRAMERATE_LIMIT = 100

Response = namedtuple("Response", ("position", "side"))

def vector_length(vector):
  return math.sqrt(vector.x * vector.x + vector.y * vector.y)

def normalized_vector(vector):
  return vector / vector_length(vector)

def test_rect_rect_collision(source_rect, target_rect, translation):
  collision = None

  translated_rect = sf.Rectangle(
    source_rect.position + translation, source_rect.size
  )
  intersection = translated_rect.intersects(target_rect)

  if intersection is not None:
    norm_translation = normalized_vector(translation)

    if intersection.width < intersection.height:
      pullback_vector = sf.Vector2(
        intersection.width * math.copysign(1, norm_translation.x),
        intersection.width * norm_translation.y,
      )
      position = source_rect.center + (translation - pullback_vector)

      if translation.x < 0:
        collision = Response(position, "right")
      elif translation.x > 0:
        collision = Response(position, "left")
    else:
      pullback_vector = sf.Vector2(
        intersection.height * norm_translation.x,
        intersection.height * math.copysign(1, norm_translation.y),
      )
      position = source_rect.center + (translation - pullback_vector)

      if translation.y < 0:
        collision = Response(position, "bottom")
      elif translation.y > 0:
        collision = Response(position, "top")

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
      brick.outline_thickness = 1
      brick.outline_color = sf.Color(0, 0, 0, 70)
      brick.fill_color = brick_type_pool[int_brick_type]
      brick.origin = brick.size / 2
      brick.position = sf.Vector2(
        (col_idx * (brick_size.x + gap_width)) + brick.origin.x,
        (row_idx * (brick_size.y + gap_width)) + brick.origin.y,
      )
      bricks.append(brick)

  return bricks

window = sf.RenderWindow(sf.VideoMode(1024, 768), "Tankoid (Python)", 0)
window.framerate_limit = FRAMERATE_LIMIT
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
left_border = sf.Rectangle((-500, -500), (500, 1000 + window.size.y))
right_border = sf.Rectangle((window.size.x, -500), (500, 1000 + window.size.y))
top_border = sf.Rectangle((-500, -500), (1000 + window.size.x, 500))
bottom_border = sf.Rectangle(
  (-500, window.size.y), (1000 + window.size.x, 500)
)
borders = (left_border, right_border, top_border, bottom_border)

frame_timer = sf.Clock()
app_timer = sf.Clock()

while run is True:
  for event in window.events:
    if type(event) is sf.KeyEvent:
      if event.code == sf.Keyboard.ESCAPE:
        run = False

      elif event.code == sf.Keyboard.SPACE:
        if ball_attached_to_paddle is True:
          ball_attached_to_paddle = False
          ball_velocity = normalized_vector(sf.Vector2(1, -1)) * BALL_SPEED

      elif event.code == sf.Keyboard.NUM2:
        ball_velocity *= 2

      elif event.code == sf.Keyboard.NUM1:
        ball_velocity /= 2;

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
    collisions = []

    # Border collision test.
    ball_box = sf.Rectangle(
      (ball.position.x - BALL_RADIUS, ball.position.y - BALL_RADIUS),
      (2*BALL_RADIUS, 2 * BALL_RADIUS),
    )

    for border in borders:
      collision = test_rect_rect_collision(ball_box, border, ball_translation)
      if collision is not None:
        collisions.append(collision)

    # Bricks collision test.
    for brick_idx, brick in enumerate(bricks):
      collision = test_rect_rect_collision(
        ball_box, brick.global_bounds, ball_translation
      )
      if collision is not None:
        collisions.append(collision)

    # Choose nearest collision.
    nearest_collision = None
    nearest_distance = None

    for collision in collisions:
      distance = vector_length(collision.position - ball.position)

      if nearest_collision is None or distance < nearest_distance:
        nearest_collision = collision
        nearest_distance = distance

    # Collision response.
    if nearest_collision is not None:
      # Set ball position to collision position.
      new_ball_position = nearest_collision.position

      # Inverse velocity component.
      if nearest_collision.side == "left" or nearest_collision.side == "right":
        ball_velocity.x *= -1
      elif (
        nearest_collision.side == "top" or nearest_collision.side == "bottom"
      ):
        ball_velocity.y *= -1

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
