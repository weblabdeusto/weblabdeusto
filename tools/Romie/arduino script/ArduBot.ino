#include "IOpins.h"
#include "DCMotors.h"
#include <SoftwareSerial.h>

void FollowLine(void);     // Follows a black line using 2 IR sensors.
char ReceiveCommand(void); // Receives and processes Bluetooth commands over a serial interface.
void ReadTag(void);        // Reads RFID tags using software serial.

// Initializes control variables
boolean detect=false;
char next=NULL;

// Instantiates the Software Serial emulation used by the RFID sensor.
SoftwareSerial swSerial=SoftwareSerial(rxPin, txPin); // RX, TX

// Instantiates the motors.
DCMotors Motors;

//--------------------------------------------------------------------------
//-- Defines input and output pins and general port configuration options --
//--------------------------------------------------------------------------
void setup()
{
  //Initializes the Pins specified in IOpins.h
  pinMode(FLIline,INPUT);
  pinMode(FRIline,INPUT);
  pinMode(MLline,INPUT);
  pinMode(MRline,INPUT);
  pinMode(Wall,INPUT);
  digitalWrite(Wall,HIGH);  //Use internal Pull-up resistor
  pinMode(rxPin,INPUT);
  pinMode(txPin,OUTPUT);

  // Starts the serial port at 9600 baud.
  Serial.begin(9600);

  // Starts the software serial port emulation at 9600 baud and clears the buffer.
  swSerial.begin(9600);
  while(swSerial.read()>=0);

  // Initializes the motors.
  Motors.setup();
}

//------------------------
//-- MAIN ROBOT PROGRAM --
//------------------------
void loop()
{
  // Follows a line until the robot reaches an intersection.
  FollowLine();
  if(digitalRead(MRline)==HIGH && digitalRead(MLline)==HIGH)
  { 
    // When an intersection is reached, the robot stops, attempts to read an RFID tag, and sends an "ACK" signal.
    Motors.stop();
    ReadTag();
    Serial.print("ACK");
    Serial.println();
    Serial.flush();
    
    // Enters a loop for command reception and processing unless the command is "F": Forward.
    do
    {  
      /*
      Serial.print("Awaiting Command...");
      Serial.println();
      */
      
      // Waits until a new Bluetooth command is received.
      do
      {
        next=ReceiveCommand(); 
      }
      while(next==NULL);

      // Processes Bluetooth commands.
      switch(next)
      {
      case 'F': // The command is "F": Forward 
        // If a wall is in the way, the robot stops and sends an "NAK" signal.
        if(digitalRead(Wall)==LOW)
        {
          Serial.print("NAK");
          Serial.println();
          Serial.flush();
          /*
          Serial.print("Obstacle in the way. Cannot move Forward.");
          Serial.println();
          */
          Motors.stop(); 
          next=NULL;
        }
        // If there is no wall, the robot advances (until the next intersection).
        else
        {
          //Serial.print("Command received: Move Forward");
          //Serial.println();
          Motors.forward(100);
          delay(300);
        }                  
        break;

      case 'R': // The command is "R": Right
        /*
        Serial.print("Command received: Turn Right");
        Serial.println();
        */
        //The robot turns right until a new intersection is reached and sends an "ACK".
        Motors.turnRight(100);
        while(digitalRead(FLIline)==HIGH);
        while(digitalRead(FRIline)==LOW || digitalRead(FLIline)==LOW);
        Motors.stop();
        Serial.print("ACK");
        Serial.println();
        Serial.flush();
        break;

      case 'L': // The command is "L": Left    
        /*
        Serial.print("Command received: Turn Left");
        Serial.println();
        */
        //The robot turns left until a new intersection is reached and sends an "ACK".
        Motors.turnLeft(100);
        while(digitalRead(FRIline)==HIGH);
        while(digitalRead(FRIline)==LOW || digitalRead(FLIline)==LOW);
        Motors.stop();
        Serial.print("ACK");
        Serial.println();
        Serial.flush();
        break;
        
      case 'S': // The commmand is "S": Read Wall Sensor    
        // Checks if there is a wall or not. If there is, it sends "True" over BT. Otherwise, it sends "False". 
        detect=!digitalRead(Wall); //Inverts the value of the sensor because the sensor is logic-low active, but blockly expects a "True" if there is a wall.
        Motors.stop();
        Serial.print(detect);
        Serial.println();
        Serial.flush();
        break;

      default:  // If the command is not recognized, the robot stops. 
        Motors.stop();
        Serial.print("NAK");
        Serial.println();
        Serial.flush();
        break;
      }
    }
    while(next!='F');
  }
}

