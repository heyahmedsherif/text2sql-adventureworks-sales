# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import os
from enum import Enum


class IdentityType(Enum):
    """The type of the indexer"""

    USER_ASSIGNED = "user_assigned"
    SYSTEM_ASSIGNED = "system_assigned"
    KEY = "key"


def get_identity_type() -> IdentityType:
    """This function returns the identity type.

    For open source version, always returns KEY (no Azure managed identity)

    Returns:
        IdentityType: The identity type
    """
    # For open source version, we don't use Azure managed identities
    identity = os.environ.get("IdentityType", "key")

    if identity == "user_assigned":
        return IdentityType.USER_ASSIGNED
    elif identity == "system_assigned":
        return IdentityType.SYSTEM_ASSIGNED
    else:
        # Default to KEY for open source version
        return IdentityType.KEY
