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
  servoAnelar.attach(25, 500, 2400);

  servoIndicador.setPeriodHertz(50);
  servoIndicador.attach(19, 500, 2400);

  servoMinimo.setPeriodHertz(50);
  servoMinimo.attach(27, 500, 2400);

  // posição inicial padrão
  papel();
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();

    if (c != '\n') {
      str[idx++] = c;
    } else {
      str[idx] = '\0';  // Finaliza a string
      idx = 0;

      Serial.print("Recebido: ");
      Serial.println(str);

      if (strlen(str) == 5) {
        // A string representa o status dos dedos na ordem:
        // mínimo, anelar, meio, indicador, polegar
        int minimo_val    = str[0] - '0';
        int anelar_val    = str[1] - '0';
        int meio_val      = str[2] - '0';
        int indicador_val = str[3] - '0';
        int polegar_val   = str[4] - '0';

        // Envia os valores para as funções dos dedos
        minimo(minimo_val);
        anelar(anelar_val);
        meio(meio_val);
        indicador(indicador_val);
        polegar(polegar_val);
      } else {
        Serial.println("Formato inválido");
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
