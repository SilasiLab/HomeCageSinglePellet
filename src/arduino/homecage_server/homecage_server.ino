#include <SoftwareSerial.h>
#include "Servo2.h"


// Config
const int servo1Pin = 10;
const int servo2Pin = 9;
int servo1Pos = -1;
int servo2Pos = -1;
typedef enum {left,right} whichServo;

const int ledPin = 13;
const int switchPin = 2;
const int IRBreakerPin = 3;
const int ptgreyGPIOSignalPin = A1;

volatile byte switchState;
volatile byte IRState;

SoftwareSerial mySerial(8,5); 
String RFID_String = "";
typedef enum {complete,wait,empty } RFID_Flag_t;
RFID_Flag_t RFID_Flag = empty;

int stepperDistFromOrigin = -1;
double stepsToMmRatio = 450;


// Hardware interrupt handler for switch pin
void handleSwitchChange() {

  switchState = digitalRead(switchPin);
}

// Hardware interrupt handler for IR breaker pin 
void handleIRChange() {

  IRState = digitalRead(IRBreakerPin);
  digitalWrite(ledPin,IRState);
}


int zeroServos() {

  Servo servo;

  // Lower servo1
  servo.attach(servo1Pin);
  for (int i = 5; i <= 100; i += 1) {
    servo.write(i);
    delay(5);
  }
  delay(50);
  servo1Pos = 100;
  servo.detach();

  // Lower servo2
  servo.attach(servo2Pin);
  for (int i = 180; i >= 55; i -= 1) {
    servo.write(i);
    delay(5);
  }
  delay(50);
  servo2Pos = 55;
  servo.detach();

   
}


int displayPellet(whichServo side) {

  Servo servo;
  int pin;
  int pos;
  
  if(side == left){
    
    pin = servo1Pin;
    pos = servo1Pos;

    // Lower arm to grab pellet.
    servo.attach(pin);
    for (int i = pos; i <= 100; i += 1) {
      servo.write(i);
      delay(5);
      pos += 1;
    }   

    // Raise arm to display pellet
    for (int i = pos; i >= 5; i -= 1) {
      servo.write(i);
      delay(5);
      pos -= 1;
    }

    servo1Pos = pos;
     
  }
  else if(side == right){
    pin = servo2Pin;
    pos = servo2Pos;

    // Lower arm to grab pellet.
    servo.attach(pin);
    for (int i = pos; i >= 55; i -= 1) {
      servo.write(i);
      delay(5);
      pos -= 1;
    }   

    // Raise arm to display pellet
    for (int i = pos; i <= 175; i += 1) {
      servo.write(i);
      delay(5);
      pos += 1;
    }

    servo2Pos = pos;
    
  }

  servo.detach(); 
  return 0;
}



int zeroStepper() {

  digitalWrite(A3, LOW);

  while(!switchState){

    digitalWrite(A4, HIGH);
    delay(1);
    digitalWrite(A4, LOW);
    delay(1);
  }

  stepperDistFromOrigin = 0;
  return 0;
}

int moveStepper(int targetPos) {

  int travelDist = targetPos - stepperDistFromOrigin;
  
  if(travelDist < 0){

    // If we try to move backwards but switch is pressed, set current position to origin and block movement.
    if(switchState){
      stepperDistFromOrigin = 0;
      return 2;
    }
    digitalWrite(A3, LOW);
  }
  else{

    digitalWrite(A3, HIGH);
  }
  
  int stepsToTake = abs(travelDist);
  int stepsTaken = 0;
  
  for(int i = 0; i < stepsToTake; i += 1){

    digitalWrite(A4, HIGH);
    delay(1);
    digitalWrite(A4, LOW);
    delay(1);

    if(travelDist < 0){
      
      stepperDistFromOrigin -= 1;    
    }
    else if(travelDist > 0){
      
      stepperDistFromOrigin += 1;
    }  
    stepsTaken += 1;

    // If we hit the limit switch after a short movement, we're at the origin and should abort. 
    if(stepsTaken > 1000 && switchState){

      stepperDistFromOrigin = 0;
      return 1;
    }
   
  }
  return 0;
}





