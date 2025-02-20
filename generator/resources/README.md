Resource Generation
===================

The old resource code was crazy and slow. Let's redesign everything!

Design Goals
------------
1. Decouple processing different types of resources from each other into their own files
2. Be completely SDK vs Firmware independent. Any differences in behaviour between the two resource
   generation variants should be captured in parameters as opposed to explicitly checking which
   one we are.
3. No more shelling out
4. Capture as much intermediate state in the filesystem itself as possible as opposed to
   generating large data structures that need to be done on each build.
5. Remove the need to put dynamically generated resource content like the bluetooth patch and
   stored apps into our static resource definition json files for more modularity.
