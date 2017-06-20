#include <crobots.ice>

module drobots {
  interface RobotFactory{
    RobotController* make(Robot* bot, int cont);
    DetectorController* makeDetector();
  };

  interface DetectorFactory{
    DetectorController* makeDetector();
  };
};
