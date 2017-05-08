// -*- mode:c++ -*-

module drobotsCoordinados{

  struct Point {
    int x;
    int y;
  };

  interface Coordinacion{
    void EnemigoDetectado(int angulo);
    void PosicionDetector(Point destino);
  };
};
