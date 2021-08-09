module.exports = {
    networks: {
        development: {
            host: "127.0.0.1",     // Localhost (default: none)
            port: 8545,            // Standard Ethereum port (default: none)
            network_id: "*",       // Any network (default: none)
            gas: 1000 * 1000 * 1000 * 1000
        },
    },

    mocha: {
        timeout: 1000000
    },

    compilers: {
        solc: {
            version: "0.6.12",      // Fetch exact version from solc-bin (default: truffle's version)
            settings: {
                optimizer: {
                    enabled: true,
                    runs: 200
                }
            }
        }
    },

    db: {
        enabled: false
    }
};
