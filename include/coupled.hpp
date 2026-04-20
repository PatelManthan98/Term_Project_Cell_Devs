#pragma once

#include <cadmium/celldevs/cell/cell.hpp>
#include <cadmium/celldevs/cell/grid_cell.hpp>
#include <cadmium/celldevs/coupled/grid_coupled.hpp>
#include <cadmium/celldevs/utils/grid_utils.hpp>

#include "wildfire_cell.hpp"
#include "wildfire_state.hpp"
#include "scenario.hpp"

using namespace cadmium::celldevs;

class WildfireCoupled {
public:
    static auto create_model(const Scenario& scenario) {
        GridDimensions dims(scenario.rows, scenario.cols);

        std::map<std::string, WildfireState> initial_states;
        for (int r = 0; r < scenario.rows; r++) {
            for (int c = 0; c < scenario.cols; c++) {
                std::string id = std::to_string(r) + "_" + std::to_string(c);
                initial_states[id] = scenario.grid[r][c];
            }
        }

        return grid_coupled<WildfireCell, WildfireState>(
            "wildfire_grid",
            dims,
            initial_states
        );
    }
};
