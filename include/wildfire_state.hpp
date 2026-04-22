#pragma once
#include <iostream>
#include <nlohmann/json.hpp>

struct WildfireCellState {
    int    state;                  // 0=non-flammable, 1=unburned, 2=burning, 3=burned
    int    fuel_type;              // 0-4 (see above)
    double elevation;              // metres above sea level (static per cell)
    double moisture;               // fuel moisture content 0.0-1.0 (static per cell)
    double intensity;              // fire intensity 0.0-1.0 (set on ignition)
    int    burn_steps_remaining;

    WildfireCellState()
        : state(1), fuel_type(3), elevation(400.0),
          moisture(0.30), intensity(0.0), burn_steps_remaining(0) {}

    // Only dynamic fields trigger a state-change notification
    bool operator!=(const WildfireCellState& o) const {
        return state                != o.state               ||
               burn_steps_remaining != o.burn_steps_remaining ||
               intensity            != o.intensity;
    }

    friend std::ostream& operator<<(std::ostream& os, const WildfireCellState& s) {
        os << "{state:"     << s.state
           << ",fuel:"      << s.fuel_type
           << ",elev:"      << s.elevation
           << ",moist:"     << s.moisture
           << ",intensity:" << s.intensity
           << ",burn:"      << s.burn_steps_remaining << "}";
        return os;
    }
};


inline void from_json(const nlohmann::json& j, WildfireCellState& s) {
    if (j.contains("state"))                 j.at("state").get_to(s.state);
    if (j.contains("fuel_type"))             j.at("fuel_type").get_to(s.fuel_type);
    if (j.contains("elevation"))             j.at("elevation").get_to(s.elevation);
    if (j.contains("moisture"))              j.at("moisture").get_to(s.moisture);
    if (j.contains("intensity"))             j.at("intensity").get_to(s.intensity);
    if (j.contains("burn_steps_remaining"))  j.at("burn_steps_remaining").get_to(s.burn_steps_remaining);
}