# NFT Holders Network Analysis

This project is a Python script designed to analyze and visualize the network of NFT holders for a specific smart contract on the Ethereum blockchain. It fetches data from Etherscan and OpenSea APIs to identify the owners of NFTs, their transaction counts, ETH balances, and other NFTs they hold. A network graph is generated to illustrate relationships between wallets based on shared NFT ownership. A csv file is also generated to display NFT names and shared ownerships. This file can be used for further analysis, providing insights into NFT distribution, influential holders, and community clustering within the NFT ecosystem.

## Features

- Fetch NFT holders for a specified smart contract.
- Obtain NFTs owned by each wallet.
- Generate a network graph to visualize the connections between wallets based on shared NFT ownership.
- Generate a csv file of shared NFTs ownership among wallets.

## Prerequisites

- Python 3.x
- Required Python packages: `requests`, `networkx`, `matplotlib`, `dotenv`, `pandas`
- Etherscan API Pro Key
- OpenSea API Key

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/cobbyrecks/nft-network-graph.git
   cd nft-network-graph
   ```
   
2. **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
   ```
   
3. **Set up environment variables:**
    
    Create a `.env` file in the project directory and add your API keys:

    ```plaintext
    ETHSCAN_API_KEY=your_etherscan_api_key
    OPENSEA_API_KEY=your_opensea_api_key
   ```

## Usage

To run the script, execute:

   ```bash
   python nft_network_analysis.py
   ```

### Script Flow
1. **Fetch NFT Holders:** Retrieves a list of wallets holding the specified NFT using the Etherscan API.
2. **Analyze Each Wallet:** Fetches ETH balance, transaction count, other NFTs, and OpenSea usernames for each wallet.
3. **Generate Network Graph:** Constructs and visualizes a network graph where nodes represent wallets, and edges indicate shared NFT ownership.
4. **Generate CSV File:** Generates a csv file to display shared NFTs among wallet addresses.

## Configuration

**Smart Contract Address:** Modify the CONTRACT_ADDRESS variable in the script with the address of the NFT contract you want to analyze.

## Example Output

1. **Wallet Analysis:** Displays detailed information about each wallet, including ETH balance, transaction count, and NFTs held.
2. **Overall Statistics:** Provides aggregated statistics across all analyzed wallets.
3. **Network Graph:** Visualizes the relationships between wallets based on shared NFT ownership.

## License

This project is licensed under the MIT License.
