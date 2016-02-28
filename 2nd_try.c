#include <stdlib.h>
#include <nfc/nfc.h>
#include <wiringPi.h>
#include <string.h>
#include <sqlite3.h>

/*
Pin 2		5VCC
Pin 6		GND
Pin 8		LED R
Pin 10	LED G
Pin 12	LED B
Pin 14	LED GND
Pin 15	NF-AMP Power
Pin 18	Dooropener
Pin 19	MOSI
Pin 21	MISO
Pin 23	CLK
Pin 24	CE0
*/

int doorCode = 0;
int *tokenID = 0;

static int toHex(const uint8_t *data) {
	int n = sizeof(data);
	int i = 0;
 
	for (i = 0; i < n; i++) {
		printf("%02x ", data[i]);
	}
}

static int callback(void *NotUsed, int argc, char **argv, char **azColName){
	
	if(argc==0) {
		doorCode = 999;
	}
	printf("%s = %s\n", azColName[0], argv[0] ? argv[0] : "NULL");
	return 0;
}
static int callback2(void *NotUsed, int argc, char **argv, char **azColName){
	
	if(argc==0) {
		doorCode = 999;
	}
	printf("%s = %s\n", azColName[0], argv[0] ? argv[0] : "NULL");
	return 0;
}

static int checkToken(char *inID) {
	sqlite3 *db;
	char *zErrMsg = 0;
	int rc;

	rc = sqlite3_open("zuul.db", &db);

	if( rc ){
		fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
		exit(0);
	}else{
		fprintf(stderr, "Opened database successfully\n");
		
	}
	
	/* Create SQL statement */
	char sql[1024];
	snprintf(sql, sizeof(sql), "SELECT tKey,uName FROM token,users WHERE tID = '%s' AND token.userID = users.uID;", inID);

	/* Execute SQL statement */
	rc = sqlite3_exec(db, sql, callback, 0, &zErrMsg);
	if( rc != SQLITE_OK ){
		fprintf(stderr, "SQL ERROR:\n");
		sqlite3_free(zErrMsg);
	}else{
		if(doorCode == 999){
			fprintf(stdout, "Token erkannt\n");
		}else{
			fprintf(stdout,"Token unbekannt\n");
			snprintf(sql, sizeof(sql), "INSERT INTO log (tokenID,answere,timecode) VALUES ('%s','U',datetime());", inID);
			rc = sqlite3_exec(db, sql, callback2, 0, &zErrMsg);
			if( rc == SQLITE_OK ){
				fprintf(stdout,"Logeintrag erfolgreich.\n");
			}else{
				fprintf(stderr, "SQL ERROR:\n");
				sqlite3_free(zErrMsg);
			}
		}
	}
	sqlite3_close(db);
	return 0;
}

int main(int argc, const char *argv[]){
	
	// nfc bereit machen
	nfc_device *pnd; // pointer für lese gerät
	nfc_target nt; //

	nfc_context *context;
	nfc_init(&context);
	// gerät initiiere
	if (context == NULL) {
		printf("ERROR: fehler beim dev init\n");
		exit(EXIT_FAILURE);
	}

	// öffnet verbindung zum token
	pnd = nfc_open(context, NULL);
 
	if (pnd == NULL) {
		printf("ERROR: fehler beim öffnen.\n");
		exit(EXIT_FAILURE);
	}

	if (nfc_initiator_init(pnd) < 0) {
		nfc_perror(pnd, "nfc_initiator_init");
		exit(EXIT_FAILURE);
	}

	const nfc_modulation nmMifare = {
    		.nmt = NMT_ISO14443A,
    		.nbr = NBR_106,
  	};
  	if (nfc_initiator_select_passive_target(pnd, nmMifare, NULL, 0, &nt) > 0) {
    		toHex(nt.nti.nai.abtUid);
			checkToken(nt.nti.nai.abtUid);
  	}

	nfc_close(pnd);
  	nfc_exit(context);
  	exit(EXIT_SUCCESS);
}
