#include <config.hpp>

#include <SFML/Graphics.hpp>

#include <iostream>
#include <fstream>
#include <exception>
#include <cmath>

namespace sf {
  using Vector2ui = Vector2<unsigned int>;
}

enum class GameState {
  START=0, NORMAL, DIE, WIN
};

struct CollisionResult {
  enum class Side {
    NONE, LEFT, RIGHT, BOTTOM, TOP
  };

  sf::Vector2f position = {0.0f, 0.0f};
  Side side = Side::NONE;
};

struct CollisionInfo {
  CollisionInfo(
    CollisionResult result_, const sf::RectangleShape* brick_=nullptr
  ) :
     brick(brick_), result(result_)
  {
  }

  const sf::RectangleShape* brick;
  CollisionResult result;
};

static const sf::VideoMode VIDEO_MODE = {1024, 768};
static const std::string WINDOW_TITLE = "Tankoid";
static const sf::Color CLEAR_COLOR = {0, 128, 128};
static const sf::Vector2f BRICK_SIZE = {50, 25};
//static const float BRICK_OUTLINE_THICKNESS = 1.0f;
static const float BRICK_GAP_WIDTH = 12.0f;
static const sf::Vector2ui LEVEL_SIZE = {10, 8};
static const sf::Vector2f PADDLE_SIZE = {140, 30};
static const sf::Color PADDLE_COLOR = sf::Color::White;
static const float PADDLE_SPEED(750.0f);
static const float BALL_RADIUS = 10.0f;
static const sf::Color BALL_COLOR = sf::Color::White;
static const float BALL_SPEED = 700.0;
static const std::vector<sf::Color> BRICK_TYPES = {
  sf::Color::Red, sf::Color::Blue, sf::Color::Green, sf::Color::White
};

template <class T>
constexpr T vector_length(const sf::Vector2<T>& vector) {
  return std::sqrt(vector.x * vector.x + vector.y + vector.y);
}

template <class T>
constexpr int sgn(T value) {
    return (T(0) < value) - (value < T(0));
}

template <class T>
sf::Vector2<T> normalized_vector(const sf::Vector2<T>& source) {
  return source / vector_length(source);
}

template <class T>
T create_shadow(const T& shape, float distance=3.0f) {
  T shadow(shape);
  shadow.move({distance, distance});
  shadow.setFillColor({0, 0, 0, 50});
  return shadow;
}

std::vector<sf::RectangleShape> load_bricks(
  const std::string& path, sf::Vector2ui level_size,
  const std::vector<sf::Color>& brick_type_pool,
  sf::Vector2f brick_size, float gap_width
) {
  std::ifstream in_stream(path.c_str());

  if(!in_stream.good()) {
    throw std::runtime_error("Failed opening bricks file: " + path);
  }

  std::string line;
  std::size_t row_idx = 0;
  std::vector<sf::RectangleShape> bricks;

  while(std::getline(in_stream, line)) {
    if(line.size() != level_size.x) {
      throw std::runtime_error(
        "Wrong column length in row " + std::to_string(row_idx + 1) + "."
      );
    }

    std::size_t column_idx = 0;

    for(; column_idx < level_size.x; ++column_idx) {
      char ch = line[column_idx];

      if(ch < '0' || ch > '9') {
        throw std::runtime_error(std::string("Invalid character: ") + ch);
      }

      uint8_t brick_idx = static_cast<uint8_t>(ch - '0');

      if(brick_idx >= brick_type_pool.size()) {
        throw std::runtime_error(
          "Brick index out of range: " + std::to_string(brick_idx)
        );
      }

      sf::RectangleShape brick(brick_size);
      brick.setPosition({
          column_idx * (brick_size.x + gap_width),
          row_idx * (brick_size.y + gap_width),
      });
      brick.setFillColor(brick_type_pool[brick_idx]);
      bricks.push_back(brick);
    }

    ++row_idx;
  }

  return bricks;
}

