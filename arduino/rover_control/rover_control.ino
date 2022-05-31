// Motor definitions
#define M1_PWM 5
#define M1_DIR 4
#define M2_PWM 6
#define M2_DIR 7

#define WATCHDOG_PERIOD_MS 500

#define BUF_SIZE 10


static struct rover_t {
  uint8_t cmd_u[BUF_SIZE];
  int8_t cmd[BUF_SIZE];
  unsigned long watchdog_time;
} rover;


static void apply_command(int8_t left, int8_t right) {
  digitalWrite(M1_DIR, left < 0);
  digitalWrite(M2_DIR, right >= 0);
  analogWrite(M1_PWM, abs(left));
  analogWrite(M2_PWM, abs(right));
}


void setup() {
  rover.watchdog_time = millis() + WATCHDOG_PERIOD_MS;
  Serial.begin(9600);
  Serial.println("Arduino code started...");
}

void loop() {
  // Check serial data available
  if (Serial.available() >= 3) {
    int n = Serial.readBytesUntil('\x80', rover.cmd_u, sizeof(rover.cmd_u));
    if (n == 2) {
      // Valid command
      memcpy(rover.cmd, rover.cmd_u, sizeof(rover.cmd));
      Serial.print("Left command: ");
      Serial.print(rover.cmd[0]);
      Serial.print(", right command: ");
      Serial.println(rover.cmd[1]);
      apply_command(rover.cmd[0], rover.cmd[1]);
      rover.watchdog_time = millis() + WATCHDOG_PERIOD_MS; 
    } else {
      // Invalid command length
      Serial.print("Invalid command length: ");
      Serial.println(n);
      Serial.println((char*)rover.cmd_u);
    }
  }
  if (millis() > rover.watchdog_time) {
    apply_command(0, 0);
    Serial.println("Watchdog time exceeded!");
  }
  Serial.println("Arduino code running...");
}
