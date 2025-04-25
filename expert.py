# """
# Template file for simple.py module.
# """

import sys
from fcenter import *


class Strategy:
    _name: str
    """This class generates a strategy for the fcenter"""

    def __init__(self, num_stations: int, wagon_capacity: int, log_path: str) -> None:
        self.name = "ExpertStrategy"
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
                bdir = self.bestDir()
                self.fcenter.wagon().move(bdir)
                self.logger.move(i, bdir)

        print(self.fcenter.cash())


    def getLeftRight(self, wagon_pos: int, goal_pos: int) -> tuple[int, int]:
        left_value = (wagon_pos - goal_pos) % self.fcenter.num_stations()
        right_value = self.fcenter.num_stations() - left_value
        return left_value, right_value
    
    def bestDir1(self):
        ##1
        # Si vagó buit
            # For paquet per recollir
                # Dreta o esquerra
            # Tries direcció final
        # Else
            # For paquet a entregar
                # Dreta o esquerra
            # Tries direcció final
        
        pos = self.fcenter.wagon().pos

        left_value = 0
        right_value = 0
        if len(self.fcenter.wagon().packages) == 0:
            for station_id in range(self.fcenter.num_stations()):
                left_steps, right_steps = self.getLeftRight(pos, station_id)
                for p in self.fcenter.station(station_id).packages:
                    if left_steps < right_steps:
                        left_value += p.value
                    elif right_steps < left_steps:
                        right_value += p.value
                    else:
                        pass

            if left_value >= right_value:
                return Direction.LEFT
            else:
                return Direction.RIGHT
            
        else:
            for p in self.fcenter.wagon().packages.values():
                left_steps, right_steps = self.getLeftRight(pos, p.destination)
                if left_steps < right_steps:
                    left_value += p.value
                elif right_steps < left_steps:
                    right_value += p.value
                else:
                    pass

            if left_value >= right_value:
                return Direction.LEFT
            else:
                return Direction.RIGHT


    
    def bestDir(self):
        pos = self.fcenter.wagon().pos

        left_value = 0
        right_value = 0
        if len(self.fcenter.wagon().packages) == 0:
            for i in range(1, (self.fcenter.num_stations() + 1) // 2):
                # i left
                for p in self.fcenter.station((pos - i) % self.fcenter.num_stations()).packages:
                    left_value += p.value

                # i right
                for p in self.fcenter.station((pos + i) % self.fcenter.num_stations()).packages:
                    right_value += p.value

            if left_value >= right_value:
            
                return Direction.LEFT
            else:
                return Direction.RIGHT
            
        else:
            for p in self.fcenter.wagon().packages.values():
                left_steps, right_steps = self.getLeftRight(pos, p.destination)
                if left_steps < right_steps:
                    left_value += p.value
                elif right_steps < left_steps:
                    right_value += p.value
                else:
                    pass

            if left_value >= right_value:
                return Direction.LEFT
            else:
                return Direction.RIGHT
            
    def bestDir2(self):
        pos = self.fcenter.wagon().pos

        left_value = 0
        right_value = 0
        if len(self.fcenter.wagon().packages) == 0:
            for i in range(1, (self.fcenter.num_stations() + 1) // 2):
                # i left
                for p in self.fcenter.station((pos - i) % self.fcenter.num_stations()).packages:
                    left_value += p.value

                # i right
                for p in self.fcenter.station((pos + i) % self.fcenter.num_stations()).packages:
                    right_value += p.value

            if left_value >= right_value:
                return Direction.LEFT
            else:
                return Direction.RIGHT
            
        else:
            for p in self.fcenter.wagon().packages.values():
                left_steps, right_steps = self.getLeftRight(pos, p.destination)
                if left_steps < right_steps:
                    left_value += p.value
                elif right_steps < left_steps:
                    right_value += p.value
                else:
                    pass
            for station_id in range(self.fcenter.num_stations()):
                left_steps, right_steps = self.getLeftRight(pos, station_id)
                for p in self.fcenter.station(station_id).packages:
                    if left_steps < right_steps:
                        left_value += p.value
                    elif right_steps < left_steps:
                        right_value += p.value
                    else:
                        pass

            if left_value >= right_value:
                return Direction.LEFT
            else:
                return Direction.RIGHT

        ##2
        # Si vagó buit
            # For paquet per recollir
                # Dreta o esquerra
            # Tries direcció final
        # Else
            # Tries direcció final segons paquet de més valor dins vagó

        ##3
        # Si vagó buit
            # Mires una posició a cada banda (si a una posició no hi ha res, mires a dues, ... +-2 % num_estacions)
                # For paquet per recollir
                    # Dreta o esquerra
            # Tries direcció final segons paquets
        # Else
            # For paquet a entregar
                # Dreta o esquerra
            # Tries direcció final

        ##4
        # Si no està buit
            # For paquet a entregar
                # ...
            # For paquet a recollir
                # ...  


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