CollisionResult test_rect_rect_collision(
  const sf::FloatRect& source, const sf::FloatRect& target,
  const sf::Vector2f& translation
) {
  CollisionResult result;

  auto translated_rect = sf::FloatRect(
    source.left + translation.x, source.top + translation.y,
    source.width, source.height
  );
  sf::FloatRect intersection = {0.0f, 0.0f, 0.0f, 0.0f};

  auto intersects = translated_rect.intersects(target, intersection);

  if(intersects) {
    auto translation_normal = normalized_vector(translation);
    auto source_center = sf::Vector2f(
      source.left + source.width / 2,
      source.top + source.height / 2
    );

    if(intersection.width < intersection.height) {
      // Left or right collision.
      sf::Vector2f pullback_vector = {
        intersection.width * sgn(translation_normal.x),
        (
          (intersection.width * sgn(translation_normal.y)) *
          (translation_normal.x / translation_normal.y)
        )
      };
      result.position = source_center + (translation - pullback_vector);

      using CollisionResult::Side::RIGHT;
      using CollisionResult::Side::LEFT;
      result.side = translation.x < 0.0f ? RIGHT : LEFT;
    }
    else {
      // Top or bottom collision.
      sf::Vector2f pullback_vector = {
        (
          (intersection.height * sgn(translation_normal.x)) *
          (translation_normal.y / translation_normal.x)
        ),
        intersection.height * sgn(translation_normal.y)
      };
      result.position = source_center + (translation - pullback_vector);

      using CollisionResult::Side::TOP;
      using CollisionResult::Side::BOTTOM;
      result.side = translation.y < 0.0f ? BOTTOM : TOP;
    }
  }
  else {
    result.side = CollisionResult::Side::NONE;
    result.position = {source.left, source.top};
  }

  return std::move(result);
}

