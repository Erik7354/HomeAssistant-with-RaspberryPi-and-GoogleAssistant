#include <Adafruit_NeoPixel.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

ESP8266WebServer server(80);
int NeoPIN = 14; // D5 on NodeMCU Lolin V3
int NUM_LEDS = 64;
Adafruit_NeoPixel matrix = Adafruit_NeoPixel(NUM_LEDS, NeoPIN, NEO_GRB + NEO_KHZ800);
//matrix.setBrightness(51);
const char* ssid = "YourWifiSSID";
const char* pw = "YourWifiPassword";

void setup() {
  matrix.begin();
  matrix.show();
  
  Serial.begin(115200);
  
  WiFi.begin(ssid,pw);
  Serial.println();
  

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.println("Waiting to connect...");
  }

  server.on("/", handlePath);
  server.begin();
  Serial.println(WiFi.localIP());
  Serial.println("Server listening.");

}




void loop() {
  server.handleClient();
}




void handlePath(){
  Serial.println("got it"); 
  server.send(200, "text/plain", "This is not for \"get\" requests");
  String message;
  int p = 1;
  if (server.args() != 0){
    matrix.setBrightness(server.arg(192).toInt());
    for (int i = 0; i < 64; i++){
      matrix.setPixelColor(i, server.arg(p-1).toInt(), server.arg(p).toInt(), server.arg(p+1).toInt());
      p += 3;
    }
  }
  /*for (int i = 0; i < server.args(); i++){
    Serial.print("Arg no" + String(i) + " -> ");
    Serial.print(server.argName(i) + ": ");
    Serial.print(server.arg(i) + "\n");
    if (server.argName(i) == "data"){
    }
  }*/
  matrix.show();
}
