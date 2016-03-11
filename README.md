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
1 mal	red		Token kein DesFire/EV1 oder Version zu alt
2 mal	red		Token nicht in db 	[logged D(enied)]
long green			Token erkannt tür öffnet
long yellow		wird berechnet


gcc -o zuul7 3rd_try.c -lnfc -lsqlite3 -lwiringPi

http://stackoverflow.com/questions/12207684/how-do-i-terminate-a-thread-in-c11
http://en.cppreference.com/w/cpp/thread