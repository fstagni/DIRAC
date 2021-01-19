"""
This module contains constants and lists for the possible job states.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__RCSID__ = "$Id$"

from DIRAC.Core.Utilities.StateMachine import State, StateMachine


#:
SUBMITTING = 'Submitting'
#:
RECEIVED = 'Received'
#:
CHECKING = 'Checking'
#:
STAGING = 'Staging'
#:
WAITING = 'Waiting'
#:
MATCHED = 'Matched'
#:
RESCHEDULED = 'Rescheduled'
#:
RUNNING = 'Running'
#:
STALLED = 'Stalled'
#:
COMPLETING = 'Completing'
#:
DONE = 'Done'
#:
COMPLETED = 'Completed'
#:
FAILED = 'Failed'
#:
DELETED = 'Deleted'
#:
KILLED = 'Killed'

#: Possible job states
JOB_STATES = [SUBMITTING,
              RECEIVED,
              CHECKING,
              STAGING,
              WAITING,
              MATCHED,
              RESCHEDULED,
              RUNNING,
              STALLED,
              COMPLETING,
              DONE,
              COMPLETED,
              FAILED,
              DELETED,
              KILLED]

#: Job States when the payload work has finished
JOB_FINAL_STATES = [DONE,
                    COMPLETED,
                    FAILED]


class JobsStateMachine(StateMachine):
  """ Jobs state machine
  """

  def __init__(self, state):
    """ c'tor
        Defines the state machine transactions
    """
    super(JobsStateMachine, self).__init__(state)

    # States transitions
    self.states = {KILLED: State(14),  # final state
                   DELETED: State(13),  # final state
                   FAILED: State(12, [RESCHEDULED, KILLED, DELETED], defState=DELETED),
                   DONE: State(11, [KILLED, DELETED], defState=DELETED),
                   COMPLETED: State(10, [DONE, FAILED, KILLED, DELETED], defState=DONE),
                   COMPLETING: State(9, [DONE, FAILED, COMPLETED], defState=COMPLETED),
                   STALLED: State(8, [RUNNING], defState=RUNNING),  # CHECK!
                   RUNNING: State(7, [RESCHEDULED, STALLED, DONE, FAILED, COMPLETING], defState=DONE),
                   RESCHEDULED: State(6, [WAITING, RECEIVED], defState=WAITING),
                   MATCHED: State(5, [RUNNING], defState=RUNNING),
                   WAITING: State(4, [MATCHED, RESCHEDULED], defState=MATCHED),
                   STAGING: State(3, [WAITING], defState=WAITING),
                   CHECKING: State(2, [STAGING, WAITING, RESCHEDULED], defState=WAITING),
                   RECEIVED: State(1, [CHECKING], defState=CHECKING),
                   # initial state
                   SUBMITTING: State(0, [RECEIVED, CHECKING], defState=RECEIVED)}
