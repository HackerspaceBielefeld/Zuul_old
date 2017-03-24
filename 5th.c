#include "config.h"

#include <err.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <nfc/nfc.h>

#include <freefare.h>

// müsste der key sein fürs file system
uint8_t key_data_picc[8] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };	
// verrechnungsschlüssel wird mit uid verrechnet
u_int8_t encryption_key[8] = { 0x42, 0x13, 0x37, 0x42, 0x13, 0x37, 0x12, 0x34 };
// key für Dir
	// Str Zuul-HSB in hex
uint8_t key_for_zuul[8] = { 0x5a, 0x75, 0x75, 0x6c, 0x2d, 0x48, 0x53, 0x42 };

// Default Mifare DESFire ATS
uint8_t new_ats[] = { 0x06, 0x75, 0x77, 0x81, 0x02, 0x80 };

struct {
	bool interactive;
} configure_options = {
	.interactive = true
};// nur für terminal mode

u_int8_t *getKeyFromUID(u_int8_t *uid) {
	int n = sizeof(uid) / sizeof(uid[0]);
	int i = 0;
	u_int8_t ret[n];
	for(i=0;i<n;i++) {
		if(uid[i] <= 0x80) {
			ret[i] = uid[i] + encryption_key[i];
		}else{
			ret[i] = uid[i] - encryption_key[i];
		}
	}
	return ret;
}

int main(int argc, char *argv[])
{
	//int ch; //???
	int error = EXIT_SUCCESS;
	nfc_device *device = NULL; // geöffneter Leser
	MifareTag *tags = NULL; //gefundene Token

	nfc_connstring devices[8]; // gefundene Leser
	size_t device_count;

	nfc_context *context;
	nfc_init (&context);

	// zählt gefundene Tags
	device_count = nfc_list_devices (context, devices, 8);
	if (device_count <= 0)
		errx (EXIT_FAILURE, "No NFC device found.");
		// fehler wenn kein dev gfunden

	for (size_t d = 0; (!error) && (d < device_count); d++) {
		// versuche tag zu öffnen
		device = nfc_open (context, devices[d]);
		if (!device) {
			warnx ("nfc_open() failed.");
			error = EXIT_FAILURE;
			continue;
		}

		// listet gefundene tags auf
		tags = freefare_get_tags (device);
		if (!tags) {
			nfc_close (device);
			errx (EXIT_FAILURE, "Error listing Mifare DESFire tags.");
		}

		for (int i = 0; (!error) && tags[i]; i++) {
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

			if (configure_options.interactive) {
				printf ("Change ATS? [yN] ");
				fgets (buffer, BUFSIZ, stdin);
				do_it = ((buffer[0] == 'y') || (buffer[0] == 'Y'));
			} else {
				printf ("\n");
			}

			if (do_it) {
				// erzeugt neuen key
				MifareDESFireKey key_picc = mifare_desfire_des_key_new_with_version (key_data_picc);
				// authentifiziert sich mit key
				res = mifare_desfire_authenticate (tags[i], 0, key_picc);
				if (res < 0) {
					freefare_perror (tags[i], "mifare_desfire_authenticate");
					error = EXIT_FAILURE;
					break;
				}
				//gibt speicher frei oder so ???
				mifare_desfire_key_free (key_picc);
				//setzt standard ATS (zur initialisierung???)
				res = mifare_desfire_set_ats (tags[i], new_ats);
				if (res < 0) {
					freefare_perror (tags[i], "mifare_desfire_set_ats");
					error = EXIT_FAILURE;
					break;
				}
			}
			// trennt verbindung
			mifare_desfire_disconnect (tags[i]);
			//speicher freigeben
			free (tag_uid);
		}

		freefare_free_tags (tags);
		nfc_close (device);
    }
    nfc_exit (context);
    exit (error);
} /* main() */

//https://github.com/raidolepp/libfreefare/tree/master/libfreefare/examples
