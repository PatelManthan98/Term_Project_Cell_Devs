#pragma once
#include "wildfire_state.hpp"
#include <cadmium/celldevs/asymm/cell.hpp>
#include <cadmium/celldevs/asymm/config.hpp>
#include <array>
#include <cmath>
#include <cstdlib>

struct FuelProperties {
    double ignition_mod;
    int    burn_steps;
    double intensity;
};

static constexpr std::array<FuelProperties, 5> FUEL_PROPS = {{
    { 0.00,  0, 0.00 },   // 0 water/road  — non-flammable firebreak
    { 1.80,  4, 0.40 },   // 1 grass       — fast, low intensity
    { 1.30,  7, 0.65 },   // 2 shrub       — moderate
    { 1.00, 10, 0.90 },   // 3 forest      — slow, high intensity
    { 0.75,  8, 1.00 },   // 4 urban       — high intensity once ignited
}};

struct WildfireAsymmCell : public cadmium::celldevs::AsymmCell<WildfireCellState, double> {

    double base_ignition_prob;
    double temperature;
    double humidity;
    double ffmc;

    WildfireAsymmCell(
        const std::string& id,
        const std::shared_ptr<const cadmium::celldevs::AsymmCellConfig<WildfireCellState, double>>& config
    ) : AsymmCell<WildfireCellState, double>(id, config)
    {
        base_ignition_prob = 0.10;
        temperature        = 22.0;
        humidity           = 40.0;
        ffmc               = 85.0;
        const auto& j = config->rawCellConfig;
        if (j.contains("ignition_prob")) j.at("ignition_prob").get_to(base_ignition_prob);
        if (j.contains("temperature"))   j.at("temperature").get_to(temperature);
        if (j.contains("humidity"))      j.at("humidity").get_to(humidity);
        if (j.contains("ffmc"))          j.at("ffmc").get_to(ffmc);
    }

    [[nodiscard]] WildfireCellState localComputation(
        WildfireCellState state,
        const std::unordered_map<std::string,
              cadmium::celldevs::NeighborData<WildfireCellState, double>>& neighborhood
    ) const override {
        WildfireCellState next = state;

        if (state.fuel_type == 0 || state.state == 0) return next;

        if (state.state == 2) {
            next.burn_steps_remaining--;
            if (next.burn_steps_remaining <= 0) { next.state = 3; next.intensity = 0.0; }
            return next;
        }

        if (state.state == 1) {
            int ft = std::max(0, std::min(4, state.fuel_type));
            if (FUEL_PROPS[ft].ignition_mod == 0.0) return next;

            double p_base = base_ignition_prob
                * (ffmc / 100.0)
                * (1.0 + (temperature - 20.0) * 0.02)
                * std::max(0.01, 1.0 - humidity / 100.0)
                * FUEL_PROPS[ft].ignition_mod
                * (1.0 - state.moisture * 0.85);

            for (const auto& [nbrId, data] : neighborhood) {
                if (data.state->state == 2) {
                    double vic = static_cast<double>(data.vicinity);
                    if (vic <= 0.0) continue;
                    double p = std::min(1.0, p_base * vic * (0.4 + 0.6 * data.state->intensity));
                    if (static_cast<double>(rand()) / RAND_MAX < p) {
                        next.state                = 2;
                        next.burn_steps_remaining = FUEL_PROPS[ft].burn_steps;
                        next.intensity            = FUEL_PROPS[ft].intensity;
                        return next;
                    }
                }
            }
        }
        return next;
    }

    [[nodiscard]] double outputDelay(const WildfireCellState& s) const override {
        return (s.state == 2) ? 2.0 : 5.0;
    }
};