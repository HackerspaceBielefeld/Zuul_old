#include <stdlib.h>
#include <nfc/nfc.h>

static void print_hex(const uint8_t *pbtData, const size_t szBytes) {
	size_t  szPos;
 
	for (szPos = 0; szPos < szBytes; szPos++) {
		printf("%02x  ", pbtData[szPos]);
	}
}

int main(int argc, const char *argv[])
{
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
		printf("NFCID-Länge: ");
		print_hex(nt.nti.nai.szUidLen);
    		printf("NFCID: ");
    		print_hex(nt.nti.nai.abtUid);

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