//------------------------------------------------------
//-- Steers the robot in order to follow a black line --
//------------------------------------------------------
void FollowLine()
{ 
  if(digitalRead(FRIline)==HIGH && digitalRead(FLIline)==HIGH)     //Si el robot está centrado ...
    Motors.forward(100);     
  else if(digitalRead(FRIline)==LOW  && digitalRead(FLIline)==HIGH) //Si se ha salido por la dcha ...
    Motors.shiftLeft(50);     
  else if(digitalRead(FLIline)==LOW  && digitalRead(FRIline)==HIGH) //Si se ha salido por la izda ...
    Motors.shiftRight(50);     
}

//----------------------------------------------------------------
//-- Receives the next BlueTooth command from the WebLab Server --
//----------------------------------------------------------------
char ReceiveCommand()          
{
  char BTcommand;

  if (Serial.available() > 0)
    BTcommand=Serial.read();  
  else 
    BTcommand=NULL;

  return BTcommand;
}

//-----------------------
//-- Reads an RFID tag --
//-----------------------
void ReadTag()          
{
  byte i = 0;
  byte val = 0;
  byte code[6];
  byte checksum = 0;
  byte bytesread = 0;
  byte tempbyte = 0;

  if(swSerial.available() > 0 )
    if((val = swSerial.read()) == 2) {                  // check for header 
      bytesread = 0; 
      while (bytesread < 12) {                        // read 10 digit code + 2 digit checksum
        if( swSerial.available() > 0) { 
          val = swSerial.read();
          if((val == 0x0D)||(val == 0x0A)||(val == 0x03)||(val == 0x02)) { // if header or stop bytes before the 10 digit reading 
            break;                                    // stop reading
          }
  
          // Do Ascii/Hex conversion:
          if ((val >= '0') && (val <= '9')) {
            val = val - '0';
          } 
          else if ((val >= 'A') && (val <= 'F')) {
            val = 10 + val - 'A';
          }
  
          // Every two hex-digits, add byte to code:
          if (bytesread & 1 == 1) {
            // make some space for this hex-digit by
            // shifting the previous hex-digit with 4 bits to the left:
            code[bytesread >> 1] = (val | (tempbyte << 4));
  
            if (bytesread >> 1 != 5) {                // If we're at the checksum byte,
              checksum ^= code[bytesread >> 1];       // Calculate the checksum... (XOR)
            };
          } 
          else {
            tempbyte = val;                           // Store the first hex digit first...
          };
  
          bytesread++;                                // ready to read next digit
        } 
      } 
  
      // Output to Serial:
  
      if (bytesread == 12)                          // if 12 digit read is complete
        if(code[5] == checksum)
        {
          Serial.print("Tag: ");
          Serial.flush();
          for (i=0; i<5; i++) 
          {
            if (code[i] < 16)
           { 
              Serial.print("0");
              Serial.flush();
           }
            Serial.print(code[i], HEX);
            Serial.flush();
            Serial.print(" ");
            Serial.flush();
          }
          Serial.println();
          Serial.flush();          
        }
        else
        {
          Serial.print("Tag Error");
          Serial.println();
          Serial.flush();
        }
      bytesread = 0;
    }
    else
    {
      while(swSerial.read()>=0);
    }

  return;
}




