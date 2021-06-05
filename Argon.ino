bool currentMotion=false;

void setup() {

  pinMode(D4, INPUT);
  Particle.variable("motion",currentMotion);

}


void loop() {

  if ( digitalRead(D4) == HIGH) {
            Particle.publish("data","Active",PRIVATE);
            
            currentMotion=true;
            
             

  }
  else {
      Particle.publish("InActive!");
    
     currentMotion=false;
      
    }
    
    delay(1000);
    //Particle.function("MOTION", MOTION);
  
}

