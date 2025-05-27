import random
from typing import List

class Node:
    """
    Represents a single node in the network with a binary state (0 or 1).
    Maintains counters for Snowflake and Snowball phases.
    """
    def __init__(self, node_id: int, initial_state: int):
        self.id = node_id
        self.state = initial_state
        self._snowflake_count = 0      
        self._snowball_counter = {0: 0, 1: 0} 

    def sample(self, peers: List['Node'], k: int) -> int:
        """
        Sample k random peers and return majority state.
        """
        sample_nodes = random.sample(peers, k)
        states = [n.state for n in sample_nodes]
        # Return majority, break ties randomly
        if states.count(0) > states.count(1):
            return 0
        elif states.count(1) > states.count(0):
            return 1
        else:
            return random.choice([0, 1])

    def update_snowflake(self, sampled_state: int, alpha: int) -> int:
        """
        Update Snowflake counter:
        """
        if sampled_state == self.state:
            self._snowflake_count += 1
        else:
            self._snowflake_count = 1
        if self._snowflake_count >= alpha:
            self.state = sampled_state
        return self.state

    def update_snowball(self, sampled_state: int) -> int:
        """
        Update Snowball.
        """
        self._snowball_counter[sampled_state] += 1
        preferred = max(self._snowball_counter, key=self._snowball_counter.get)
        self.state = preferred
        return self.state

class AvalancheSimulation:
    """
    Parameters:
    - num_nodes: total number of nodes
    - k: sample size per query
    - alpha: consecutive agreement threshold for Snowflake
    - beta: final convergence threshold 
    - max_rounds: safety cap on iterations
    """
    def __init__(self, num_nodes: int, k: int, alpha: int, beta: int, max_rounds: int = 10000):
        self.nodes = [Node(i, random.choice([0, 1])) for i in range(num_nodes)]
        self.k = k
        self.alpha = alpha
        self.beta = beta
        self.max_rounds = max_rounds

    def run(self) -> int:
        """
        Run the multi-phase Avalanche consensus until convergence or max_rounds.
        Returns the number of rounds taken.
        """
        rounds = 0
        while rounds < self.max_rounds:
            rounds += 1
            # Each node updates through Slush -> Snowflake -> Snowball
            for node in self.nodes:
                peers = [p for p in self.nodes if p.id != node.id]
                sampled = node.sample(peers, self.k)
                node.update_snowflake(sampled, self.alpha)
                node.update_snowball(sampled)
            # Avalanche: check for network convergence
            states = [n.state for n in self.nodes]
            count_0 = states.count(0)
            count_1 = states.count(1)
            if count_0 >= self.beta or count_1 >= self.beta:
                break
        return rounds

if __name__ == '__main__':
    try:
        num = int(input("Enter number of nodes: "))
        k = int(input("Enter sample size k: "))
        alpha = int(input("Enter Snowflake threshold alpha: "))
        beta = int(input("Enter convergence threshold beta: "))
        max_r = input("Enter max rounds : ")
        max_rounds = int(max_r) 
    except ValueError:
        print("Invalid input. Please enter integer values.")
        exit(1)

    sim = AvalancheSimulation(num_nodes=num, k=k, alpha=alpha, beta=beta, max_rounds=max_rounds)
    rounds_needed = sim.run()
    final_states = [node.state for node in sim.nodes]
    print(f"\nConverged in {rounds_needed} rounds")
    print(f"State 0 count: {final_states.count(0)}")
    print(f"State 1 count: {final_states.count(1)}")
