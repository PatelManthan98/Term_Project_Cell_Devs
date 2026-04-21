#pragma once
#include <iostream>
#include <nlohmann/json.hpp>

struct WildfireCellState {
    int state;
    int burn_steps_remaining;

    WildfireCellState() : state(1), burn_steps_remaining(0) {}

    bool operator!=(const WildfireCellState& other) const {
        return state != other.state ||
               burn_steps_remaining != other.burn_steps_remaining;
    }

    friend std::ostream& operator<<(std::ostream& os, const WildfireCellState& s) {
        os << "{state:" << s.state << ", burn:" << s.burn_steps_remaining << "}";
        return os;
    }
};

// JSON loader required by Cadmium
inline void from_json(const nlohmann::json& j, WildfireCellState& s) {
    j.at("state").get_to(s.state);
    j.at("burn_steps_remaining").get_to(s.burn_steps_remaining);
}
