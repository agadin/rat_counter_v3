#include <FS.h>
#include <SD.h>
#include <SPI.h>

#include "RTClib.h"
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "esp_task_wdt.h"

// RTC instance
RTC_DS3231 rtc;


LiquidCrystal_I2C lcd(0x27, 20, 4);

// Sensor pins and file paths
const int sensorPins[] = {D3, D4, D5, D6, D7, D8, D9, 41};
const char* sensorFiles[] = {"/SENSOR1.TXT", "/SENSOR2.TXT", "/SENSOR3.TXT", "/SENSOR4.TXT",
                             "/SENSOR5.TXT", "/SENSOR6.TXT", "/SENSOR7.TXT", "/SENSOR8.TXT"};
const char* sensorLabels[] = {"A: ", "B: ", "C: ", "D: ", "E: ", "F: ", "G: ", "H: "};

volatile unsigned long sensorCounts[8] = {0};

// Queue to hold triggered sensors
#define QUEUE_SIZE 10
volatile int sensorQueue[QUEUE_SIZE];
volatile int queueHead = 0;
volatile int queueTail = 0;

unsigned long lastUpdateTime = 0; // Tracks the last update time
int displayMode = 0;             // Tracks the current display state

// Function to add to queue
void enqueueSensor(int sensorIndex) {
    int nextTail = (queueTail + 1) % QUEUE_SIZE;
    if (nextTail != queueHead) { // Ensure queue is not full
        sensorQueue[queueTail] = sensorIndex;
        queueTail = nextTail;
    } else {
        Serial.println("Queue full, dropping sensor event!");
    }
}

void initializeSensorCounts() {
    Serial.println("Initializing sensor counts...");

    for (int i = 0; i < 8; i++) {
        Serial.printf("Opening file: %s for Sensor %d (%s)\n", sensorFiles[i], i + 1, sensorLabels[i]);

        File file = SD.open(sensorFiles[i], FILE_READ);
        if (file) {
            Serial.printf("File %s opened successfully.\n", sensorFiles[i]);

            String lastLine = "";
            String currentLine = "";
            while (file.available()) {
                char c = file.read();
                if (c == '\n') {
                    if (!currentLine.isEmpty()) {
                        lastLine = currentLine; // Update last valid line
                        currentLine = "";       // Clear for the next line
                    }
                } else {
                    currentLine += c; // Build the current line
                }
            }

            // Handle the last line if it exists and wasn't terminated with '\n'
            if (!currentLine.isEmpty()) {
                Serial.printf("Read final line: %s\n", currentLine.c_str());
                lastLine = currentLine;
            }

            file.close();

            // Process the last line
            Serial.printf("Last line read: %s\n", lastLine.c_str());
            if (lastLine.length() > 0) {
                // Extract the 7th field (count) from the line
                int commaPos = -1;
                int prevCommaPos = -1;
                int fieldIndex = 0;

                for (int j = 0; j < lastLine.length(); j++) {
                    if (lastLine[j] == ',') {
                        fieldIndex++;
                        prevCommaPos = commaPos;
                        commaPos = j;

                        // Stop when the 7th field is found
                        if (fieldIndex == 7) {
                            break;
                        }
                    }
                }

                if (fieldIndex >= 7) {
                    String countString = lastLine.substring(prevCommaPos + 1, commaPos);
                    sensorCounts[i] = countString.toInt();
                    Serial.printf("Parsed count for Sensor %d: %s -> %lu\n", i + 1, countString.c_str(), sensorCounts[i]);
                } else {
                    Serial.printf("Could not find count in the last line for Sensor %d. Defaulting count to 0.\n", i + 1);
                    sensorCounts[i] = 0;
                }
            } else {
                Serial.printf("File for Sensor %d is empty. Defaulting count to 0.\n", i + 1);
                sensorCounts[i] = 0;
            }
        } else {
            Serial.printf("Failed to open file for Sensor %d (%s). Defaulting count to 0.\n", i + 1, sensorLabels[i]);
            sensorCounts[i] = 0; // Initialize to zero if no file exists
        }

        Serial.printf("Sensor %d (%s) initialized with count: %lu\n", i + 1, sensorLabels[i], sensorCounts[i]);
    }

    Serial.println("Sensor count initialization complete.");
}



