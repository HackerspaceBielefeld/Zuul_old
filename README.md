# Zuul!

Gozars gate keeper

Pinbelegung
Pin 2			5VCC
Pin 6			GND
Pin 7			NF-AMP Power
Pin 8			LED R
Pin 10		LED G
Pin 12		LED B
Pin 14		LED GND
Pin 18		Dooropener
Pin 19		MOSI
Pin 21		MISO
Pin 22		Ring
Pin 23		CLK
Pin 24		CE0

Blink Fehlercode
1 mal	red	Token kein DesFire
2 mal	red	Token nicht in db 	[logged D(enied)]

gcc -o zuul7 3rd_try.c -lnfc -lsqlite3 -lwiringPi
