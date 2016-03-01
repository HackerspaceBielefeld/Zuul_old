#include <stdlib.h>
#include <nfc/nfc.h>
#include <wiringPi.h>
#include <string.h>
#include <sqlite3.h>

// konstanten GPIO
const int LED_R = 8;	//rot
const int LED_G = 10;	//grün
const int LED_B = 12;	//blau

const int DOOR = 18;	//türöffner

// konstanten SQLITE3
const char *dbFile = "zuul.db";

// Konstanten NFC
const nfc_modulation nmMifare = {
	.nmt = NMT_ISO14443A,
	.nbr = NBR_106,
};

// globale variablen
char tokenID[32];
char tokenKey[32];

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

//überprüfe den token
//TODO chier gehts weiter
int chkTokenKey(void *NotUsed, int argc, char **argv, char **azColName){
	printf("ARGC: %u\n",argc);
	if(argc==0) {
		//doorCode = 1;
	}
	
	printf("UID: %s\nKey: %s\n",argv[1], argv[0]);

	return 0;
}

//suche token in DB
//ungeprüft
int chkTokenID() {
	sqlite3 *db;
	char *zErrMsg = 0;
	int rc;
	char query[1024];

	rc = sqlite3_open(dbFile, &db);
	if(rc) {
		printf("SQL: unbekannter Fehler.\n");
		exit(1);
	}else{
		printf("SQL: DB geoeffnet.\n");
		snprintf(query, sizeof(query), "SELECT tKey,userID FROM token WHERE tID = '%s';", tokenID);
		printf("%s\n",query);
		rc = sqlite3_exec(db, query, chkTokenKey, 0, &zErrMsg);
		if( rc != SQLITE_OK ){
			printf("SQL: %s\n", zErrMsg);
			sqlite3_free(zErrMsg);
		}else{
			printf("SQL: success\n");
		}
	}
	sqlite3_close(db);
}


//dummy func für nach dem zugriff auf die db
//ungeprüft
static int sqlDoNothing(void *NotUsed, int argc, char **argv, char **azColName){
	return 0;
}


int main(int argc, const char *argv[]){
	printf("Zuul [v0.2 dev] Hauptprogramm\n\n");
	
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
			sprintf(tokenID,"%02x %02x %02x %02x %02x %02x %02x %02x",nt.nti.nai.abtUid[0],nt.nti.nai.abtUid[1],nt.nti.nai.abtUid[2],nt.nti.nai.abtUid[3],nt.nti.nai.abtUid[4],nt.nti.nai.abtUid[5],nt.nti.nai.abtUid[6],nt.nti.nai.abtUid[7]);
			printf("%s\n",tokenID);
		}
		
		printf("--- Beginne Pruefung ---\n");
		
		// TODO checken der token ok ist
		chkTokenID();
		
		printf("--- Pruefung beendet ---\n");
		
		while(nfc_initiator_target_is_present(pnd,NULL) == 0) {
			sleep(1);
		}
		
		printf("--- Durchgang beendet ---\n");
		
		// TODO checken ob offen ist oder nicht um dann blau oder black zu zeigen

		nfc_close(pnd);
	}
  	nfc_exit(context);
  	exit(EXIT_SUCCESS);
}	
