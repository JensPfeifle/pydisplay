/*

  The circuit:
   LCD RS pin to digital pin 7
   LCD Enable pin to digital pin 6
   LCD D4 pin to digital pin 5
   LCD D5 pin to digital pin 4
   LCD D6 pin to digital pin 3
   LCD D7 pin to digital pin 2
   LCD R/W pin to ground
   LCD VSS pin to ground
   LCD VCC pin to 5V
   10K resistor:
   ends to +5V and ground
   wiper to LCD VO pin (pin 3)

*/
#include <SPI.h>         // needed for Arduino versions later than 0018
#include <Ethernet.h>
#include <EthernetUdp.h>         // UDP library from: bjoern@cs.stanford.edu 12/30/2008
#define UDP_TX_PACKET_MAX_SIZE 128 //increase UDP size
#include <LiquidCrystal.h>

// liquidCrystal
const int rs = 7, en = 6, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
const int rows = 4;
const int columns = 20;
// Ethernet
// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED
};
IPAddress ip(192, 168, 2, 2);

unsigned int localPort = 8888;      // local port to listen on

// buffers for receiving and sending data
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];  //buffer to hold incoming packet,
char  ReplyBuffer[] = "acknowledged";       // a string to send back

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;


void setup() {
  // set up the LCD's number of columns and rows:
  lcd.begin(columns, rows);
  // start the Ethernet and UDP:
  Ethernet.begin(mac, ip);
  Udp.begin(localPort);
  // Print a message to the LCD.
  lcd.print(ip);
  // start serial
  Serial.begin(9600);
}

void loop() {
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From ");
    IPAddress remote = Udp.remoteIP();
    for (int i = 0; i < 4; i++) {
      Serial.print(remote[i], DEC);
      if (i < 3) {
        Serial.print(".");
      }
    }
    Serial.print(", port ");
    Serial.println(Udp.remotePort());

    // read the packet into packetBufffer
    Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
    Serial.println("Contents:");
    Serial.println(packetBuffer);
    if (packetSize != 80) {
      Serial.println("Wrong size!");
    }
    else {
      //initialize char arrays +1 for null terminator
      char lineOne[columns + 1] = {};
      char lineTwo[columns + 1] = {};
      char lineThree[columns + 1] = {};
      char lineFour[columns + 1] = {};

      int i = 0;
      while (i < columns) {
        lineOne[i] = packetBuffer[i];
        i++;
      }
      Serial.print("lineOne:");
      Serial.println(lineOne);

      int n = 0;
      do  {
        lineTwo[n] = packetBuffer[i];
        n++;
        i++;
      } while (i < columns * 2);
      Serial.print("lineTwo:");
      Serial.println(lineTwo);

      n = 0;
      do {
        lineThree[n] = packetBuffer[i];
        n++;
        i++;
      } while (i < columns * 3);
      Serial.print("lineThree:");
      Serial.println(lineThree);

      n = 0;
      do {
        lineFour[n] = packetBuffer[i];
        n++;
        i++;
      } while (i < columns * 4);
      Serial.print("lineFour:");
      Serial.println(lineFour);

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(lineOne);
      lcd.setCursor(0, 1);
      lcd.print(lineTwo);
      lcd.setCursor(0, 2);
      lcd.print(lineThree);
      lcd.setCursor(0, 3);
      lcd.print(lineFour);
    }
    if (false) {
      // send a reply to the IP address and port that sent us the packet we received
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write(ReplyBuffer);
      Udp.endPacket();
    }
    //finally, clear packet buffer
    memset(packetBuffer, 0, sizeof(packetBuffer));
  }
  delay(10);
}

