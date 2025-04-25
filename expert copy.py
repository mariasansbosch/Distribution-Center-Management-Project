# """
# Template file for expert.py module.
# """

import sys

from fcenter import *


class Strategy:
    _name: str
    """This class generates a strategy for a fcenter"""

    def __init__(self, num_stations: int, wagon_capacity: int, log_path: str) -> None:
        self.name = "SimpleStrategy"
        self.fcenter = FullfilmentCenter(num_stations, wagon_capacity)
        self.logger = Logger(log_path, self.name, num_stations, wagon_capacity)

    def cash(self) -> int:
        return self.fcenter.cash()

    def exec(self, packages: list[Package]) -> None:
        """We execute out strategy"""
        lastInstant = packages[-1].arrival
        for i in range(lastInstant + 1):
            # 1 Part: we check for new package arrival to the stations
            # receive_package(pack) for pack in packages if pack.arrival == i
            arrPack = [pack for pack in packages if pack.arrival == i]
            for ap in arrPack:
                self.fcenter.receive_package(ap)
                self.logger.add(i, ap.identifier)
            # 2 Part: We first try to deliver our packages
            wPack = [pack for pack in self.fcenter.wagon().packages.values(
            ) if self.fcenter.wagon().pos == pack.destination]
            # We check if there is a package to take from the current station
            p = self.fcenter.current_station_package()
            if len(wPack) > 0:  # There is a package to deliver to the current station inside the wagon
                self.fcenter.deliver_package(wPack[0].identifier)
                self.logger.deliver(i, wPack[0].identifier)
            # 3 Part: We try to load any package from the current station to the wagon
            elif p != None:
                self.fcenter.load_current_station_package()
                self.logger.load(i, p.identifier)
            # 4 Part: We move
            else:
                bdir = self.bestDir()
                self.fcenter.wagon().move(bdir)
                self.logger.move(i, bdir)
        print(self.cash())

    def bestDir(self):
        wPack = [pack for pack in self.fcenter.wagon().packages.values()]
        if len(wPack) > 0:
            pos = self.fcenter.wagon().pos
            offset = pos - (self.fcenter.num_stations() - 1) // 2
            wPackScale = wPack.copy()
            # We redefine the station indexes
            for wpack in wPackScale:
                wpack.destination -= offset
                while wpack.destination < 0:
                    wpack.destination += self.fcenter.num_stations()
                while wpack.destination >= self.fcenter.num_stations():
                    wpack.destination -= self.fcenter.num_stations()

            stationsLeft = [
                p.value for p in wPackScale if p.destination < self.fcenter.num_stations() // 2]
            stationsRight = [
                p.value for p in wPackScale if p.destination > self.fcenter.num_stations() // 2]

            balance = sum(stationsRight) - sum(stationsLeft)

            return Direction.RIGHT if balance >= 0 else Direction.LEFT
        else:  # Decidimos en funcion a los paquetes de las estaciones
            return Direction.RIGHT


def execute_strategy(packages_path: str, log_path: str, num_stations: int, wagon_capacity: int) -> None:
    """Execute the strategy on an fcenter with num_stations stations reading packages from packages_path and logging to log_path."""

    packages = read_packages(packages_path)
    strategy = Strategy(num_stations, wagon_capacity, log_path)
    strategy.exec(packages)


def main() -> None:
    """main script"""
    packages_path = "simple.txt"  # sys.argv[1]
    log_path = "log.txt"  # sys.argv[2]
    num_stations = 8  # int(sys.argv[3])
    wagon_capacity = 8000  # int(sys.argv[4])

    execute_strategy(packages_path, log_path, num_stations, wagon_capacity)
    check_and_show(packages_path, log_path)


if __name__ == '__main__':
    main()
