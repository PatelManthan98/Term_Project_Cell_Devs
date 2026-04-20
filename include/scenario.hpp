#pragma once
#include <string>
#include <vector>

struct IncombustibleArea {
    int x_start;
    int y_start;
    int x_end;
    int y_end;
    std::string label;
};

struct Scenario {
    std::string scenario_name;
    int width;
    int height;
    int timesteps;
    int seed;
    double wind_x;
    double wind_y;
    double fuel_scale;
    double moisture_scale;
    std::vector<IncombustibleArea> incombustible_areas;
};

Scenario loadScenarioFromJSON(const std::string& path);
