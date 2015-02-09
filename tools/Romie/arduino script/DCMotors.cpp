#include <Arduino.h>
#include "DCMotors.h"

// Specifies the control pins for the motors.
int PWMleft = 5;
int DIRleft = 4;
int PWMright = 6;
int DIRright = 7;

void DCMotors::setup()
{
  pinMode(PWMleft,OUTPUT);  
  pinMode(PWMright,OUTPUT);
  pinMode(DIRleft,OUTPUT);
  pinMode(DIRright,OUTPUT);
  	
  digitalWrite(DIRleft,LOW);
  digitalWrite(DIRright,LOW);      
  analogWrite(PWMleft,0);
  analogWrite(PWMright,0);
}

void DCMotors::stop()
{
  digitalWrite(DIRleft,LOW);
  digitalWrite(DIRright,LOW);      
  analogWrite(PWMleft,0);
  analogWrite(PWMright,0);
}

void DCMotors::shiftRight(int percent)
{
  digitalWrite(DIRleft,HIGH);
  digitalWrite(DIRright,HIGH);      
  analogWrite(PWMleft,(int)(percent*255/100));
  analogWrite(PWMright,0);
}

void DCMotors::shiftLeft(int percent)
{
  digitalWrite(DIRleft,HIGH);
  digitalWrite(DIRright,HIGH);      
  analogWrite(PWMleft,0);
  analogWrite(PWMright,(int)(percent*255/100));
}

void DCMotors::turnRight(int percent)
{
  digitalWrite(DIRleft,HIGH);
  digitalWrite(DIRright,LOW);      
  analogWrite(PWMleft,(int)(percent*255/100));
  analogWrite(PWMright,(int)(percent*255/100));
}

void DCMotors::turnLeft(int percent)
{
  digitalWrite(DIRleft,LOW);
  digitalWrite(DIRright,HIGH);      
  analogWrite(PWMleft,(int)(percent*255/100));
  analogWrite(PWMright,(int)(percent*255/100));
}

void DCMotors::forward(int percent)
{
  digitalWrite(DIRleft,HIGH);
  digitalWrite(DIRright,HIGH);      
  analogWrite(PWMleft,(int)(percent*255/100));
  analogWrite(PWMright,(int)(percent*255/100));
}

void DCMotors::backward(int percent)
{
  digitalWrite(DIRleft,LOW);
  digitalWrite(DIRright,LOW);      
  analogWrite(PWMleft,(int)(percent*255/100));
  analogWrite(PWMright,(int)(percent*255/100));
}
