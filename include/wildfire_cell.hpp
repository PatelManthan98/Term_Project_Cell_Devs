#pragma once
#include "wildfire_state.hpp"
#include <cadmium/celldevs/grid/cell.hpp>
#include <cmath>
#include <cstdlib>

struct WildfireCell : public cadmium::celldevs::GridCell<WildfireCellState, double> {

    int burn_duration;
    double base_ignition_prob;

    double wind_speed;
    double wind_dir;
    double temperature;
    double humidity;
    double ffmc;

    WildfireCell(
        const cadmium::celldevs::coordinates& id,
        const std::shared_ptr<const cadmium::celldevs::GridCellConfig<WildfireCellState, double>>& config
    ) : GridCell(id, config)
    {
        burn_duration = 8;
        base_ignition_prob = 0.10;

        wind_speed = 0.0;
        wind_dir = 0.0;
        temperature = 20.0;
        humidity = 40.0;
        ffmc = 85.0;

        auto& j = config->rawCellConfig;

        if (j.contains("burn_duration")) j.at("burn_duration").get_to(burn_duration);
        if (j.contains("ignition_prob")) j.at("ignition_prob").get_to(base_ignition_prob);

        if (j.contains("wind_speed")) j.at("wind_speed").get_to(wind_speed);
        if (j.contains("wind_dir")) j.at("wind_dir").get_to(wind_dir);

        if (j.contains("temperature")) j.at("temperature").get_to(temperature);
        if (j.contains("humidity")) j.at("humidity").get_to(humidity);
        if (j.contains("ffmc")) j.at("ffmc").get_to(ffmc);
    }

    double computeIgnitionProb(const cadmium::celldevs::coordinates& nbr) const {
        double p = base_ignition_prob;

        p *= (ffmc / 100.0);
        p *= (1.0 + (temperature - 20.0) * 0.02);
        p *= (1.0 - humidity / 100.0);

       auto my_id = this->getId();
        double dx = nbr[0] - my_id[0];
        double dy = nbr[1] - my_id[1];


        double angle_to_nbr = atan2(dy, dx) * 180.0 / M_PI;
        double diff = fabs(angle_to_nbr - wind_dir);
        if (diff > 180) diff = 360 - diff;

        double wind_factor = 1.0 + (wind_speed / 30.0) * cos(diff * M_PI / 180.0);
        p *= wind_factor;

        if (p < 0.0) p = 0.0;
        if (p > 1.0) p = 1.0;

        return p;
    }

    WildfireCellState localComputation(
        WildfireCellState state,
        const std::unordered_map<cadmium::celldevs::coordinates,
        cadmium::celldevs::NeighborData<WildfireCellState, double>>& neighborhood
    ) const override
    {
        WildfireCellState next = state;

        if (state.state == 2) {
            next.burn_steps_remaining--;
            if (next.burn_steps_remaining <= 0)
                next.state = 3;
            return next;
        }

        if (state.state == 1) {
            for (const auto& [nbr, data] : neighborhood) {
                if (data.state->state == 2) {
                    double p = computeIgnitionProb(nbr);
                    double r = (double)rand() / RAND_MAX;
                    if (r < p) {
                        next.state = 2;
                        next.burn_steps_remaining = burn_duration;
                        return next;
                    }
                }
            }
        }

        return next;
    }

    double outputDelay(const WildfireCellState&) const override {
        return 5.0;
    }
};
