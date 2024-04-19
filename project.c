int LED_PIN_MOTION = 9;   // Pin for motion LED
int LED_PIN_SOUND = 10;   // Pin for sound LED

void setup() {
  pinMode(LED_PIN_MOTION, OUTPUT);
  pinMode(LED_PIN_SOUND, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char signal = Serial.read();
    if (signal == '1') {
      digitalWrite(LED_PIN_MOTION, HIGH); // Turn on motion LED
    } else if (signal == '0') {
      digitalWrite(LED_PIN_MOTION, LOW); // Turn off motion LED
    } else if (signal == '2') {
      digitalWrite(LED_PIN_SOUND, HIGH); // Turn on sound LED
    } else if (signal == '3') {
      digitalWrite(LED_PIN_SOUND, LOW); // Turn off sound LED
    }
  }
}