// ISRs
void IRAM_ATTR sensorCallback0() { enqueueSensor(0); }
void IRAM_ATTR sensorCallback1() { enqueueSensor(1); }
void IRAM_ATTR sensorCallback2() { enqueueSensor(2); }
void IRAM_ATTR sensorCallback3() { enqueueSensor(3); }
void IRAM_ATTR sensorCallback4() { enqueueSensor(4); }
void IRAM_ATTR sensorCallback5() { enqueueSensor(5); }
void IRAM_ATTR sensorCallback6() { enqueueSensor(6); }
void IRAM_ATTR sensorCallback7() { enqueueSensor(7); }

// Initialize SD card
void initSDCard() {
    if (!SD.begin()) {
        Serial.println("Card Mount Failed");
        return;
    }
    uint8_t cardType = SD.cardType();
    if (cardType == CARD_NONE) {
        Serial.println("No SD card attached");
        return;
    }
    Serial.println("SD card initialized");
}

// init sensors

// Process a sensor event
void processSensorEvent(int sensorIndex) {
    Serial.println("before");
    DateTime now = rtc.now();
    Serial.println("triggered");
    String year = String(now.year(), DEC);
    String month = String(now.month(), DEC);
    String day = String(now.day(), DEC);
    String hour = String(now.hour(), DEC);
    String minute = String(now.minute(), DEC);
    String second = String(now.second(), DEC);

    // Increment the count for the sensor
    Serial.println("after");

    unsigned long currentCount = sensorCounts[sensorIndex];
    sensorCounts[sensorIndex] = currentCount + 1;
    
    String timestamp = String(now.year(), DEC) + "," + String(now.month(), DEC) + "," + String(now.day(), DEC) + "," +
                       String(now.hour(), DEC) + "," + String(now.minute(), DEC) + "," + String(now.second(), DEC);

    // Create the new message
    String newMessage = String(timestamp + "," + String(sensorCounts[sensorIndex]) + ",Sensor " + String(sensorIndex + 1) + "," + sensorLabels[sensorIndex] + "\n");
    
    Serial.println(newMessage);
    // Append the message to the file
    appendFile(SD, sensorFiles[sensorIndex], newMessage.c_str());
}

// Dequeue and process sensor events
void processQueue() {
    while (queueHead != queueTail) {
        int sensorIndex = sensorQueue[queueHead];
        queueHead = (queueHead + 1) % QUEUE_SIZE;
        processSensorEvent(sensorIndex);
    }
}

// Write to the SD card
void appendFile(fs::FS &fs, const char *path, const char *message) {
    File file = fs.open(path, FILE_APPEND);
    if (!file) {
        Serial.printf("Failed to open file %s for appending\n", path);
        return;
    }
    file.print(message);
    file.close();
}

void setup() {
    Serial.begin(115200);


    if (!rtc.begin()) {
        Serial.println("Couldn't find RTC");
        while (1);
    }

    if (rtc.lostPower()) {
        rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    }

    initSDCard();

    // Configure sensors and attach interrupts
    for (int i = 0; i < 8; i++) {
        pinMode(sensorPins[i], INPUT_PULLUP);
    }

    attachInterrupt(digitalPinToInterrupt(D3), sensorCallback0, FALLING);
    attachInterrupt(digitalPinToInterrupt(D4), sensorCallback1, FALLING);
    attachInterrupt(digitalPinToInterrupt(D5), sensorCallback2, FALLING);
    attachInterrupt(digitalPinToInterrupt(D6), sensorCallback3, FALLING);
    attachInterrupt(digitalPinToInterrupt(D7), sensorCallback4, FALLING);
    attachInterrupt(digitalPinToInterrupt(D8), sensorCallback5, FALLING);
    attachInterrupt(digitalPinToInterrupt(D9), sensorCallback6, FALLING);
    attachInterrupt(digitalPinToInterrupt(D41), sensorCallback7, FALLING);

    Serial.println("Setup complete. Intializing Counts...");
    initializeSensorCounts();

    //LCD init
    lcd.init();
    lcd.backlight();
    updateDisplay();

    // Watch Dog
    esp_task_wdt_config_t wdt_config = {
    .timeout_ms = 8000,  // 8 seconds timeout
    .idle_core_mask = 0, // WDT will monitor all cores
    .trigger_panic = true,
    };
    esp_task_wdt_init(&wdt_config);

    esp_task_wdt_add(NULL);     // Add current task to WDT
}

