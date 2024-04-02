// Arduino sampling with interrupt for WWEmg game
// Include the TimerOne library for Timer1 operations
#include <TimerOne.h>

#define READING_FREQ 1000   // Timer triggers every 1000 microseconds (1ms) - means 10kHz

int analogPin = 0;

const int bufferSize = 100;
int buffer[bufferSize];
int bufferIndex = 0;
int bufferSum = 0;

int calibTime = 400;
int calibCount = 0;
long computedAverage = 0;
bool average = false;

void setup() {

  Serial.begin(115200);  //  setup serial with high baud rate
  for (int i = 0; i < bufferSize; i++) {
    buffer[i] = 0;
  }

  // Set up Timer1 to trigger interrupt:
  Timer1.initialize(READING_FREQ);
  Timer1.attachInterrupt(timerISR); // Define the ISR function
}

void loop() {

}  // Void Loop

// interrupt func to read in every 1 ms
void timerISR() {
  // at every interrupt read in the analog value and safe it into an array:
  // compute the mean noise value for the contraction - calibration period
  // sum up the values and divide by the past time in the end
  if (average
        == false) {
      int emgData = analogRead(analogPin);
      computedAverage += emgData;
      calibCount++;
    } else {
      // after calibration calculate the smoothed contraction value
      // Read EMG data: data-period
      int emgData = analogRead(analogPin);

      // Update circular buffer and sum, sum is divide by 100 in python to get the value for that 
      // sum for moving average  
      int contractionValue = abs(emgData - computedAverage);
      bufferSum -= buffer[bufferIndex];
      buffer[bufferIndex] = contractionValue;
      bufferSum += contractionValue;
      //print
      if( 0 == (bufferIndex % 10)){
        Serial.println(bufferSum);
      }
    }

    // break for calibration period
    if (calibCount
        == calibTime) {
      average = true;
      computedAverage = computedAverage / calibTime;
      calibCount++;
      Serial.println(computedAverage);
    }  
    // iterate through buffer circulary
    bufferIndex = (bufferIndex + 1) % bufferSize;
 
}
