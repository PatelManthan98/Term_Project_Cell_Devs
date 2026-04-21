#include <cadmium/celldevs/grid/coupled.hpp>
#include <cadmium/core/logger/csv.hpp>
#include <cadmium/core/simulation/root_coordinator.hpp>

#include "wildfire_cell.hpp"
#include "wildfire_state.hpp"

using namespace cadmium::celldevs;

std::shared_ptr<GridCell<WildfireCellState, double>> addCell(
    const coordinates& id,
    const std::shared_ptr<const GridCellConfig<WildfireCellState, double>>& cfg
) {
    return std::make_shared<WildfireCell>(id, cfg);
}

int main(int argc, char** argv) {
    std::string config = (argc > 1) ? argv[1] : "scenario.json";
    double sim_time = (argc > 2) ? std::stod(argv[2]) : 500.0;

    auto model = std::make_shared<GridCellDEVSCoupled<WildfireCellState, double>>(
        "wildfire",
        addCell,
        config
    );
    model->buildModel();

    auto root = cadmium::RootCoordinator(model);
    auto logger = std::make_shared<cadmium::CSVLogger>("grid_log.csv", ";");
    root.setLogger(logger);

    root.start();
    root.simulate(sim_time);
    root.stop();

    return 0;
}
