#ifndef JSON_LOGGER_HPP
#define JSON_LOGGER_HPP

#include <fstream>
#include <string>
#include <cadmium/json/json.hpp>

class JSONLogger {
    std::ofstream file;
    nlohmann::json root;

public:
    JSONLogger(const std::string& path) {
        file.open(path);
        root["timesteps"] = nlohmann::json::array();
    }

    template<typename State, typename GridType>
    void log(double time, const GridType& grid) {
        nlohmann::json step;
        step["time"] = time;
        step["cells"] = nlohmann::json::array();

        for (auto& [coord, cell] : grid.cells) {
            const State& s = cell->state;

            nlohmann::json c;
            c["row"]       = coord[0];
            c["col"]       = coord[1];
            c["burned"]    = s.burned;
            c["fuel"]      = s.fuel;
            c["moisture"]  = s.moisture;
            c["elevation"] = s.elevation;

            step["cells"].push_back(c);
        }

        root["timesteps"].push_back(step);
    }

    ~JSONLogger() {
        if (file.is_open()) {
            file << root.dump(2);
            file.close();
        }
    }
};

#endif
