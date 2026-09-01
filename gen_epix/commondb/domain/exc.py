"""Re-export FastApp API and domain exceptions used by commondb contracts.

Consumers import these shared exception types from this module when they need
to report command, validation, or API failures without depending directly on
the underlying FastApp exception modules.
"""

# pylint: disable=wildcard-import, unused-wildcard-import
# because this is a package, and imported as such in other modules

from gen_epix.fastapp.api.exc import *
from gen_epix.fastapp.exc import *