void logMessage(const String &message) {
  Serial.println(message);
  String log_name = "/log.txt";
  DateTime now = rtc.now();
  String year = String(now.year(), DEC);
  String month = String(now.month(), DEC);
  String day = String(now.day(), DEC);
  String hour = String(now.hour(), DEC);
  String minute = String(now.minute(), DEC);
  String second = String(now.second(), DEC);

  String new_message = String(month + "-" + day +"-" + year +"-" + hour +"-" + minute +"-" + second+ "," + message);  // we save the current date to a string so we can use it later to name our files.


  File file = SD.open(log_name.c_str() );  // here we are checking to see if the current date file already exist or not.
  if(!file) {
    Serial.println("File doesn't exist");// if it doesn't exist then we create a new file with the current date.
    Serial.println("Creating file...");
    writeFile(SD, log_name.c_str(), new_message.c_str()); // this is the header of the file. so the top of the file will have these labels.
    // and we will add our data for each item under this labels.
  }
  else {
    appendFile(SD, log_name.c_str(), new_message.c_str()); // if there is already a file with the current date then we append our new data to that file.

  }

}

void loop() {
    esp_task_wdt_reset();
    unsigned long currentMillis = millis();
    processQueue();
    // Update the display every 7 seconds for sensors, 3 seconds for time
    if (currentMillis - lastUpdateTime >= (displayMode == 2 ? 3000 : 7000)) {
        lastUpdateTime = currentMillis;
        displayMode = (displayMode + 1) % 3; // Cycle through modes (0, 1, 2)
        updateDisplay();
    }
}

void updateDisplay() {
    lcd.clear();

    if (displayMode == 0) {
        // Show A-D
        lcd.setCursor(0, 0);
        lcd.print(sensorLabels[0]);
        lcd.print(sensorCounts[0]);
        lcd.print(" ");
        lcd.print(sensorLabels[1]);
        lcd.print(sensorCounts[1]);

        lcd.setCursor(0, 1);
        lcd.print(sensorLabels[2]);
        lcd.print(sensorCounts[2]);
        lcd.print(" ");
        lcd.print(sensorLabels[3]);
        lcd.print(sensorCounts[3]);
    } else if (displayMode == 1) {
        // Show E-H
        lcd.setCursor(0, 0);
        lcd.print(sensorLabels[4]);
        lcd.print(sensorCounts[4]);
        lcd.print(" ");
        lcd.print(sensorLabels[5]);
        lcd.print(sensorCounts[5]);

        lcd.setCursor(0, 1);
        lcd.print(sensorLabels[6]);
        lcd.print(sensorCounts[6]);
        lcd.print(" ");
        lcd.print(sensorLabels[7]);
        lcd.print(sensorCounts[7]);
    } else if (displayMode == 2) {
        // Show Time
        DateTime now = rtc.now();
        lcd.setCursor(0, 0);
        lcd.print("Time: ");
        lcd.print(now.hour());
        lcd.print(":");
        lcd.print(now.minute());
        lcd.print(":");
        lcd.print(now.second());

        lcd.setCursor(0, 1);
        lcd.print("Date: ");
        lcd.print(now.month());
        lcd.print("/");
        lcd.print(now.day());
        lcd.print("/");
        lcd.print(now.year());
    }
}