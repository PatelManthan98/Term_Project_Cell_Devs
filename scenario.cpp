#include "scenario.hpp"
#include <fstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

Scenario loadScenarioFromJSON(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open scenario file: " + path);
    }

    json j;
    file >> j;

    Scenario s;
    s.scenario_name = j.value("scenario_name", "unnamed");
    s.width = j.value("width", 100);
    s.height = j.value("height", 100);
    s.timesteps = j.value("timesteps", 200);
    s.seed = j.value("seed", 42);
    s.wind_x = j.value("wind_x", 0.0);
    s.wind_y = j.value("wind_y", 0.0);
    s.fuel_scale = j.value("fuel_scale", 1.0);
    s.moisture_scale = j.value("moisture_scale", 1.0);

    if (j.contains("incombustible_areas")) {
        for (auto& a : j["incombustible_areas"]) {
            IncombustibleArea area;
            area.x_start = a.value("x_start", 0);
            area.y_start = a.value("y_start", 0);
            area.x_end = a.value("x_end", 0);
            area.y_end = a.value("y_end", 0);
            area.label = a.value("label", "");
            s.incombustible_areas.push_back(area);
        }
    }

    return s;
}
