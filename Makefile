clean:
     rm zuul

all: 
   gcc -o zuul zuul.c -lnfc -lsqlite3 -lwiringPi -o3
