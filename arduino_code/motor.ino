#define STEP 6
#define DIR 5
#define DISABLE 7

#define ROT_PER_SEC 2.5
#define STEP_PER_ROT 100
#define USEC_PER_STEP_2 (1000000UL/(ROT_PER_SEC * STEP_PER_ROT * 2))

static inline void step() {
  digitalWrite(STEP, 1);
  delayMicroseconds(USEC_PER_STEP_2);
  digitalWrite(STEP, 0);
  delayMicroseconds(USEC_PER_STEP_2);  
}

static inline void steps(int8_t n) {
  if(n < 0) {
    n = -n;
    digitalWrite(DIR, 1);
  } else {
    digitalWrite(DIR, 0);
  }
  
  while(n--) {
    step();
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(STEP, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(DISABLE, OUTPUT);
  
  digitalWrite(DISABLE, 1);
  
  Serial.write("Ready.\r\n");
}

int r = 0;

void loop() {
  if(Serial.available()) {
    int c = Serial.read();
    if(c == '.') {
      r = 0;
      step();
    }
    if(c >= '0' && c <= '9') {
      r = r * 10 + c - '0';
    }
    if(c == '\r') {
      while(r > 0) {
        digitalWrite(DISABLE, 0);
        delay(50);
        steps(STEP_PER_ROT*5/8);
        delay(10);
        steps(-STEP_PER_ROT/2);
        delay(10);
        steps(STEP_PER_ROT/8);
        delay(10);
        steps(-STEP_PER_ROT/2-STEP_PER_ROT/8);
        delay(50);
        steps(STEP_PER_ROT-STEP_PER_ROT*5/8);
        delay(100);
        
        steps(-STEP_PER_ROT*3/8);
        delay(50);
        steps(STEP_PER_ROT);
        delay(50);
        steps(-STEP_PER_ROT+STEP_PER_ROT*3/8);
        
        r--;
      }
      delay(500);
      digitalWrite(DISABLE, 1);
      r = 0;
    }
    
    if(c != '\n') {
      Serial.write(c);
      if(c == '\r') {
        Serial.write('\n');
      }
    }
  }
}
