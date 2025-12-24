# Pirate Ship Battle Game Project

A third-person Pirate Ship Battle Game featuring ship sailing mechanics, dynamic weather, enemy AI, and combat systems.

Computer Graphics (CSE423) Project

---

## Core Gameplay Features

### 1. Ship Movement & Sailing Controls

* **W / S** – Raise or lower sails (3 sail states):

  * **No Sail**: Ship remains stationary
  * **Half Sail**: Medium movement speed
  * **Full Sail**: Maximum movement speed
* **A / D** – Turn ship left or right (rotation on Z-axis)
* The ship always moves forward in the direction it is facing
* **Momentum System**: Ship does not stop instantly when sails are lowered, creating realistic movement

---

### 2. Enemy Ship AI

* Enemy ships spawn at random positions around the player after a storm
* Enemy behavior:

  * Always aggressive
  * Positions itself broadside to the player
  * Fires cannons when within range
  * Maintains distance while attacking

---

### 3. Storm System

* Storm events occur:

  * 30 seconds after game start
  * After an enemy ship is destroyed
* Storm effects include:

  * Rain from a random direction (angular rain animation)
  * Darkened sky visuals
  * **Full Sail**: Ship takes **5 damage per second**
  * **Half Sail**: Ship gains wind speed boost but takes **2 damage per second**

---

### 4. Cannon System

* **Left Click** – Fire cannons
* Reload cooldown of **1–2 seconds per side**
* Cannonballs:

  * Disappear after traveling a fixed distance
  * Disappear upon collision

---

### 5. Infinite Ocean & Spawning System

* Infinite ocean using procedural, tile-based grid rendering
* Ocean tiles repeat seamlessly
* Third-person camera follows the player ship

---

### 6. Health System with Regeneration

* **Player Ship**: 100 HP
* **Enemy Ships**: 30 HP each
* Visual health indicator displayed as 2D text (top-right corner)
* Ship sinks when HP reaches 0

---

### 7. Cannon Aiming Range Indicator

* While aiming (holding **Q** or **E**):

  * A red line/arrow is drawn from the ship
  * Indicates maximum cannon range
* Cannon range is always fixed

---

### 8. Ramming Attack System

* The front of the ship has collision detection
* Ramming an enemy ship deals damage

---

### 9. Large Wave System

* Triggered after the storm ends
* A large wave appears:

  * In front of the ship at a fixed distance
  * Moves forward in the ship’s direction
* Wave behavior:

  * Appears as a tall wall of water
  * **Head-on hit (±30°)**: Safe
  * **Side hit**: Ship takes **15 damage**

---

## Game Rules

* After **30 seconds** of gameplay, a storm begins
* Storm lasts **10 seconds**
* After the storm ends, an enemy ship spawns
* Destroying the enemy triggers the next storm
* This cycle repeats continuously

---

## Default Game Assets

### Ship Model

* **Hull**: Cuboid
* **Mast**: Cylinder
* **Sail**: Quad/Triangle (size changes with sail state)
* **Cannons**: Small cylinders mounted on both sides

---

### Ocean

* Flat grid with animated wave texture
* Color states:

  * Blue-green (normal)
  * Dark gray (during storm)

---

### Camera

* Third-person camera behind the ship
* **Up / Down Arrows** – Zoom in / out
* **Left / Right Arrows** – Rotate camera around the ship

---

## Controls Summary

| Key        | Action                 |
| ---------- | ---------------------- |
| W / S      | Raise / Lower sails    |
| A / D      | Turn ship left / right |
| Q          | Aim left cannons       |
| E          | Aim right cannons      |
| Left Click | Fire cannons           |
| R          | Reset game             |
| Arrow Keys | Camera control         |

---
