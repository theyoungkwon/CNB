#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>

WiFiMulti WiFiMulti;
#define USE_SERIAL Serial

const char* SSID = "SPARTHAN";
const char* PASS = "66668888";
const String HOST = "192.168.137.192";
const uint16_t PORT = 5000;

void setup() {

  USE_SERIAL.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(SSID, PASS);
  Serial.print("Wait for WiFi...");
  while (WiFiMulti.run() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  delay(500);
}

void loop() {
  if ((WiFiMulti.run() == WL_CONNECTED)) {
    HTTPClient http;
    http.begin("http://" + HOST + ":" + PORT + "/");
    int httpCode = http.GET();
    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        String cmd = payload;
        if (String("PALM") == cmd) {
          Serial.println("PALM");
        }
        else if (String("FIST") == cmd) {
          Serial.println("FIST");
        }
        else if (String("THUMB") == cmd) {
          Serial.println("THUMB");
        }
        else if (String("POINT") == cmd) {
          Serial.println("POINT");
        }
        else if (String("PEACE") == cmd) {
          Serial.println("PEACE");
        }
      }
    } else {
      USE_SERIAL.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
  }

  delay(500);
}