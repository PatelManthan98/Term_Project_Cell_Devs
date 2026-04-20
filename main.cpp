#include <iostream>
#include <string>
#include <filesystem>

#include "scenario.hpp"
#include "coupled.hpp"
#include "json_grid_logger.hpp"

#include <cadmium/engine/pdevs_dynamic_runner.hpp>

namespace fs = std::filesystem;

int main(int argc, char** argv) {

    // Must provide a JSON file
    if (argc < 2) {
        std::cerr << "Usage: ./WildfireSpreadSimulator <scenario.json>\n";
        return 1;
    }

    std::string json_file = argv[1];
    Scenario scenario;

    // Load scenario JSON
    try {
        scenario = loadScenarioFromJSON(json_file);
        std::cout << "Loaded scenario: " << scenario.scenario_name << "\n";
        std::cout << "Grid: " << scenario.width << " x " << scenario.height << "\n";
        std::cout << "Timesteps: " << scenario.timesteps << "\n";
        std::cout << "Wind: (" << scenario.wind_x << ", " << scenario.wind_y << ")\n";
        std::cout << "Fuel scale: " << scenario.fuel_scale << "\n";
        std::cout << "Moisture scale: " << scenario.moisture_scale << "\n";
        std::cout << "Incombustible areas: " << scenario.incombustible_areas.size() << "\n";
    }
    catch (const std::exception& e) {
        std::cerr << "Error loading scenario: " << e.what() << "\n";
        return 1;
    }

    // Output directory
    std::string outdir = "simulation_results/" + scenario.scenario_name;
    fs::create_directories(outdir);

    // Build wildfire model from scenario
    auto model = std::make_shared<WildfireCoupled>("wildfire", scenario);

    // Logger
    JsonGridLogger logger(outdir + "/wildfire.csv", scenario.width, scenario.height);

    // Runner
    cadmium::dynamic::engine::runner runner(model, scenario.seed);

    // Run simulation
    for (int t = 0; t < scenario.timesteps; t++) {
        runner.run_until(t + 1);
        logger.log_grid(model->get_grid());
    }

    // Summary
    logger.write_summary(outdir + "/summary.csv");

    std::cout << "Simulation finished. Outputs:\n";
    std::cout << "  " << outdir << "/wildfire.csv\n";
    std::cout << "  " << outdir << "/summary.csv\n";

    return 0;
}
