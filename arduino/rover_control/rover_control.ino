// Motor definitions
#define M1_PWM 5
#define M1_DIR 4
#define M2_PWM 6
#define M2_DIR 7

#define WATCHDOG_PERIOD_MS 500

#define BUF_SIZE 10


static struct rover_t {
  int cmd[BUF_SIZE];
  int *cmd_ptr;
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


static bool command_valid(void) {
  // Validate length
  return rover.cmd_ptr - rover.cmd == 2;
}


static void serial_in_flush(void) {
  while(Serial.available()) Serial.read();
}


void setup() {
  rover.cmd_ptr = rover.cmd;
  rover.watchdog_time = millis() + WATCHDOG_PERIOD_MS;
  Serial.begin(9600);
  Serial.println("Arduino code started...");
}

void loop() {
  // Read serial data
  while (Serial.available()) {
    int in = Serial.read();  // int: -1 or byte value (unsigned I assume?)
    if (in < 0) break;
    if (in == 0x80) {
      // Start/stop byte
      if (command_valid()) {
        apply_command(rover.cmd[0], rover.cmd[1]);
        rover.watchdog_time = millis() + WATCHDOG_PERIOD_MS;
      } else {
        Serial.print("Invalid command: ");
        for (int* p = rover.cmd; p < rover.cmd_ptr; p++) {
          Serial.print(*p);
        }
        Serial.println();
      }
      // Reset buffer
      rover.cmd_ptr = rover.cmd;
      serial_in_flush();
    } else if (rover.cmd_ptr < rover.cmd + BUF_SIZE) {
      *rover.cmd_ptr = in;
      rover.cmd_ptr++;
    }
  }
  // Check watchdog timer
  if (millis() > rover.watchdog_time) {
    apply_command(0, 0);
    Serial.println("Watchdog time exceeded!");
  }
  Serial.println("Arduino code running...");
  Serial.flush();
}
