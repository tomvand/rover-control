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


static void apply_command(int left, int right) {
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
  int n = Serial.available();
  if (n > 0) {
    if (n > 512) n = 512;
    n = Serial.readBytes(rover.cmd, n);
    // Read command from *latest* byte
    byte cmd = rover.cmd[n - 1];
    uint8_t left_val = (cmd & 0x70) >> 4;
    uint8_t right_val = (cmd & 0x07);
    bool left_sign = (cmd & 0x80);
    bool right_sign = (cmd & 0x08);
    int left = (left_sign ? -1 : 1) * (int)left_val;
    int right = (right_sign ? -1 : 1) * (int)right_val;
    apply_command(left, right);
    rover.watchdog_time = millis() + WATCHDOG_PERIOD_MS;
  }
  // Check watchdog timer
  if (millis() > rover.watchdog_time) {
    apply_command(0, 0);
    Serial.println("Watchdog time exceeded!");
  }
  Serial.flush();
}
