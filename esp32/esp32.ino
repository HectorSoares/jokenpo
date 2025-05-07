#include <ESP32Servo.h>

char c;
char str[255];
uint8_t idx = 0;

Servo servoMeio; // MEIO
Servo servoPolegar; // POLEGAR
Servo servoAnelar; // ANELAR
Servo servoIndicador; // INDICADOR
Servo servoMinimo; // MINIMO

void setup() {
  Serial.begin(115200);

  servoMeio.setPeriodHertz(50);
  servoMeio.attach(32, 500, 2400);

  servoPolegar.setPeriodHertz(50);
  servoPolegar.attach(16, 500, 2400);

  servoAnelar.setPeriodHertz(50);
  servoAnelar.attach(17, 500, 2400);

  servoIndicador.setPeriodHertz(50);
  servoIndicador.attach(19, 500, 2400);

  servoMinimo.setPeriodHertz(50);
  servoMinimo.attach(27, 500, 2400);

  // posição inicial padrão
  papel();
}

void loop() {
  if (Serial.available() > 0) {
    c = Serial.read();

    if (c != '\n') {
      str[idx++] = c;
    } else {
      str[idx] = '\0';
      idx = 0;

      Serial.print("Received: ");
      Serial.println(str);

      if (strcmp(str, "PEDRA") == 0) {
        pedra();
      } else if (strcmp(str, "TESOURA") == 0) {
        tesoura();
      } else if (strcmp(str, "PAPEL") == 0) {
        papel();
      } 
    }
  }
}

void pedra() {
    polegar(0);
    indicador(0);
    meio(0);
    anelar(0);
    minimo(0);
}

void papel() {
    polegar(1);
    indicador(1);
    meio(1);
    anelar(1);
    minimo(1);
}

void tesoura() {
    polegar(0);
    indicador(1);
    meio(1);
    anelar(0);
    minimo(0);
}

void minimo(int flag){
  servoMinimo.write(!flag ? 180 : 0);
}

void anelar(int flag){
  servoAnelar.write(!flag ? 180 : 0);
}

void meio(int flag){
  servoMeio.write(!flag ? 180 : 0);
}

void indicador(int flag){
  servoIndicador.write(flag ? 180 : 0);
}

void polegar(int flag){
  servoPolegar.write(flag ? 180 : 0);
}
