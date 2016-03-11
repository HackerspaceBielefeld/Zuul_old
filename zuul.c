#include <err.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <nfc/nfc.h>
#include <freefare.h>

#include <wiringPi.h>

#include <sqlite3.h>

int debug = 1;

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
	if(debug) printf("# %u %u %u", r,g,b);
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
	
	int i,j;
		
	//GPIO als ausgänge legen
    pinMode(LED_R, OUTPUT);
    pinMode(LED_G, OUTPUT);
    pinMode(LED_B, OUTPUT);

	pinMode(DOOR, OUTPUT);
	
	while(true) {
		sleep(1);
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
		
		// listet gefundene tags auf
		tags = freefare_get_tags (device);
		if(debug) printf("Tag: %x\n",tags);
		
		
		if(debug) printf("--- Durchgang beendet ---\n");
	}

/*
		
		if (!tags) {
			nfc_close (device);
			errx (EXIT_FAILURE, "Error listing Mifare DESFire tags.");
		}

		int i;
		for (i = 0; (!error) && tags[i]; i++) {
			// wenn tag kein Desfire,dann überspringen
			if (DESFIRE != freefare_get_tag_type (tags[i]))
				continue;

			//holt uid von token
			char *tag_uid = freefare_get_tag_uid (tags[i]);
			char buffer[BUFSIZ]; // ??? nur für konsolen kram
			int res;

			// verbindet token
			res = mifare_desfire_connect (tags[i]);
			if (res < 0) {
				warnx ("Can't connect to Mifare DESFire target.");
				error = EXIT_FAILURE;
				break;
			}

			// Make sure we've at least an EV1 version
			struct mifare_desfire_version_info info;
			res = mifare_desfire_get_version (tags[i], &info);
			if (res < 0) {
				freefare_perror (tags[i], "mifare_desfire_get_version");
				error = 1;
				break;
			}
			
			// bei altem tag überspringen
			if (info.software.version_major < 1) {
				warnx ("Found old DESFire, skipping");
				continue;
			}
			printf ("Found %s with UID %s. ", freefare_get_tag_friendly_name (tags[i]), tag_uid);
			bool do_it = true;
		}
		freefare_free_tags (tags);
		nfc_close (device);
		
		nfc_exit (context);
	}
    exit (error);*/
} /* main() */

//https://github.com/raidolepp/libfreefare/tree/master/libfreefare/examples
