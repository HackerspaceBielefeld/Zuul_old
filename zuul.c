#include <err.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <nfc/nfc.h>
#include <freefare.h>

#include <wiringPi.h>

#include <sqlite3.h>

int debug = 0;

char tokenID[32];
char tokenKey[32];
int status = 0;
sqlite3 *db;

// Konstanten NFC
const nfc_modulation nmMifare = {
	.nmt = NMT_ISO14443A,
	.nbr = NBR_106,
};
nfc_device *device; 		// pointer für lese gerät
nfc_target nt; 			// platz für daten vom Token
nfc_context *context;	//
MifareTag *tags = NULL; //gefundene Token
int rc;

// konstanten GPIO
const int LED_R = 8;	//rot
const int LED_G = 10;	//grün
const int LED_B = 12;	//blau

const int DOOR = 18;	//türöffner

// konstanten SQLITE3
const char *dbFile = "zuul.db";

// müsste der key sein fürs file system
uint8_t key_data_picc[8] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };	
// verrechnungsschlüssel wird mit uid verrechnet
u_int8_t encryption_key[8] = { 0x42, 0x13, 0x37, 0x42, 0x13, 0x37, 0x12, 0x34 };
u_int8_t new_key[8] = { 0x42, 0x13, 0x37, 0x42, 0x13, 0x37, 0x12, 0x34 };
// key für Dir
	// Str Zuul-HSB in hex
uint8_t key_for_zuul[8] = { 0x5a, 0x75, 0x75, 0x6c, 0x2d, 0x48, 0x53, 0x42 };

// Default Mifare DESFire ATS
uint8_t new_ats[] = { 0x06, 0x75, 0x77, 0x81, 0x02, 0x80 };

// led steuerung
// untested
static void led(int r, int g, int b) {
	digitalWrite(LED_R, r);
	digitalWrite(LED_G, g);
	digitalWrite(LED_B, b);
	printf("# %u %u %u\n", r,g,b);
}

// blinkt <count> mal mit der led
// untested
static void blink(int r,int g,int b, int count) {
	int i = 0;
	for(i=0;i<count;i++) {
		led(r,g,b);
		printf("Blink an\n");
		sleep(1);
		led(0,0,0);
		printf("Blink aus\n");
		sleep(1);
	}
}

// tür öffnen
// untested
static void door() {
	printf("Tuer oeffnen\n");
	digitalWrite(DOOR, 1);
	sleep(3);
	printf("Tuer beenden\n");
	digitalWrite(DOOR, 0);
}

//dummy func für nach dem zugriff auf die db
//ungeprüft
static int sqlDoNothing(void *NotUsed, int argc, char **argv, char **azColName){
	return 0;
}

//schreibt einen Log eintrag
//ungeprüft
void sqlDoLog(char *answ,char *info) {
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



// berechnet den Key aus der UID und dem encryption_key
// untested
void getKeyFromUID(u_int8_t *uid) {
	int n = sizeof(uid);
	printf("N: %i\n",n);
	int i = 0;
	for(i=0;i<n;i++) {
		if(uid[i] <= 0x80) {
			new_key[i] = uid[i] + encryption_key[i];
		}else{
			new_key[i] = uid[i] - encryption_key[i];
		}
	}
}

int main(int argc, char *argv[])
{
	printf("Zuul [v0.4 dev] Hauptprogramm\n\n");
	led(1,1,1);
	
	int i,j;
	for(i=1;i<argc;i++) {
		//printf("%i: %s\n",i,argv[i]);
		if(!strcmp(argv[i],"-d")){
			debug = 1;
			printf("[Debug-Mode]\n");
		}
	}
		
	//GPIO als ausgänge legen
    pinMode(LED_R, OUTPUT);
    pinMode(LED_G, OUTPUT);
    pinMode(LED_B, OUTPUT);

	pinMode(DOOR, OUTPUT);
	
	while(true) {
		sleep(1);
		led(0,0,0);
		// nfc initiiere
		nfc_init(&context); //lese gerät initiieren
		if (context == NULL) {
			printf("Unable to init libnfc (malloc)\n");
			exit(EXIT_FAILURE);
		}
		
		if(debug) printf("--- Neuer Durchgang ---\n");
		// auf token warten
		device = nfc_open(context, NULL);
		if(debug) printf("-- nfc_open --\n");
		if (device == NULL) {
			if(debug) printf("ERROR:%s\n", "Unable to open NFC device.");
			exit(EXIT_FAILURE);
		}
		
		while(nfc_initiator_select_passive_target(device, nmMifare, NULL, 0, &nt) != 1) {
			sleep(1);
		}
		led(1,1,0); //gelb an
		
		// listet gefundene tags auf
		tags = freefare_get_tags (device);
		if(!tags) continue;
		if(debug) printf("Tag: %x\n",tags);
		
		for (i = 0; tags[i]; i++) {
			int res = mifare_desfire_connect (tags[i]);
			char *tag_uid = freefare_get_tag_uid (tags[i]);

			
			// hole UID
			if (res < 0) {
				if(debug) warnx ("Can't connect to Mifare DESFire target.");
				blink(1,0,0,1);
				break;
			}
			
			// prüfte ob EV1
			struct mifare_desfire_version_info info;
			res = mifare_desfire_get_version (tags[i], &info);
			if (res < 0) {
				freefare_perror (tags[i], "mifare_desfire_get_version");
				if(debug) printf("Token ist kein EV1\n");
				blink(1,0,0,1);
				break;
			}
			
			// prüfe ob version
			if (info.software.version_major < 1) {
				if(debug) warnx ("Found old DESFire, skipping");
				blink(1,0,0,1);
				continue;
			}
			if(debug) printf ("Found %s with UID %s.\n", freefare_get_tag_friendly_name (tags[i]), tag_uid);
			//------------------------------------
			
			
			
			//------------------------------------
			mifare_desfire_disconnect (tags[i]);
			free (tag_uid);
		}
		freefare_free_tags (tags);
		nfc_close (device);
		nfc_exit (context);
		if(debug) printf("--- Durchgang beendet ---\n");
	}
}

//https://github.com/raidolepp/libfreefare/tree/master/libfreefare/examples
