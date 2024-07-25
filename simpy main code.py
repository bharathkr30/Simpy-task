import simpy
import random

class ContainerTerminal:
    def _init_(self, env, num_berths, num_cranes, num_trucks, crane_speed, truck_speed, container_count, arrival_interval):
        self.env = env
        self.num_berths = num_berths
        self.num_cranes = num_cranes
        self.num_trucks = num_trucks
        self.crane_speed = crane_speed
        self.truck_speed = truck_speed
        self.container_count = container_count
        self.arrival_interval = arrival_interval
        
        self.berths = simpy.Resource(env, num_berths)
        self.cranes = simpy.Resource(env, num_cranes)
        self.trucks = simpy.Resource(env, num_trucks)
        
    def log(self, message):
        print(f"{self.env.now:.2f}: {message}")
    
    def vessel_arrival(self):
        while True:
            yield self.env.timeout(random.expovariate(1.0 / self.arrival_interval))
            self.env.process(self.handle_vessel())

    def handle_vessel(self):
        self.log("Vessel arriving.")
        
        with self.berths.request() as berth_request:
            yield berth_request
            self.log("Vessel berthed.")
            yield self.env.process(self.unload_vessel())
            self.log("Vessel leaving.")

    def unload_vessel(self):
        with self.cranes.request() as crane_request:
            yield crane_request
            self.log("Crane starting to unload.")

            for _ in range(self.container_count):
                yield self.env.process(self.move_container())
            self.log("Crane finished unloading.")

    def move_container(self):
        with self.trucks.request() as truck_request:
            yield truck_request
            yield self.env.timeout(self.crane_speed)
            self.log("Crane moved a container to a truck.")
            yield self.env.timeout(self.truck_speed)
            self.log("Truck delivered a container to the yard block.")
            self.log("Truck returning for the next container.")

def main(simulation_time):
    env = simpy.Environment()
    terminal = ContainerTerminal(
        env,
        num_berths=2,
        num_cranes=2,
        num_trucks=3,
        crane_speed=3,  
        truck_speed=6,  
        container_count=150,
        arrival_interval=5 * 60  
    )
    
    env.process(terminal.vessel_arrival())
    env.run(until=simulation_time)

if _name_ == "_main_":
    SIMULATION_TIME = 24 * 60  
    main(SIMULATION_TIME)