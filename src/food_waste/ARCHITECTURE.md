# Architecture
This document describes the architecture of the project.

## Code Map
This section describes various directories and files and what they mean/do.

* `api`
  * Files in this directory are used to communicate with the backend API.
* `events`
  * This directory contains classes subclassed by other event emitter-like objects in the project.
* `gpio`
  * This directory wraps GPIO libraries for use in other parts of the project to interact with the hardware.
* `io`
  * This directory contains classes that interact with the hardware.
  * `component`
    * These classes are lower-level than the classes in the parent directory.
* `log`
  * This directory contains functions that are used to log information to the console.
