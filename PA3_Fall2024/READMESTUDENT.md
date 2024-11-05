Andrew Nguyen
CS480
PA3

1) I made a predator and prey class in ModelLinkage that are children of the Linkage class. I used my old model for predator and a small one for prey. I changed vivarium.py to have two new methods that clear the vivarium and add either 1 predator and 1 prey for the test scene or 1 predator and 2 prey for the default scene. I then changed Sketch.py keyboard interrupts to call those functions respectively when t or r are pressed.

2) I changed animationUpdate to make it so the creature as a whole will not rotate, but did not change the function further than that. I made it so the list of components in each creature only listed the moveable parts so that animationUpdate wouldn't move everything. I also set the rotation limits to look like normal movement.

3) I used a bounding sphere for the collision detection. I used Ritter's algorithm to find the bounding sphere for the creatures, although i only took into account the positions of each creature's components and not their size and orientation, so the bounding sphere's are a little smaller than they should be. Each creature has a center and a radius for their sphere and I test that agains the world position of the walls to see if they collide against the tank. When they collide, they do a reflection against the wall by reversing the axis they hit on. Each creature then loops through each other creature in the tank to see if they collide, if they do, predator eats prey and preys bounce off each other. Predators find the closest prey by keeping track of the minimum distance and goes towards the position of that creature. The prey checks if its heading towards the predator and if it is, it changes direction to move away.

4) I changed environmentobject.py to make the positive z direction the direction it faces. It matches that axis with the direction vector using cross products. 