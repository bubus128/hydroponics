#include <Wire.h>
#include "Pump.h"
#include "DosingQueue.h"
#define TdsSensorPin A2
#define PhSensorPin A3
#define VREF 5.0      // analog reference voltage(Volt) of the ADC

float temperature = 25;
DosingQueue dosing_queue;
int pins1[4]={6,7,8,9};
SyringePump phPlusPump(pins1);
int pins2[4]={2,3,4,5};
SyringePump phMinusPump(pins2);
int pins3[4]={10,11,12,13};
SyringePump costamPump (pins3);
String sensor="PH";
int pomp_buffer[2][30];
int tds=0;
int rotetes_per_ml=658;

void receiveEvent(int byte_count) {
  int data=Wire.read();
  if(data==5){
    sensor="PH";
  }
  else if(data==6){
    sensor="TDS";
    float voltage=VREF*(float)analogRead(TdsSensorPin)/1024;
    float compensationCoefficient=(float)1.0+0.02*(temperature-25.0);    
    float compensationVolatge=(float)voltage/compensationCoefficient;  //temperature compensation
    float tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5; //convert voltage value to tds value
    tds=(int)round(tdsValue);
    Serial.println(tds);
  }
  else{
    Wire.read();
    int pump = Wire.read();
    int dose = rotetes_per_ml*Wire.read();
    Serial.println("dosing");
    Serial.println(pump);
    Serial.println(dose);
    if(pump>3)
    {
      pump-=3;
      dose*=-1;      
    }
    dosing_queue.add(pump,dose);
  }
}

void requestEvent(){
  if(sensor=="TDS"){
    Wire.write(tds);
    tds=tds>>8;
  }
  else if(sensor=="PH"){
    Serial.println("measuring ph");
    float ph_measure=analogRead(PhSensorPin);
    float phValue=(float)ph_measure*VREF*3.5/1024; //convert the analog into ph
    int sent_value=(int)round(10*phValue); 
    Serial.println(sent_value);                  
    Wire.write(sent_value);
  }
  else
    Wire.write(10);
}

void setup() {
  Serial.begin(9600);
  Wire.begin(0x7);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  pinMode(TdsSensorPin,INPUT);
}

void dosingActions(){
  while(!dosing_queue.is_empty()){
    int tab[2];
    if(dosing_queue.get_next(tab)==NULL){
      break;
    }
    Serial.println("dosing");
    if(tab[0]==1){
      int dose=tab[1];
      if(dose>0)
         phPlusPump.dosing(dose);
      else if(dose<0)
         phPlusPump.refile(dose*(-1));
    }
    else if(tab[0]==2){
      int dose=tab[1];
      if(dose>0)
         phMinusPump.dosing(dose);
      else if(dose<0)
         phMinusPump.refile(dose*(-1));
    }
    else
      Serial.println("error");
  }
  Serial.println("dosing queue empty");
}

void loop() {
  delay(500);
  dosingActions();
}
