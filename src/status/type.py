STATUS_TYPE = {
  STANDBY: "standby",                 # Device is ready to be used
  ACTIVE: "active",                   # Device is actively waiting for an object to be detected
  OBJECT_DETECTED: "object_detected", # Device has detected an object, user may remove object
  TARING: "taring",                   # Device is taring the scale
  DIRTY: "dirty",                     # TODO: Confirm whether this status is needed
  SHUTDOWN: "shutdown",               # Device is shutting down
  POWER_OFF: "power_off",             # Device is powered off
}
