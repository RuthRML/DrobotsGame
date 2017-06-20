// -*- mode:c++ -*-

module drobotsCoordinados{

  interface Coordinacion{
    void enemigoDetectado(int angulo);
    void posicionDetector(int posx, int posy);
    int localizacionx();
    int localizaciony();
  };
};
