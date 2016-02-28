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

static void print_hex(const uint8_t *pbtData, const size_t szBytes) {
	size_t  szPos;
 
	for (szPos = 0; szPos < szBytes; szPos++) {
		printf("%02x  ", pbtData[szPos]);
	}
}

static int callback(void *NotUsed, int argc, char **argv, char **azColName){
	int i;
	for(i=0; i<argc; i++){
		printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
	}
	printf("\n");
	return 0;
}

static int checkToken(char *tID) {
	sqlite3 *db;
	char *zErrMsg = 0;
	int rc;
	char *sql;

	rc = sqlite3_open("zuul.db", &db);

	if( rc ){
		fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
		exit(0);
	}else{
		fprintf(stderr, "Opened database successfully\n");
		
	}
	
	/* Create SQL statement */
	sql = "SELECT * FROM log;";

	/* Execute SQL statement */
	rc = sqlite3_exec(db, sql, callback, 0, &zErrMsg);
	if( rc != SQLITE_OK ){
		fprintf(stderr, "SQL error: %s\n", zErrMsg);
		sqlite3_free(zErrMsg);
	}else{
		fprintf(stdout, "Table created successfully\n");
	}
	sqlite3_close(db);
	return 0;
}

int main(int argc, const char *argv[])
{
	checkToken("bla");
	
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
    		printf("Alter TAG gefunden:");
    		printf("ATQA:");
    		print_hex(nt.nti.nai.abtAtqa, 2);
			printf("NFCID-Typ: %c", (nt.nti.nai.abtUid[0] == 0x08 ? '3' : '1'));
    		printf("NFCID: ");
    		print_hex(nt.nti.nai.abtUid,nt.nti.nai.szUidLen);

    		printf("SAK: ");
    		print_hex(&nt.nti.nai.btSak, 1);
    		if (nt.nti.nai.szAtsLen) {
      			printf("          ATS (ATR): ");
      			print_hex(nt.nti.nai.abtAts, nt.nti.nai.szAtsLen);
    		}
  	}

	nfc_close(pnd);
  	nfc_exit(context);
  	exit(EXIT_SUCCESS);
}
