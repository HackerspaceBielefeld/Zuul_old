#include <stdlib.h>
#include <nfc/nfc.h>
#include <wiringPi.h>
#include <string.h>
#include <sqlite3.h>

// konstanten für Pinbelegung
const int LED_R = 8;	//rot
const int LED_G = 10;	//grün
const int LED_B = 12;	//blau

const int DOOR = 18;	//türöffner

// Konstante für NFC
const nfc_modulation nmMifare = {
	.nmt = NMT_ISO14443A,
	.nbr = NBR_106,
};

// nfc bereit machen
nfc_device *pnd; 		// pointer für lese gerät
nfc_target nt; 			// platz für daten vom Token
nfc_context *context;	//

// led steuerung
// ungeprüft
static void led(int r, int g, int b) {
	digitalWrite(LED_R, r);
	digitalWrite(LED_G, g);
	digitalWrite(LED_B, b);
}

//tür öffnen
//ungeprüft
static void door() {
	digitalWrite(DOOR, 1);
	sleep(2000);
	digitalWrite(DOOR, 0);
}


//dummy func für nach dem zugriff auf die db
//ungeprüft
static int sqlDoNothing(void *NotUsed, int argc, char **argv, char **azColName){
	return 0;
}


int main(int argc, const char *argv[]){
	//GPIO als ausgänge legen
    pinMode(LED_R, OUTPUT);
    pinMode(LED_G, OUTPUT);
    pinMode(LED_B, OUTPUT);

	pinMode(DOOR, OUTPUT);
	
	// nfc initiiere
	nfc_init(&context); //lese gerät initiieren
	
	while(true) {
		// auf token warten
		pnd = nfc_open(context, NULL);
		led(1,1,0); //Gelb an
		
		// token lesen
		if (nfc_initiator_select_passive_target(pnd, nmMifare, NULL, 0, &nt) > 0) {
			printf("%s\n",nt.nti.nai.abtUid);
		}
		
		nfc_close(pnd);
	}
  	nfc_exit(context);
  	exit(EXIT_SUCCESS);
}	
