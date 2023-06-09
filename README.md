# SO2

<p align="center">
  <a href="[https://github.com/Julia1204/SO2/blob/main]">
    <img src="assets/ghost_images/blue.png" alt="Logo" width="200" height="200">
  </a>
</p>
 
<h3 align="center">Pac-xon</h3>
<p>
  Re-creation of a game with the same name, where player as a pac-man tries to gather 80% of available space to win with ghosts.
</p>

<h3 align="center">Rules</h3>
<p>
Gameplay: Take over 80% of the field by moving with arrow keys and avoid the ghosts. If you run into a ghost or it crosses your line while you are not in a safe zone, you lose a life. Be careful, you have only three of those, if u lose all of them, game restarts.  

Enemies: Pink ghosts are just bouncing around and can be eaten by other ghosts, what makes them disappear from the map. 
Orange ghosts travel close to safe zone boarders.
Red ghosts destroy save zone as they bounce off the walls.  
</p>

<p align="center">
  <a href="[https://github.com/Julia1204/SO2/blob/main]">
    <img src="assets/gameplay.png" alt="Logo" width="900" height="700">
  </a>
</p>

<!-- TECHNOLOGIES -->
## Technologies
To create our game we used `Python 3.9`. 

| Library             | Usage                     |
|---------------------|---------------------------|
| `pygame`            | Pygame is a set of Python modules designed for writing video games. Pygame adds functionality on top of the excellent SDL library. This allows us to create fully featured games and   multimedia programs in the python language. |
| `threading`           | Threading is a Python module that allows us to have different parts of our program run concurrently.|
| `numpy`               | Numpy simplifies working with array what allows us to easily manipulate the board of our game.|
| `scipy`               | Scipy in our project is used for labeling arrays. |

<!-- IMPLEMENTATION -->
## Implementation
Important part of our project was implementing threads and critical section. Our threads handle: player movement, ghosts movement (pink, orange, red) and board updates. Critical section is created on a thread connected to the board. If pink ghost takes the same spot as a red or an orange ghost it gets 'eaten' (removed from the board).

Board of our project is implemented as an array and is stored in `board.py` file. Array consists of numeric values that represent: 0 - empty tile, 1 - filled tile, 2 - temporarly filled tile, -1,-2,-3 - ghosts. Player movement, ghost movement, UI and all the game logic is stored in a `pac-xon.py`.

<!-- AUTHORS -->
## Authors

Project: [https://github.com/Julia1204/SO2/blob/main](https://github.com/Julia1204/SO2/blob/main)

| Author             | Email                     |
|--------------------|---------------------------|
| Julia Gościniak    | 259164@student.pwr.edu.pl |
| Hubert Kustosz     | 259119@student.pwr.edu.pl |
