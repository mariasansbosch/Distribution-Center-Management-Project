# """
# Template file for simple.py module.
# """

import sys

from fcenter import *


class Strategy:
    _name: str
    """This class generates a strategy for the fcenter"""

    def __init__(self, num_stations: int, wagon_capacity: int, log_path: str) -> None:
        self.name = "SimpleStrategy"
        self.fcenter = FullfilmentCenter(num_stations, wagon_capacity)
        self.logger = Logger(log_path, self.name, num_stations, wagon_capacity)

    def cash(self) -> int:
        """Returns the total cash obtained"""
        return self.fcenter.cash()

    def exec(self, packages: list[Package]) -> None:
        """Executes out strategy"""
        lastInstant = packages[-1].arrival

        for i in range(0, lastInstant + 1):

            # 1 Part: Checks for a new package arrival to the stations
            arrPack = [pack for pack in packages if pack.arrival == i]
            for ap in arrPack:
                self.fcenter.receive_package(ap)
                self.logger.add(i, ap.identifier)

            # 2 Part: Tries to deliver the packages
            wPack = [pack for pack in self.fcenter.wagon().packages.values(
            ) if self.fcenter.wagon().pos == pack.destination]

            # Cheks if there is a package to take from the current station
            p = self.fcenter.current_station_package()
            if len(wPack) > 0:  # There is a package to deliver to the current station inside the wagon
                self.fcenter.deliver_package(wPack[0].identifier)
                self.logger.deliver(i, wPack[0].identifier)

            # 3 Part: Tries to load any package from the current station to the wagon
            elif p != None:
                self.fcenter.load_current_station_package()
                self.logger.load(i, p.identifier)

            # 4 Part: The Wagon moves through the station
            else:
                self.fcenter.wagon().move(Direction.RIGHT)
                self.logger.move(i, Direction.RIGHT)
        print(self.fcenter.cash())


def init_curses() -> None:
    """Initializes the curses library to get fancy colors and whatnots."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS - 1):
        try:
            curses.init_pair(i + 1, curses.COLOR_WHITE, i)
        except:
            pass


def execute_strategy(packages_path: str, log_path: str, num_stations: int, wagon_capacity: int) -> None:
    """Executes the strategy on an fcenter with num_stations stations reading packages from packages_path and logging to log_path."""

    packages = read_packages(packages_path)
    strategy = Strategy(num_stations, wagon_capacity, log_path)
    strategy.exec(packages)


def main(stdscr: curses.window) -> None:  
    
    """main script"""
    init_curses()

    packages_path = sys.argv[1]
    log_path = sys.argv[2]
    num_stations = int(sys.argv[3])
    wagon_capacity = int(sys.argv[4])

    execute_strategy(packages_path, log_path, num_stations, wagon_capacity)
    check_and_show(packages_path, log_path, stdscr)


if __name__ == '__main__':
    curses.wrapper(main)
