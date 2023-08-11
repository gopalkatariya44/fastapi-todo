from fastapi import Header, HTTPException, status


async def get_token_header(intanal_token: str = Header(...)):
    if intanal_token != 'allowed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Internal-Token header invalid'
        )
