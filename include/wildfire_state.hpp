#ifndef WILDFIRE_STATE_HPP
#define WILDFIRE_STATE_HPP

struct WildfireState {
    double burned;     // fraction [0,1] already burned
    double fuel;       // remaining fuel units
    double moisture;   // moisture factor [0,1] reduces spread
    double elevation;  // elevation (unused in simple model)

    WildfireState()
        : burned(0.0), fuel(1.0), moisture(0.0), elevation(0.0) {}

    WildfireState(double b, double f, double m, double e)
        : burned(b), fuel(f), moisture(m), elevation(e) {}
};

#endif // WILDFIRE_STATE_HPP