void setup() {

  // Open serial connection
  // Note: This takes a bit to connect so while(!Serial) keeps it waiting
  // until the connection is ready.
  mySerial.begin(9600);
  Serial.begin(9600);
  while (!Serial) {
    delay(100);
  }

  zeroServos();
  
  // Set switch read pin
  pinMode(switchPin, INPUT);
  switchState = digitalRead(switchPin);
  attachInterrupt(digitalPinToInterrupt(switchPin), handleSwitchChange, CHANGE);
  zeroStepper();
  
  // Set IR breaker read pin
  pinMode(IRBreakerPin, INPUT_PULLUP);
  IRState = digitalRead(IRBreakerPin);
  attachInterrupt(digitalPinToInterrupt(IRBreakerPin), handleIRChange, HIGH);
  // Set LED control pin
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH);
  pinMode(ptgreyGPIOSignalPin, OUTPUT);
  digitalWrite(ptgreyGPIOSignalPin, HIGH);
  // Let client know we're ready
  Serial.write("READY\n");
}




void listenForRFID() {
 
 if (mySerial.available()) 
 {
  
  char A = mySerial.read();
  switch (A){
    case (0x02)  : {RFID_String="";RFID_Flag = empty;break;}
    case (0x03)  : {RFID_Flag = complete;break;}
    default:{  RFID_String +=(String)A; RFID_Flag = wait;}
  }
 }
 
}

bool authRFID() {

  Serial.print(RFID_String);
  
  char authByte;
  
  while(!IRState) {

    if(Serial.available() > 0) {
      
      authByte = Serial.read();
    }
    
    if(authByte == 'A') {
      
      return true;
    }
    else if (authByte == 'B' ) {
      
      return false;
    }

  }


  return false;
}



int startSession() {


  while(!IRState) {

    char cmd;
    char stepperDist;
    
    if(Serial.available() > 0) {

      cmd = Serial.read();
      
      switch(cmd){
        
        case ('1'):
          displayPellet(right);
          break;
          
        case ('2'):
          displayPellet(left);
          break;
          
        case ('3'):

          // Give client a second to respond
          delay(1000);
          stepperDist = Serial.read();
          
          switch(stepperDist){
            case('0'):
              moveStepper(0);
              break;
            case('1'):
              moveStepper(stepsToMmRatio * 1);
              break;
            case('2'):
              moveStepper(stepsToMmRatio * 2);
              break;
            case('3'):
              moveStepper(stepsToMmRatio * 3);
              break;
            case('4'):
              moveStepper(stepsToMmRatio * 4);
              break;
            case('5'):
              moveStepper(stepsToMmRatio * 5);
              break;
            case('6'):
              moveStepper(stepsToMmRatio * 6);
              break;
            default:
              break;  
            }
            
        default:
          break;
      }
    }
    
  }

  // Flush serial buffer.
  while(Serial.read() >= 0) {
    continue;
  }

  // Send session end message.
  Serial.write("TERM\n");
  return 0;
}



void loop() { 

  displayPellet(left);
  displayPellet(right);
 delay(5000);
  
  // If IR beam is broken, enter RFID listening state. 
  if(!IRState) {

      // Flush RFID serial buffer...serial.flush() not working...
      while(mySerial.read() >= 0) {
        continue;
      }
      
      while(RFID_Flag != complete && !IRState) {
         listenForRFID();     
      }

      if(RFID_Flag == complete) {

         // Ask client to authenticate RFID.
         if(authRFID()) {

            // If RFID authenticated, start session.
            startSession();          
         }
      }


      RFID_String = "";
      RFID_Flag = empty;
  }
}

 
