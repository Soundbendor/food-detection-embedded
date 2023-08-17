import threading

class EventEmitter:

  def __init__(self):
    self._events = {}

  def emit(self, event, *args):
    """
    Emit an event.

    :param event: The event to emit.
    :param args: The arguments to pass to the callbacks.
    """
    if event in self._events:
      event_list = list(self._events[event]) # Copy the set to prevent RuntimeError
      for callback in event_list:
        threading.Thread(target=callback, args=args).start()

  def on(self, event, callback):
    """
    Register a callback to be called when the event is emitted.

    :param event: The event to listen for.
    :param callback: The callback to call when the event is emitted.
    """
    if event not in self._events:
      self._events[event] = set()
    self._events[event].add(callback)

  def off(self, event, callback):
    """
    Remove a callback from the event.

    :param event: The event to remove the callback from.
    :param callback: The callback to remove.
    """
    if event in self._events:
      try:
        self._events[event].remove(callback)
      except Exception:
        for cb in self._events[event]:
          if hasattr(cb, '_original_callback') and cb._original_callback == callback:
            self._events[event].remove(cb)
            break

  def once(self, event, callback):
    """
    Register a callback to be called once when the event is emitted.

    :param event: The event to listen for.
    :param callback: The callback to call when the event is emitted.
    """
    def once_callback(*args):
      self.off(event, once_callback)
      callback(*args)
    once_callback._original_callback = callback
    self.on(event, once_callback)

  def wait(self, event, timeout=None):
    """
    Wait for an event to be emitted.

    :param event: The event to wait for.
    :param timeout: The maximum time to wait for the event in seconds. If `None`, wait indefinitely.
    """
    waiter = threading.Event()
    cb = lambda: waiter.set()
    self.once(event, cb)
    flag = waiter.wait(timeout=timeout)
    if not flag:
      self.off(event, cb)
