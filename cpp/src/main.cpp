#include <config.hpp>

#include <SFML/Graphics.hpp>

#include <iostream>

namespace sf {
  using Vector2ui = Vector2<unsigned int>;
}

static const sf::VideoMode VIDEO_MODE(1024, 768);
static const std::string WINDOW_TITLE = "Tankoid";
static const sf::Color CLEAR_COLOR(0, 128, 128);
static const sf::Vector2f BRICK_SIZE(50, 25);
static const float BRICK_OUTLINE_THICKNESS(1.0f);
static const float BRICK_GAP_WIDTH(12.0f);
static const sf::Vector2ui LEVEL_SIZE(10, 8);
static const sf::Vector2f PADDLE_SIZE(140, 30);
static const sf::Color PADDLE_COLOR(sf::Color::White);
//static const float PADDLE_SPEED(750.0f);
static const float BALL_RADIUS = 10.0f;
static const sf::Color BALL_COLOR(sf::Color::White);

int main() {
  std::cout << "Resources path: " << RESOURCES_PATH << std::endl;

  sf::RenderWindow window = {VIDEO_MODE, WINDOW_TITLE, 0};
  window.setFramerateLimit(100);

  bool run = true;
  sf::Event event;

  // Setup bricks.
  std::vector<sf::RectangleShape> bricks;

  {
    sf::RectangleShape shape(BRICK_SIZE);
    shape.setFillColor({255, 0, 0});
    shape.setOutlineThickness(BRICK_OUTLINE_THICKNESS);

    sf::Color outline_color(shape.getFillColor());
    outline_color.a = 80;
    shape.setOutlineColor(outline_color);

    for(unsigned int y = 0; y < LEVEL_SIZE.y; ++y) {
      for(unsigned int x = 0; x < LEVEL_SIZE.x; ++x) {
        shape.setPosition({
            x * (BRICK_SIZE.x + BRICK_GAP_WIDTH),
            y * (BRICK_SIZE.y + BRICK_GAP_WIDTH),
        });
        bricks.push_back(shape);
      }
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

  while(run) {
    while(window.pollEvent(event)) {
      if(event.type == sf::Event::KeyPressed) {
        run = false;
      }
    }

    window.clear(CLEAR_COLOR);

    for(const auto& brick : bricks) {
      window.draw(brick);
    }

    window.draw(paddle);
    window.draw(ball);

    window.display();
  }

  return 0;
}
