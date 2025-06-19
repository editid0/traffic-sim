import simpy
from typing import List, Optional
import random, numpy.random as npr
import matplotlib.pyplot as plt

DO_PRINT = False


class RoadObject:
    """Base class for objects on the road (speed bumps, cameras, etc)."""

    def affect(self, car, env):
        pass


class SpeedCamera(RoadObject):
    def __init__(self, speed_limit):
        self.speed_limit = speed_limit

    def affect(self, car, env):
        if random.choice([True, False]):
            car.speed = max(
                car.speed - 5, 1
            )  # 50% chance to slow down before speed check
        if car.speed > self.speed_limit:
            if DO_PRINT:
                print(f"Car {car.id} fined for speeding at {env.now}s!")


class SpeedBump(RoadObject):
    def __init__(self, slow_down):
        self.slow_down = slow_down

    def affect(self, car, env):
        car.speed = max(car.speed - self.slow_down, 1)
        if DO_PRINT:
            print(
                f"Car {car.id} slowed to {car.speed} at {env.now}s due to speed bump."
            )


class CongestionCharging(RoadObject):
    def __init__(self, fumes: float):
        self.fumes = fumes

    def affect(self, car, env):
        if self.fumes > 0.5:
            if bool(
                npr.choice([True, False], 1, p=[0.4, 0.6])[0]
            ):  # 60% chance of aborting and not going through congestion zone
                if DO_PRINT:
                    print(f"Car is being charged for entering")
            else:
                car.speed = 0


class TrafficCollisionDetection(RoadObject):
    def __init__(self): ...

    def affect(self, car, env):
        # Simulate a collision detection system
        if bool(npr.choice([True, False], 1, p=[0.05, 0.95])[0]):
            if DO_PRINT:
                print(f"Collision detected for Car {car.id} at {env.now}s!")
            car.speed = 0  # Stop the car in case of collision


class Car:
    def __init__(self, id, speed=10):
        self.id = id
        self.speed = speed
        self.position = 0

    def move(self):
        self.position += self.speed


class Road:
    def __init__(self, length, objects: Optional[List[RoadObject]] = None):
        self.length = length
        self.objects = objects if objects else []

    def check_objects(self, car, env):
        for obj in self.objects:
            obj.affect(car, env)


def car_process(env, car: Car, road: Road, finished_cars, time_limit):
    while car.position < road.length and env.now < time_limit:
        car.move()
        if DO_PRINT:
            print(
                f"Car {car.id} at position {car.position} (speed {car.speed}) at {env.now}s"
            )
        road.check_objects(car, env)
        yield env.timeout(1)
    if car.position >= road.length and env.now <= time_limit:
        if DO_PRINT:
            print(f"Car {car.id} finished at {env.now}s!")
        finished_cars.append(car.id)
    elif car.position < road.length:
        if DO_PRINT:
            print(f"Car {car.id} did not finish in time (stopped at {car.position})!")


def run_simulation(num_cars=50, time_limit=30):
    env = simpy.Environment()
    road = Road(
        length=100,
        objects=[
            SpeedCamera(15),
            SpeedBump(5),
            CongestionCharging(
                float(
                    npr.choice(
                        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                        1,
                        p=[0.05, 0.1, 0.1, 0.15, 0.2, 0.15, 0.1, 0.1, 0.05],
                    )[0]
                )
            ),
            TrafficCollisionDetection(),
        ],
    )
    speeds = [
        random.choices([10, 15, 20, 25, 30], weights=[1, 3, 5, 3, 1])[0]
        for _ in range(num_cars)
    ]
    cars = [Car(id=i + 1, speed=speeds[i]) for i in range(num_cars)]
    finished_cars = []
    for car in cars:
        env.process(car_process(env, car, road, finished_cars, time_limit))
    env.run(until=time_limit)
    return len(finished_cars)


def main():
    num_runs = 1000
    num_cars = 100
    time_limit = 60
    results = []
    for _ in range(num_runs):
        finished = run_simulation(num_cars=num_cars, time_limit=time_limit)
        if finished <= 10:
            continue
        results.append(finished)

    # Plot histogram of results
    plt.hist(results, bins=20, color="skyblue", edgecolor="black")
    plt.title(f"Number of Cars Finished per Run ({num_runs} runs)")
    plt.xlabel("Cars Finished")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.savefig("cars_finished_histogram.png")

    avg_finished = sum(results) / len(results)
    print(
        f"\nAverage number of cars that finished in {time_limit} seconds over {num_runs} runs: {avg_finished:.2f} out of {num_cars} cars."
    )


if __name__ == "__main__":
    main()
