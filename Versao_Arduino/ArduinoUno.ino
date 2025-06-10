#define NumBotoes 5
#define NumLeds 4

#define BLACK_BUTTOM 6
#define RED_BUTTOM 5
#define YELLOW_BUTTOM 4
#define BLUE_BUTTOM 3
#define GREEN_BUTTOM 2
#define RED_LED 13
#define YELLOW_LED 12
#define BLUE_LED 11
#define GREEN_LED 10

#define ON 1
#define OFF 0

int LEDS = ON;
int botoes[NumBotoes] = {RED_BUTTOM, YELLOW_BUTTOM, BLUE_BUTTOM, GREEN_BUTTOM, BLACK_BUTTOM};
int leds[NumLeds] = {RED_LED, YELLOW_LED, BLUE_LED, GREEN_LED};

void setup() {
  for (int i = 0; i < NumBotoes; i++) 
    pinMode(botoes[i], INPUT_PULLUP);
  for (int i = 0; i < NumLeds; i++) 
    pinMode(leds[i], OUTPUT);

  Serial.begin(9600);
  randomSeed(analogRead(0));
}

void loop() {
  
  int pressionarBotao = DetectarBotao();

  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();  // Remove espaços e quebras extras
    if (comando == "OFF")
      LEDS = OFF;
    if (comando == "ON")
      LEDS = ON;
    Serial.println(comando);
  }

  switch(pressionarBotao){
    case RED_BUTTOM:
      Serial.println("VERMELHO");
      if (LEDS)
        acenderLed(RED_LED);
      else delay(100);
      break;
    case YELLOW_BUTTOM:
      Serial.println("AMARELO");
      if (LEDS)
        acenderLed(YELLOW_LED);
      else delay(100);
      break;
    case BLUE_BUTTOM:
      Serial.println("AZUL");
      if (LEDS)
        acenderLed(BLUE_LED);
      else delay(100);
      break;
    case GREEN_BUTTOM:
      Serial.println("VERDE");
      if (LEDS)
        acenderLed(GREEN_LED);
      else delay(100);
      break;
    case BLACK_BUTTOM:
      Serial.println("PRETO");
      delay(200);
      break;
  }

  delay(100);
}

void acenderLed(int LED) {
  digitalWrite(LED, HIGH);
  delay(250);
  digitalWrite(LED, LOW);
}

int DetectarBotao(){
  for (int i = 0; i < NumBotoes; i++) 
    if (digitalRead(botoes[i]) == LOW) 
      return botoes[i];
  return -1;
}
