MifareDESFireKey default_key = mifare_desfire_des_key_new_with_version (null_key_data);
res = mifare_desfire_authenticate (tags[i], 0, default_key);
if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_authenticate");
	error = EXIT_FAILURE;
	break;
}
mifare_desfire_key_free (default_key);

MifareDESFireKey new_key = mifare_desfire_des_key_new (new_key_data);
mifare_desfire_key_set_version (new_key, NEW_KEY_VERSION);
res = mifare_desfire_set_default_key (tags[i], new_key);
// https://manned.org/mifare_desfire_create_application.3
free (new_key);
if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_set_default_key");
	error = EXIT_FAILURE;
	break;
}

/*
 * Perform some tests to ensure the function actually worked
 * (it's hard to create a unit-test to do so).
 */

MifareDESFireAID aid = mifare_desfire_aid_new (0x112233);
res = mifare_desfire_create_application (tags[i], aid, 0xFF, 1);

if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_create_application");
	error = EXIT_FAILURE;
	break;
}

res = mifare_desfire_select_application (tags[i], aid);
if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_select_application");
	error = EXIT_FAILURE;
	break;
}

uint8_t version;
res = mifare_desfire_get_key_version (tags[i], 0, &version);
if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_get_key_version");
	error = EXIT_FAILURE;
	break;
}

if (version != NEW_KEY_VERSION) {
	fprintf (stderr, "Wrong key version: %02x (expected %02x).\n", version, NEW_KEY_VERSION);
	error = EXIT_FAILURE;
	/* continue */
}

new_key = mifare_desfire_des_key_new (new_key_data);
res = mifare_desfire_authenticate (tags[i], 0, new_key);
free (new_key);
if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_authenticate");
	error = EXIT_FAILURE;
	break;
}

free (aid);

/* Resetdefault settings */

res = mifare_desfire_select_application (tags[i], NULL);
if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_select_application");
	error = EXIT_FAILURE;
	break;
}

default_key = mifare_desfire_des_key_new (null_key_data);

res = mifare_desfire_authenticate (tags[i], 0, default_key);
if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_authenticate");
	error = EXIT_FAILURE;
	break;
}

res = mifare_desfire_set_default_key (tags[i], default_key);
if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_set_default_key");
	error = EXIT_FAILURE;
	break;
}

mifare_desfire_key_free (default_key);

/* Wipeout the card */

res = mifare_desfire_format_picc (tags[i]);
if (res < 0) {
	freefare_perror (tags[i], "mifare_desfire_format_picc");
	error = EXIT_FAILURE;
	break;
}