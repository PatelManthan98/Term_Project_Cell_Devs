#ifndef JSON_GRID_LOGGER_HPP
#define JSON_GRID_LOGGER_HPP
#include <cadmium/logger/logger.hpp>

#include <cadmium/json/json.hpp>
#include <fstream>
#include <memory>

template<typename MODEL, typename STATE>
class JsonGridLogger : public cadmium::Logger {
private:    
    std::ofstream file;
    nlohmann::json root;
    std::shared_ptr<MODEL> model;

public:
    JsonGridLogger(const std::string& path, std::shared_ptr<MODEL> m)
        : model(std::move(m))
    {
        file.open(path);
        root["timesteps"] = nlohmann::json::array();
    }

    void start() override {
        // nothing special
    }

    void stop() override {
        if (file.is_open()) {
            file << root.dump(2);
            file.close();
        }
    }

    // Called by RootCoordinator before each transition
    void logTime(double t) override {
        nlohmann::json step;
        step["time"] = t;
        step["cells"] = nlohmann::json::array();

        // Assumes MODEL exposes getCells() returning map<coordinates, shared_ptr<Cell>>
        for (auto& [coord, cell] : model->getCells()) {
            const STATE& s = cell->state;

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

    // Required by base class, but we don't need them for grid logging
    void logOutput(double, long, const std::string&,
                   const std::string&, const std::string&) override {
        // ignore port-level outputs
    }

    void logState(double, long, const std::string&,
                  const std::string&) override {
        // we already log full state via logTime()
    }
};

#endif
