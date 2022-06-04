# Hydroponics - autonomous hydroponic strawberry plantation

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Thesis](#thesis)

## General info
The aim of the project was to create fully autonomous hydroponics strawberry plantation. It enables the plant to grow and bear fruit regardless of the conditions of the external environments. The main idea was to allow cultivation at home without the need for supervision. To achieve this goal, the device must provide optimal conditions for the internal environment, such as:
* temperature
* humidity
* light intensity
* water pH
* the appropriate content of fertilizers in the water
* water aeration

## Technologies
To monitor the condition of the plantation and environmental conditions, sensors were used, such as:
* **pH sensor**
* **TDS sensor** (sensor for measuring the content of fertilizers in the water)
* **thermometers**
* **hygrometers**
* **light intensity sensor**

Software was mainly written with:
* **Python 3.10** with libraries like:
  * RPi.GPIO
  * picamera
  * smbus
  * adafruit_dht
  * adafruit_tsl2591
* **Arduino**

3d models were created with **Autodesk Fusion 360**

**Raspberry Pi 4 B** was used as the main managing computer for the device. While the **Arduino Nano** served as an auxiliary computer that controlled the syringe pumps.

## Thesis
More detailed information about this project can be found in the BSc thesis which can be found [**here**](projekt_dyplomowy_inzynierski.pdf). Project still in development after writing this thesis so there may be discrepancies between the code in the repository and the inserts in thesis.
