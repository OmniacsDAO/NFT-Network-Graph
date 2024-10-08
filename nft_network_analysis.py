import os
import time
import random
import csv
import pprint

import requests
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd

from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from matplotlib.ticker import MaxNLocator


load_dotenv()
ETHSCAN_API_KEY = os.getenv("ETHSCAN_API_KEY")
OPENSEA_API_KEY = os.getenv("OPENSEA_API_KEY")
CONTRACT_ADDRESS = "0x11111111384122718f7a44d48290bb70a3a9f793"  # specify address of the NFT contract you want to analyze.


# def fetch_nft_holders(contract_address):
#     """Fetch holders of the NFT."""
#     url = f"https://api.etherscan.io/api?module=token&action=tokenholderlist&contractaddress={contract_address}&apikey={ETHSCAN_API_KEY}"
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#         return response.json().get("result", [])
#     except requests.RequestException as e:
#         print(f"Failed to fetch NFT holders: {e}")
#         return []


def fetch_nft_holders():
    df = pd.read_csv("export-tokenholders.csv")  # local csv file containing token holder addresses
    holders_list = [
        {"TokenHolderAddress": row["HolderAddress"], "TokenHolderQuantity": row["Quantity"]}
        for _, row in df.iterrows()
    ]
    # Return 50 random entries from the list
    return random.sample(holders_list, 50)


def get_eth_balance(wallet_address, max_retries=5):
    """Fetch ETH balance for a wallet with retry logic."""
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={wallet_address}&apikey={ETHSCAN_API_KEY}"
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Check if the response contains an error message
            result = response.json().get("result", "0")
            if "Max calls per sec rate limit reached" in result:
                # print(f"Rate limit error for wallet {wallet_address}: {result}. Retrying in 0.2 second...")
                time.sleep(0.2)
                retries += 1
                continue

            return int(result) / (10 ** 18)

        except requests.RequestException as e:
            print(f"Failed to fetch balance for wallet {wallet_address}: {e}. Retrying in 1 second...")
            time.sleep(0.2)
            retries += 1

    print(f"Failed to fetch balance for wallet {wallet_address} after {max_retries} retries.")
    return 0


def get_transaction_count(wallet_address):
    """Fetch number of transactions for a wallet."""
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={ETHSCAN_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return len(response.json().get("result", []))
    except requests.RequestException as e:
        print(f"Failed to fetch transactions for wallet {wallet_address}: {e}")
        return 0


def get_other_nfts(wallet_address):
    """Fetch NFTs owned by a wallet using OpenSea API."""
    url = f"https://api.opensea.io/api/v2/chain/ethereum/account/{wallet_address}/nfts"
    headers = {"accept": "application/json", "x-api-key": OPENSEA_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return [nft.get("name") for nft in response.json().get("nfts", [])]
    except requests.RequestException as e:
        print(f"Failed to fetch NFTs for wallet {wallet_address}: {e}")
        return []


def get_username(wallet_address):
    """Fetch the username of the wallet from OpenSea API."""
    url = f"https://api.opensea.io/api/v2/accounts/{wallet_address}"
    headers = {"accept": "application/json", "x-api-key": OPENSEA_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("username") or wallet_address[-5:]  # truncated address to last 5 characters (node names)
    except requests.RequestException as e:
        print(f"Failed to fetch username for wallet {wallet_address}: {e}")
        return wallet_address[-5:]


def analyze_wallet(wallet):
    """Analyze data for each wallet."""
    address = wallet["TokenHolderAddress"]
    username = get_username(address)
    eth_balance = get_eth_balance(address)
    tx_count = get_transaction_count(address)
    nfts = get_other_nfts(address)

    return {
        "address": address,
        "username": username,
        "eth_balance": eth_balance,
        "tx_count": tx_count,
        "num_nfts_held": len(nfts),
        "nfts": nfts
    }


def main():
    """Fetch data, analyze and generate graph"""
    # holders = fetch_nft_holders(CONTRACT_ADDRESS)
    holders = fetch_nft_holders()

    # Analyze data for each wallet concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        wallets = list(executor.map(analyze_wallet, holders))

    # Output Wallet Analysis
    print("\n\nWallet Analysis\n---------------")
    # pprint.pprint(wallets, sort_dicts=False)

    # Initialize a dictionary to hold NFTs and their respective owners
    shared_nfts = {}

    # Populate the shared NFTs dictionary
    for wallet in wallets:
        for nft in wallet["nfts"]:
            if nft is not None:
                if nft not in shared_nfts:
                    shared_nfts[nft] = []
                shared_nfts[nft].append(wallet["address"])

    # Filter to keep only NFTs shared among two or more wallets
    shared_nfts = {nft: wallets for nft, wallets in shared_nfts.items() if len(wallets) > 1}

    with open("shared_nfts.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["NFT Name", "Wallet Addresses"])  # Header

        for nft, addresses in shared_nfts.items():
            writer.writerow([nft, ", ".join(addresses)])  # Join wallet addresses with a comma

    print("Shared NFTs have been written to shared_nfts.csv")

    # Initialize the graph
    G = nx.Graph()

    # Add nodes for each wallet
    for wallet in wallets:
        G.add_node(wallet["username"])

    nft_to_wallets = {}

    # Populate the NFT to wallet mapping
    for wallet in wallets:
        for nft in wallet["nfts"]:
            if nft is not None:
                if nft not in nft_to_wallets:
                    nft_to_wallets[nft] = set()
                nft_to_wallets[nft].add(wallet["username"])

    # Add edges based on shared NFT ownership
    shared_nft_counts = {wallet["username"]: 0 for wallet in wallets}
    for nft_wallets in nft_to_wallets.values():
        wallets_list = list(nft_wallets)
        for i in range(len(wallets_list)):
            for j in range(i + 1, len(wallets_list)):
                wallet_i = wallets_list[i]
                wallet_j = wallets_list[j]
                G.add_edge(wallet_i, wallet_j)
                shared_nft_counts[wallet_i] += 1
                shared_nft_counts[wallet_j] += 1

    # Normalize shared NFT counts for color mapping
    max_shared_nfts = max(shared_nft_counts.values()) if shared_nft_counts else 1
    norm = mcolors.Normalize(vmin=0, vmax=max_shared_nfts)
    cmap = plt.get_cmap("YlOrRd")  # Choose a colormap

    # Determine node colors and sizes based on the number of shared NFTs
    node_colors = [cmap(norm(shared_nft_counts[username])) for username in G.nodes()]

    # Create the plot and draw the graph
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.circular_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=100, node_color=node_colors, font_size=6, font_color="black",
            edge_color="gray", ax=ax)

    # Add color bar to indicate the intensity
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes((0.9, 0.15, 0.01, 0.7))
    cbar = plt.colorbar(sm, cax=cbar_ax, label="Number of Shared NFTs")

    cbar.locator = MaxNLocator(integer=True, nbins=5)
    cbar.update_ticks()

    plt.show()


if __name__ == "__main__":
    main()
