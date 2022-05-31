// Motor definitions
#define M1_PWM 5
#define M1_DIR 4
#define M2_PWM 6
#define M2_DIR 7

#define WATCHDOG_PERIOD_MS 500

#define BUF_SIZE 1024


static struct rover_t {
  byte cmd[BUF_SIZE];
  unsigned long watchdog_time;
} rover;


static void apply_command(int8_t left, int8_t right) {
  digitalWrite(M1_DIR, left < 0);
  digitalWrite(M2_DIR, right >= 0);
  analogWrite(M1_PWM, abs(left));
  analogWrite(M2_PWM, abs(right));
  Serial.print("Left: ");
  Serial.print(left);
  Serial.print(", right: ");
  Serial.println(right);
}


void setup() {
  rover.watchdog_time = 0;
  Serial.begin(9600);
  Serial.println("Arduino code started...");
}

void loop() {
  // Read serial data
  byte left, right;
  int n = Serial.available();
  if (n > 3) {
    if (n > 512) n = 512;
    n = Serial.readBytes(rover.cmd, n);
    // Find latest stop byte
    byte *p = rover.cmd + n - 1;
    while (p >= rover.cmd + 2) {
      if (*p == 0x80) {
        // Stop byte found
        Serial.println("Stop byte found");
        left = *(p - 2);
        right = *(p - 1);
        Serial.println(left);
        apply_command(left, right);
        rover.watchdog_time = millis() + WATCHDOG_PERIOD_MS;
      }
    }
  }
  // Check watchdog timer
  if (millis() > rover.watchdog_time) {
    apply_command(0, 0);
    Serial.println("Watchdog time exceeded!");
  }
  Serial.flush();
}
