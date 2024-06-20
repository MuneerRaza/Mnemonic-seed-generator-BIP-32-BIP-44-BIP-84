#ifndef CONFIG_HPP
#define CONFIG_HPP

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <algorithm>

class ConfigClass {
public:
    // Paths to legacy, segwit, and native segwit tables
    std::string folder_tables_legacy;
    std::string folder_tables_segwit;
    std::string folder_tables_native_segwit;

    // Number of mnemonics to generate and number of child addresses per path
    uint64_t number_of_generated_mnemonics;
    uint32_t num_child_addresses;

    // Paths to generate flags
    bool generate_path[10];  // Array to store boolean flags for each path

    // Total number of paths
    uint32_t num_paths;

    // Other configuration options
    std::string check_equal_bytes_in_addresses;
    std::string save_generation_result_in_file;
    std::string static_words_generate_mnemonic;

    // CUDA configuration
    uint32_t cuda_grid;
    uint32_t cuda_block;

    // Constructor to initialize default values
    ConfigClass() {
        number_of_generated_mnemonics = 0;
        num_child_addresses = 0;
        num_paths = 10; // Default number of paths
        check_equal_bytes_in_addresses = "no";
        save_generation_result_in_file = "no";
        static_words_generate_mnemonic = "";

        cuda_grid = 0;
        cuda_block = 0;

        for (int i = 0; i < 10; ++i) {
            generate_path[i] = false;
        }
    }

    // Function to parse config file and populate ConfigClass instance
    void parse_config(const std::string& configFile) {
        std::ifstream file(configFile);
        if (!file.is_open()) {
            std::cerr << "Failed to open config file: " << configFile << std::endl;
            return;
        }

        std::string line;
        while (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string key, value;
            if (std::getline(iss, key, '=') && std::getline(iss, value)) {
                trim(key);
                trim(value);
                if (key == "folder_tables_legacy") {
                    folder_tables_legacy = value;
                } else if (key == "folder_tables_segwit") {
                    folder_tables_segwit = value;
                } else if (key == "folder_tables_native_segwit") {
                    folder_tables_native_segwit = value;
                } else if (key == "number_of_generated_mnemonics") {
                    number_of_generated_mnemonics = std::stoull(value);
                } else if (key == "num_child_addresses") {
                    num_child_addresses = std::stoul(value);
                } else if (key == "num_paths") {
                    num_paths = std::stoul(value);
                } else if (key == "path_m0_x") {
                    generate_path[0] = (value == "yes");
                } else if (key == "path_m1_x") {
                    generate_path[1] = (value == "yes");
                } else if (key == "path_m0_0_x") {
                    generate_path[2] = (value == "yes");
                } else if (key == "path_m0_1_x") {
                    generate_path[3] = (value == "yes");
                } else if (key == "path_m44h_0h_0h_0_x") {
                    generate_path[4] = (value == "yes");
                } else if (key == "path_m44h_0h_0h_1_x") {
                    generate_path[5] = (value == "yes");
                } else if (key == "path_m49h_0h_0h_0_x") {
                    generate_path[6] = (value == "yes");
                } else if (key == "path_m49h_0h_0h_1_x") {
                    generate_path[7] = (value == "yes");
                } else if (key == "path_m84h_0h_0h_0_x") {
                    generate_path[8] = (value == "yes");
                } else if (key == "path_m84h_0h_0h_1_x") {
                    generate_path[9] = (value == "yes");
                } else if (key == "check_equal_bytes_in_addresses") {
                    check_equal_bytes_in_addresses = value;
                } else if (key == "save_generation_result_in_file") {
                    save_generation_result_in_file = value;
                } else if (key == "static_words_generate_mnemonic") {
                    static_words_generate_mnemonic = value;
                } else if (key == "cuda_grid") {
                    cuda_grid = std::stoul(value);
                } else if (key == "cuda_block") {
                    cuda_block = std::stoul(value);
                } else {
                    std::cerr << "Unknown config key: " << key << std::endl;
                }
            }
        }

        file.close();
    }

private:
    // Function to trim whitespace from strings
    void trim(std::string& str) {
        str.erase(str.begin(), std::find_if(str.begin(), str.end(), [](unsigned char ch) { return !std::isspace(ch); }));
        str.erase(std::find_if(str.rbegin(), str.rend(), [](unsigned char ch) { return !std::isspace(ch); }).base(), str.end());
    }
};

#endif // CONFIG_HPP
