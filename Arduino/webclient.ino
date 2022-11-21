/* GPIO Server using ESP8266 Webserver with a Temp sensor and relay control

   Based on ESP8266Webserver, DHTexample, and BlinkWithoutDelay (thank you)

   Version 1.0  Eran Marelly
*/
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const char* ssid     = "XXXXXXXX";

const char* password = "XXXXXXXX";
 // GPIO where the DS18B20 is connected to
const int oneWireBus = 4;     

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(oneWireBus);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);
// variable to hold device addresses
DeviceAddress Thermometer;
int deviceCount = 0;

ESP8266WebServer server(80);
 
 
String webString="";     // String to display
const long interval = 2000;              // interval at which to read sensor
void handle_root() {
  server.send(200, "text/plain", "Hello from  esp8266, \r\nUsage: \r\n1) read temp sensor /temp \r\n2) Set GPIO /SetGPIO?id=<GPIO #>;value=<1 or 0> \r\n3) Read GPIO /GetGPIO?id=<GPIO #>\r\n4) Change one wire port (default = 4) /SetONEWire?id=<GPIO #>");
  delay(100);
}


void setup(void)
{
  // for Arduino IDE Serial Monitor window 
  Serial.begin(115200);  
   // Start the DS18B20 sensor
  sensors.begin();

  // Connect to WiFi network
  Serial.printf("\n\r \n\rDefault hostname: %s\n", WiFi.hostname().c_str());
  WiFi.hostname("ESPBoilerControler");
  Serial.printf("New hostname: %s\n", WiFi.hostname().c_str());
  WiFi.begin(ssid, password);
  Serial.print("\n\r \n\rWorking to connect");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("GPIO Server");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
   
  server.on("/help", handle_root);
  server.on("/h", handle_root);
  server.on("/Help", handle_root);
  server.on("/", handle_root);
  server.on("/SetONEWire", [](){
  if (server.args() > 0) {
        int oneWireBusNum =server.arg(0).toInt();
        oneWire = OneWire(oneWireBusNum);
        sensors = DallasTemperature(&oneWire);
        sensors.begin();
        webString = "ONEWire port set to  " + String(oneWireBusNum); 
        server.send(200, "text/plain", webString);
    }
  });
  server.on("/temp", [](){  
    sensors.requestTemperatures(); 
    deviceCount = sensors.getDeviceCount();
    webString ="{ \"Temp Sensors\": [ ";
    String sepersator = "";
    for (int i = 0;  i < deviceCount;  i++)
    {
      float temperatureC = sensors.getTempCByIndex(i);
      sensors.getAddress(Thermometer, i);
      webString=webString + sepersator +"  {\"Temperature\": "+String((float)temperatureC)+" ,\"Address\": \"" +printAddress(Thermometer)+ "\"}";   // Arduino has a hard time with float to string
      sepersator = ",";
    }
    server.send(200, "text/plain", webString +"]}");            
  });

  server.on("/GetGPIO", [](){  
    /*for (int i = 0; i < server.args(); i++) {
      Serial.print(String(i) + " ");  //print id
      Serial.print("\"" + String(server.argName(i)) + "\" ");  
      Serial.println("\"" + String(server.arg(i)) + "\"");  
      }*/
      if (server.args() > 0) {
        int GPIONum =server.arg(0).toInt();
        //pinMode(GPIONum, OUTPUT);
        int GPIOStatus = digitalRead(GPIONum);
        webString = "GPIO " + String(GPIONum) + " = " + String(GPIOStatus); 
      }
      //webString ="mmm....";
      server.send(200, "text/plain", webString);            
  });
  
  server.on("/SetGPIO", [](){  
    /*for (int i = 0; i < server.args(); i++) {
      Serial.print(String(i) + " ");  //print id
      Serial.print("\"" + String(server.argName(i)) + "\" ");  //print name
      Serial.println("\"" + String(server.arg(i)) + "\"");  //print value
    }*/
      if (server.args() > 1) {
        int GPIONum =server.arg(0).toInt();
        pinMode(GPIONum, OUTPUT);
        if (server.arg(1).toInt() == 1) {
           digitalWrite(GPIONum,HIGH);
           webString = "GPIO " + String(GPIONum) + " = 1" ; 
        }
        else{
          digitalWrite(GPIONum,LOW);
          webString = "GPIO " + String(GPIONum) + " = 0" ; 
        }
        
      }
      //webString ="mmm....";
      server.send(200, "text/plain", webString);            
  });

 
  
  server.begin();
  Serial.println("HTTP server started");
}
 
void loop(void)
{
  server.handleClient();
} 

String printAddress(DeviceAddress deviceAddress)
{ 
  char addr[30];
  String RetSTR = "0x";
  for (uint8_t i = 0; i < 8; i++)
  {
  // RetSTR = RetSTR + "0x";
   if (deviceAddress[i] < 0x10) RetSTR = RetSTR + "0";
   sprintf(addr,"%x",deviceAddress[i]);
   RetSTR = RetSTR + addr;
   //if (i < 7) RetSTR = RetSTR +", "; 
  }
  return RetSTR;
}
