from dataclasses import dataclass
import uuid

@dataclass
class TokenDetails:
    """
    Details for a token
    
    :param jti: The JWT ID
    :param exp: The expiration time
    """
    jti: uuid.UUID
    exp: int