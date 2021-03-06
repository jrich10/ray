from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import random

from ray.rllib.offline.input_reader import InputReader
from ray.rllib.utils.annotations import override, DeveloperAPI

logger = logging.getLogger(__name__)


@DeveloperAPI
class ShuffledInput(InputReader):
    """Randomizes data over a sliding window buffer of N batches.

    This increases the randomization of the data, which is useful if the
    batches were not in random order to start with.
    """

    @DeveloperAPI
    def __init__(self, child, n=0):
        """Initialize a MixedInput.

        Arguments:
            child (InputReader): child input reader to shuffle.
            n (int): if positive, shuffle input over this many batches.
        """
        self.n = n
        self.child = child
        self.buffer = []

    @override(InputReader)
    def next(self):
        if self.n <= 1:
            return self.child.next()
        if len(self.buffer) < self.n:
            logger.info("Filling shuffle buffer to {} batches".format(self.n))
            while len(self.buffer) < self.n:
                self.buffer.append(self.child.next())
            logger.info("Shuffle buffer filled")
        i = random.randint(0, len(self.buffer) - 1)
        self.buffer[i] = self.child.next()
        return random.choice(self.buffer)
