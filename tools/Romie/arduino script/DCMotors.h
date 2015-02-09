#ifndef DCMotors_h
#define DCMotors_h
#include <Arduino.h>

// Control class for DC motors.
class DCMotors
{
  public:
  
  void setup();                  // Prepares the motors for use by initializing the correct pins. Should be called in setup() before the program itself
  void stop();                   // Stops the motors.
  void shiftRight(int percent);  // Turns the robot right while advancing at the specified percentage of maximum power.
  void shiftLeft(int percent);   // Turns the robot left while advancing at the specified percentage of maximum power.
  void turnRight(int percent);   // Turns the robot right over itself at the specified percentage of maximum power.
  void turnLeft(int percent);    // Turns the robot left over itself at the specified percentage of maximum power.
  void forward(int percent);     // Advances at the specified percentage of maximum power.
  void backward(int percent);    // Moves backward at the specified percentage of maximum power.
};

#endif
