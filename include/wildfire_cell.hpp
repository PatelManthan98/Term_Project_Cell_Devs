#pragma once

#include <cadmium/celldevs/cell/cell.hpp>
#include <cadmium/celldevs/cell/grid_cell.hpp>
#include <cadmium/celldevs/cell/msg.hpp>

#include "wildfire_state.hpp"
#include "scenario.hpp"

using namespace cadmium::celldevs;

class WildfireCell : public Cell<WildfireState> {
public:
    WildfireCell() = default;

    WildfireCell(const WildfireState& state, const std::string& id)
        : Cell<WildfireState>(state, id) {}

    WildfireState local_computation(const WildfireState& state,
                                    const std::vector<WildfireState>& neighbors) const override {
        WildfireState new_state = state;

        // Example wildfire logic (replace with your actual rules)
        if (state.burning) {
            new_state.burning = false;
            new_state.burned = true;
        } else {
            for (const auto& n : neighbors) {
                if (n.burning && !state.burned) {
                    new_state.burning = true;
                    break;
                }
            }
        }

        return new_state;
    }
};
