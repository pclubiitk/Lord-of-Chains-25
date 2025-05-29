#!/usr/bin/env python3
"""
Bitcoin PoW Blockchain - Network Wallet Viewer
A professional wallet interface for viewing blockchain network balances and statistics
"""

import json
import os

def view_node_balances():
    """Display network wallet balances and statistics in a professional wallet interface"""
    
    blockchain_dir = "blockchain_data"
    network_summary_file = os.path.join(blockchain_dir, "network_summary.json")
    
    if not os.path.exists(network_summary_file):
        print("ERROR: No blockchain network data found. Please run the blockchain simulation first.")
        return
    
    print("Bitcoin PoW Blockchain - Network Wallet Summary")
    print("=" * 65)
    
    # Load network summary
    with open(network_summary_file, 'r') as f:
        network_data = json.load(f)
    
    # Display network information
    network_info = network_data['network_info']
    print("Network Stats:")
    print(f"   Total Nodes: {network_info['total_nodes']}")
    print(f"   Total Miners: {network_info['total_miners']}")
    print(f"   Blockchain Length: {network_info['blockchain_length']} blocks")
    print(f"   Difficulty: {network_info['difficulty']}")
    print(f"   Pending Transactions: {network_info['pending_transactions']}")
    print()
    
    # Display node balances
    print("Wallet Balances:")
    print("-" * 65)
    print(f"{'Wallet ID':<15} {'Type':<8} {'Balance':<15} {'Status'}")
    print("-" * 65)
    
    total_balance = 0
    miners_count = 0
    nodes_count = 0
    
    # Sort nodes by balance (highest first) for better wallet display
    sorted_nodes = sorted(network_data['nodes'], key=lambda x: x['balance'], reverse=True)
    
    for node in sorted_nodes:
        node_name = node['name']
        node_type = node['type']
        balance = node['balance']
        total_balance += balance
        
        # Count node types
        if node_type == "Miner":
            miners_count += 1
            status_icon = "[M]"
            status_text = "Mining Active"
        else:
            nodes_count += 1
            status_icon = "[N]"
            status_text = "Online"
        
        # Determine wallet status based on balance patterns
        if balance > 50.0:
            if node_type == "Miner":
                status_text = "Earned Rewards"
            else:
                status_text = "Received Funds"
        elif balance < 50.0:
            status_text = "Sent Funds"
        elif balance == 50.0:
            status_text = "Genesis Balance"
        
        # Format balance display
        balance_display = f"{balance:.1f} BTC"
        
        print(f"{node_name:<15} {node_type:<8} {balance_display:<15} {status_icon} {status_text}")
    
    print("-" * 65)
    print(f"{'TOTAL SUPPLY':<15} {'NETWORK':<8} {total_balance:.1f} BTC")
    print(f"{'ACTIVE WALLETS':<15} {'':<8} {len(network_data['nodes'])} wallets")
    print(f"{'MINERS':<15} {'':<8} {miners_count} active")
    # Network summary
    print("\nNetwork Overview:")
    print(f"   Total Supply: {total_balance:.1f} BTC")
    print(f"   Active Wallets: {len(network_data['nodes'])}")
    print(f"   Active Miners: {network_info['total_miners']}")
    print(f"   Blockchain Height: {network_info['blockchain_length']} blocks")
    print(f"   Mining Difficulty: {network_info['difficulty']}")
    print(f"   Pending Transactions: {network_info['pending_transactions']}")
    print()
    
    # Transaction summary
    print("Coin Distribution:")
    if network_info['blockchain_length'] > 1:
        mining_blocks = network_info['blockchain_length'] - 1
        print(f"   - Genesis Distribution: {network_info['total_nodes'] * 50} BTC (50 BTC per wallet)")
        print(f"   - Mining Rewards: {mining_blocks * 50} BTC ({mining_blocks} block(s) x 50 BTC)")
    else:
        print(f"   - Genesis Distribution: {network_info['total_nodes'] * 50} BTC (50 BTC per wallet)")
    print(f"   - Total Circulating Supply: {total_balance} BTC")
    print()
    
    # Verify balance integrity
    # Calculate expected total based on actual blockchain length
    genesis_coins = network_info['total_nodes'] * 50  # 50 BTC per wallet in genesis
    mining_rewards = (network_info['blockchain_length'] - 1) * 50  # 50 BTC per mined block (excluding genesis)
    expected_total = genesis_coins + mining_rewards
    
    print("Balance Verification:")
    if abs(total_balance - expected_total) < 0.01:
        print("   PASSED - All coins properly accounted for")
        print(f"   Genesis: {genesis_coins} BTC | Mining: {mining_rewards} BTC | Total: {expected_total} BTC")
    else:
        print(f"   FAILED - Balance mismatch detected!")
        print(f"   Expected: {expected_total} BTC | Actual: {total_balance} BTC")
        print(f"   Genesis: {genesis_coins} BTC | Mining: {mining_rewards} BTC")
    
    print("\n" + "=" * 65)

if __name__ == "__main__":
    view_node_balances()
