from dataclasses import dataclass
from typing import TextIO
from collections import deque
from enum import Enum
import curses
import time


TimeStamp = int


Identifier = int


class Direction(Enum):
    RIGHT = 1
    LEFT = -1

    def __int__(self):
        return self.value


@dataclass
class Package:
    identifier: Identifier
    arrival: TimeStamp
    source: int
    destination: int
    weight: int
    value: int


class Station:
    packages: deque[Package]
    identifier: Identifier
    # netValue: float # De cara a experto sum(value)/sum(weight)

    def __init__(self, identifier: Identifier) -> None:
        self.identifier = identifier
        self.packages = deque()


class Wagon:
    pos: int
    packages: dict[Identifier, Package]
    num_stations: int
    capacity: int
    current_load: int

    def __init__(self, num_stations: int, capacity: int) -> None:
        """The wagon is initialized in the first station, has a current capacity of 0 and 
        its max capacity and number of stations are initialized"""
        self.pos = 0
        self.current_load = 0
        self.capacity = capacity
        self.num_stations = num_stations
        self.packages = {}

    def move(self, direction: Direction) -> None:
        """We asume that movements will be between -1 and 1 and we will compute the difference. 
        If it exceeds or defects the num_stations (0, num_stations -1), we will adapt 
        so the ring structure is respected"""
        self.pos = self.pos + direction.value

        if self.pos < 0:
            self.pos = self.num_stations - 1
        if self.pos >= self.num_stations:
            self.pos = 0

    def load_package(self, p: Package) -> None:
        """We load a package into the wagon"""
        self.packages[p.identifier] = p
        self.current_load = sum(
            [package.weight for package in self.packages.values()])

    def deliver(self, identifier: Identifier) -> int:
        """We deliver a package to a corresponding station"""
        if identifier not in list(self.packages.keys()):
            return 0
        myPackage = self.packages.pop(identifier)
        self.current_load = sum(
            [package.weight for package in self.packages.values()])
        return myPackage.value


class FullfilmentCenter:

    _wagon: Wagon

    def __init__(self, num_stations: int, wagon_capacity: int) -> None:
        """Creates a Wagon object with the specified number of stations and wagon capacity, 
        and a dictionary of Station objects for each station on the Wagon's route. 
        The train's cash is also set to zero."""
        self._wagon = Wagon(num_stations, wagon_capacity)
        self._stations = {ident: Station(ident)
                          for ident in range(num_stations)}
        self._cash = 0

    def cash(self) -> int:
        """Returns the cash."""
        return self._cash

    def wagon(self) -> Wagon:
        """Returns de Wagon object with the specified number of stations and wagon capacity."""
        return self._wagon

    def num_stations(self) -> int:
        """Returns the number of stations."""
        return len(self._stations)

    def station(self, idx: int) -> Station:
        """Returns the current station"""
        return self._stations[idx]

    def receive_package(self, p: Package) -> None:
        """The package arrives to the center of distribution and the source station receives the package."""
        destStation = self.station(p.source)
        if not destStation:
            return None
        destStation.packages.appendleft(p)

    def deliver_package(self, identifier: Identifier) -> None:
        """Checks if the identifier is correct, and if the wagon is in the correct destination of the package to deliver."""
        self._cash += self._wagon.deliver(identifier)

    def current_station_package(self) -> Package | None:
        """Checks if the station is empty. If so, returns None, and it not returns the very first package from down below. """
        # if self.current_station.is_empty():
        if (len(self._stations[self._wagon.pos].packages) == 0):
            return None
        elif (self._wagon.current_load + self._stations[self._wagon.pos].packages[-1].weight) > self._wagon.capacity:
            return None
        else:
            return self._stations[self._wagon.pos].packages[-1]

    def load_current_station_package(self) -> None:
        """Calls the function load_package of Wagon."""
        package = self.current_station_package()
        if (package != None):
            self._wagon.load_package(package)
            self._stations[self._wagon.pos].packages.pop()

    def write(self, stdscr: curses.window, caption: str = '') -> None:
        def package_color(p: Package) -> int:
            return curses.color_pair(1 + p.destination * 6 * 764351 % 250)

        factory_height = 8  # maximum number of rows to write
        wagon_height = 6  # maximum number of rows to write
        delay = 0.03  # delay after writing the state
        # start: clear screen
        stdscr.clear()
        # write caption
        stdscr.addstr(0, 0, caption)
        stdscr.addstr(1, 0, ' ' * caption.find('t:') +
                      '$: ' + str(self.cash()))
        # write stations base
        for i in range(self.num_stations()):
            stdscr.addstr(factory_height + 3, 3*i, '-')
            stdscr.addstr(factory_height + 3, 3*i + 1,
                          f's{i}', package_color(Package(-1, -1, -1, i, -1, -1)))
        stdscr.addstr(factory_height + 3, 3*self.num_stations(), '-')
        # write packages in stations
        for i in range(self.num_stations()):
            x, dy = 3*i + 1, 0
            for p in self.station(i).packages:
                dy += 1
                if dy > factory_height:
                    stdscr.addstr(factory_height + 3 -
                                  factory_height - 1, x, f'..')
                else:
                    stdscr.addstr(factory_height + 3 - dy, x,
                                  f'{p.identifier%100:02d}', package_color(p))
        # write wagon
        for i in range(wagon_height):
            stdscr.addstr(factory_height + 4 + wagon_height -
                          1-i, 3*self.wagon().pos, '|')
            stdscr.addstr(factory_height + 4 + wagon_height -
                          1-i, 3*self.wagon().pos + 3, '|')
        # write wagon packages
        ps = list(self.wagon().packages.values())
        for i in range(min(len(ps), wagon_height-1)):
            p = ps[i]
            stdscr.addstr(factory_height + 4 + wagon_height-1-i, 3 *
                          self.wagon().pos + 1, f'{p.identifier%100:02d}', package_color(p))
        if len(ps) >= wagon_height:
            stdscr.addstr(factory_height + 4, 3*self.wagon().pos + 1, '..')
        stdscr.addstr(factory_height + 4 + wagon_height,
                      3*self.wagon().pos, f'o--o')
        # done
        stdscr.refresh()
        time.sleep(delay)


