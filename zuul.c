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
int status = 0;
sqlite3 *db;
int rc;

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

// blinkt <count> mal mit der led
//ungetested
static void blink(int r,int g,int b, int count) {
	int i = 0;
	for(i=0;i<count;i++) {
		led(r,g,b);
		sleep(0.5);
		printf("Blink an\n");
		led(0,0,0);
		sleep(0.5);
		printf("Blink aus\n");
	}
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

//schreibt einen Log eintrag
//ungeprüft
int sqlDoLog(char *answ,char *info) {
	char *zErrMsg = 0;
	char query[1024];

	rc = sqlite3_open(dbFile, &db);
	if(rc) {
		printf("SQL: unbekannter Fehler.\n");
		exit(1);
	}else{
		printf("SQL: DB geoeffnet.\n");
		snprintf(query, sizeof(query), "INSERT INTO log (tokenID,answere,timeCode,addInfo) VALUES ('%s','%s',datetime(),'%s');", tokenID,answ,info);
		printf("%s\n",query);
		rc = sqlite3_exec(db, query, sqlDoNothing, 0, &zErrMsg);
		if( rc != SQLITE_OK ){
			printf("SQL: %s\n", zErrMsg);
			sqlite3_free(zErrMsg);
		}else{
			printf("SQL: Log: success\n");
		}
	}
	sqlite3_close(db);
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

int chkTokenID_res(void *NotUsed, int argc, char **argv, char **azColName){
	printf("ARGC: %u\n",argc);
	if(argc == 0) {
		//keine übereinstimmung
		strcpy(tokenKey,"");
		status = -1;
		return 1;
	}else{
		//übereinstimmung gefunden
		strcpy(tokenKey,argv[0]);
		status = 1;
		return 0;
	}
	
	//printf("UID: %s\nKey: %s\n",argv[1], argv[0]);

}

//suche token in DB
//ungeprüft
int chkTokenID() {
	char *zErrMsg = 0;
	char query[1024];
	rc = sqlite3_open(dbFile, &db);
	
	if(rc) {
		printf("SQL: unbekannter Fehler.\n");
		exit(1);
	}else{
		printf("SQL: DB geoeffnet.\n");
		snprintf(query, sizeof(query), "SELECT tKey,userID FROM token WHERE tID = '%s';", tokenID);
		printf("%s\n",query);
		rc = sqlite3_exec(db, query, chkTokenID_res, 0, &zErrMsg);
		if( rc != SQLITE_OK ){
			printf("SQL: %s\n", zErrMsg);
			sqlite3_free(zErrMsg);
		}else{
			printf("SQL: success\n");
		}
	}
	sqlite3_close(db);
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
	if (context == NULL) {
		printf("Unable to init libnfc (malloc)\n");
		exit(EXIT_FAILURE);
	}
	
	// while(true) {
		printf("--- Neuer Durchgang ---\n");
		// auf token warten
		pnd = nfc_open(context, NULL);
		printf("-- nfc_open --\n");
		if (pnd == NULL) {
			printf("ERROR:%s\n", "Unable to open NFC device.");
			exit(EXIT_FAILURE);
		}
		led(1,1,0); //Gelb an
		// token lesen
		//printf("Tokens gefunden: %u\n",nfc_initiator_select_passive_target(pnd, nmMifare, NULL, 0, &nt));

		if (nfc_initiator_select_passive_target(pnd, nmMifare, NULL, 0, &nt) == 1) {
			sprintf(tokenID,"%02x %02x %02x %02x %02x %02x %02x %02x",nt.nti.nai.abtUid[0],nt.nti.nai.abtUid[1],nt.nti.nai.abtUid[2],nt.nti.nai.abtUid[3],nt.nti.nai.abtUid[4],nt.nti.nai.abtUid[5],nt.nti.nai.abtUid[6],nt.nti.nai.abtUid[7]);
			printf("%s\n",tokenID);
		}
		
		printf("--- Beginne Pruefung ---\n");
		
		chkTokenID();
		if(status == 1) {
			printf("--- Suchen Token Key ---\n");
			sqlDoLog("G","Test");
			//chkTokenKey();
		}else{
			sqlDoLog("D","Test");
			// blink(1,0,0,2);
		}
		
		printf("--- Pruefung beendet ---\n");
		
		while(nfc_initiator_target_is_present(pnd,NULL) == 0) {
			sleep(1);
		}
		
		printf("--- Durchgang beendet ---\n");
		
		// TODO checken ob offen ist oder nicht um dann blau oder black zu zeigen

		nfc_close(pnd);
		
		//strcpy(tokenID,"");
		//strcpy(tokenKey,"");
		status = 0;
	// }
  	nfc_exit(context);
  	exit(EXIT_SUCCESS);
}	