int main() {
  std::cout << "Resources path: " << RESOURCES_PATH << std::endl;

  sf::RenderWindow window = {VIDEO_MODE, WINDOW_TITLE, 0};
  window.setFramerateLimit(100);

  bool run = true;
  sf::Event event;

  // Setup bricks.
  auto bricks = load_bricks(
    RESOURCES_PATH + "/levels/0000.lvl", LEVEL_SIZE, BRICK_TYPES, BRICK_SIZE,
    BRICK_GAP_WIDTH
  );

  // Center bricks.
  {
    sf::Vector2f shift(
      (
        window.getSize().x / 2 -
        LEVEL_SIZE.x / 2 * (BRICK_SIZE.x + BRICK_GAP_WIDTH) +
        BRICK_GAP_WIDTH / 2
      ),
      50
    );

    for(auto& brick : bricks) {
      brick.move(shift);
    }
  }

  // Paddle.
  sf::RectangleShape paddle(PADDLE_SIZE);
  paddle.setFillColor(PADDLE_COLOR);
  paddle.setOrigin(PADDLE_SIZE / 2.0f);
  paddle.setPosition({
      (
        (window.getSize().x / 2) + paddle.getOrigin().x -
        (paddle.getSize().x / 2)
      ),
      window.getSize().y - (paddle.getSize().y - paddle.getOrigin().y) - 20
  });

  // Ball.
  sf::CircleShape ball(BALL_RADIUS);
  ball.setOrigin({BALL_RADIUS, BALL_RADIUS});
  ball.setFillColor(BALL_COLOR);
  ball.setPosition(paddle.getPosition() - sf::Vector2f(0, paddle.getSize().y));

  sf::Clock frame_clock;
  auto game_state = GameState::START;
  sf::Vector2f ball_velocity = {0.0f, 0.0f};

  // Borders.
  std::vector<sf::FloatRect> borders;

  borders.emplace_back( // Left.
    -500, 0,
    500, window.getSize().y
  );
  borders.emplace_back( // Right.
    window.getSize().x, 0,
    500, window.getSize().y
  );
  borders.emplace_back( // Top.
    0, -500,
    window.getSize().x, 500
  );
  borders.emplace_back( // Bottom.
    0, window.getSize().y,
    window.getSize().x, 500
  );

  while(run) {
    while(window.pollEvent(event)) {
      if(event.type == sf::Event::KeyPressed) {
        if(event.key.code == sf::Keyboard::Escape) {
          run = false;
        }
        else if(event.key.code == sf::Keyboard::Space) {
          if(game_state == GameState::START) {
            game_state = GameState::NORMAL;
            ball_velocity = sf::Vector2f(0.5f, -0.5f) * BALL_SPEED;
          }
        }
      }
    }

    auto frame_time = frame_clock.restart();
    auto frame_seconds = frame_time.asSeconds();

    if(game_state == GameState::START || game_state == GameState::NORMAL) {
      // Paddle movement.
      bool move_left = (
        sf::Keyboard::isKeyPressed(sf::Keyboard::Left) ||
        sf::Keyboard::isKeyPressed(sf::Keyboard::A)
      );
      bool move_right = (
        sf::Keyboard::isKeyPressed(sf::Keyboard::Right) ||
        sf::Keyboard::isKeyPressed(sf::Keyboard::D)
      );
      sf::Vector2f paddle_velocity = {
        (move_left ? -1.0f : 0.0f) + (move_right ? 1.0f : 0.0f),
        0.0f
      };

      paddle.move(paddle_velocity * PADDLE_SPEED * frame_seconds);
    }

    if(game_state == GameState::START) {
      // Make the ball follow the paddle.
      ball.setPosition(
        paddle.getPosition() - sf::Vector2f(0, paddle.getSize().y)
      );
    }
    else if(game_state == GameState::NORMAL) {
      using Side = CollisionResult::Side;

      sf::Vector2f ball_translation = ball_velocity * frame_seconds;
      sf::Vector2f new_position = ball.getPosition() + ball_translation;
      std::vector<CollisionInfo> collisions;

      // Paddle collision test.
      {
        auto collision = test_rect_rect_collision(
          ball.getGlobalBounds(), paddle.getGlobalBounds(), ball_translation
        );

        if(collision.side != Side::NONE) {
          collisions.emplace_back(collision);
        }
      }

      // Border collision test.
      for(const auto& border : borders) {
        auto collision = test_rect_rect_collision(
          ball.getGlobalBounds(), border, ball_translation
        );

        if(collision.side != Side::NONE) {
          collisions.emplace_back(collision);
        }
      }

      // Bricks collision tests.
      for(const auto& brick : bricks) {
        auto collision = test_rect_rect_collision(
          ball.getGlobalBounds(), brick.getGlobalBounds(), ball_translation
        );

        if(collision.side != Side::NONE) {
          collisions.emplace_back(collision, &brick);
        }
      }

      // Choose nearest collision.
      const CollisionInfo* nearest_collision = nullptr;
      float nearest_distance = 0.0f;

      for(const auto& collision : collisions) {
        auto distance = vector_length(
          collision.result.position - ball.getPosition()
        );

        if(!nearest_collision || distance < nearest_distance) {
          nearest_distance = distance;
          nearest_collision = &collision;
        }
      }

      // Collision response.
      if(nearest_collision) {
        new_position = nearest_collision->result.position;

        // Inverse velocity.
        if(
          nearest_collision->result.side == Side::LEFT ||
          nearest_collision->result.side == Side::RIGHT
        ) {
          ball_velocity.x *= -1;
        }
        else if(
          nearest_collision->result.side == Side::TOP ||
          nearest_collision->result.side == Side::BOTTOM
        ) {
          ball_velocity.y *= -1;
        }

        // Remove brick.
        if(nearest_collision->brick) {
          for(std::size_t idx = 0; idx < bricks.size(); ++idx) {
            if(&bricks[idx] == nearest_collision->brick) {
              bricks.erase(
                std::begin(bricks) +
                static_cast<decltype(bricks)::difference_type>(idx)
              );
              break;
            }
          }
        }
      }

      ball.setPosition(new_position);
    }

    window.clear(CLEAR_COLOR);

    for(const auto& brick : bricks) {
      window.draw(create_shadow(brick));
      window.draw(brick);
    }

    window.draw(create_shadow(paddle));
    window.draw(paddle);
    window.draw(create_shadow(ball));
    window.draw(ball);

    window.display();
  }

  return 0;
}