class Logger:
    """Class to log fcenter actions to a file."""

    _file: TextIO

    def __init__(self, path: str, name: str, num_stations: int, wagon_capacity: int) -> None:
        self._file = open(path, 'w')
        print(0, 'START', name, num_stations, wagon_capacity, file=self._file)

    def load(self, t: TimeStamp, identifier: Identifier) -> None:
        print(t, 'LOAD', identifier, file=self._file)

    def deliver(self, t: TimeStamp, identifier: Identifier) -> None:
        print(t, 'DELIVER', identifier, file=self._file)

    def move(self, t: TimeStamp, direction: Direction) -> None:
        print(t, 'MOVE', int(direction), file=self._file)

    def add(self, t: TimeStamp, identifier: Identifier) -> None:
        print(t, 'ADD', identifier, file=self._file)


def read_packages(path: str) -> list[Package]:
    """Returns a list of packages read from a file at path."""

    with open(path, 'r') as file:
        packages: list[Package] = []
        for line in file:
            identifier, arrival, location, destination, weight, value = map(
                int, line.split())
            package = Package(identifier, arrival, location,
                              destination, weight, value)
            packages.append(package)
        return packages


def check_and_show(packages_path: str, log_path: str, stdscr: curses.window | None = None) -> None:
    """
    Check that the actions stored in the log at log_path with the packages at packages_path are legal.
    Raise an exception if not.
    // In the case that stdscr is not None, the store is written after each action.
    """

    # get the data
    packages = read_packages(packages_path)
    packages_map = {p.identifier: p for p in packages}
    log = open(log_path, 'r')
    lines = log.readlines()

    # process first line
    tokens = lines[0].split()
    assert len(tokens) == 5
    assert tokens[0] == "0"
    assert tokens[1] == "START"
    name = tokens[2]
    num_stations = int(tokens[3])
    wagon_capacity = int(tokens[4])
    fcenter = FullfilmentCenter(num_stations, wagon_capacity)
    last_wagon_action = -1
    last_package_arrival = -1

    for line in lines[1:]:
        tokens = line.split()
        t: TimeStamp = int(tokens[0])
        what = tokens[1]
        assert t >= max(last_wagon_action, last_package_arrival)

        p: Package | None = None

        if what == "ADD":
            assert t > last_wagon_action
            identifier = int(tokens[2])
            assert identifier in packages_map.keys()
            p = packages_map[identifier]
            assert p.arrival == t
            fcenter.receive_package(p)
            last_package_arrival = t
        elif what == "DELIVER":
            identifier = int(tokens[2])
            matches = list(filter(lambda p: p.identifier ==
                           identifier, fcenter.wagon().packages.values()))
            assert len(matches) == 1
            p = matches[0]
            fcenter.deliver_package(identifier)
            last_wagon_action = t
        elif what == "MOVE":
            direction = Direction(int(tokens[2]))
            fcenter.wagon().move(direction)
            last_wagon_action = t
        elif what == "LOAD":
            identifier = int(tokens[2])
            p = fcenter.current_station_package()
            assert p is not None
            assert p.identifier == identifier
            fcenter.load_current_station_package()
            assert 0 <= sum(pkg.weight for pkg in fcenter.wagon(
            ).packages.values()) <= wagon_capacity
            last_wagon_action = t
        else:
            assert False

        if stdscr:
            fcenter.write(stdscr, f'{name} t: {line.strip()}')
