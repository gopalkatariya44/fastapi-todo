from fastapi import APIRouter, status

router = APIRouter(
    prefix='/company',
    tags=['Company'],
    responses={status.HTTP_418_IM_A_TEAPOT: {
        'description': 'Internal Use Only.'
    }}
)


@router.get('/')
async def get_company_name():
    return {
        'company_name': "Skylink PVT LTD",
    }


@router.get('/employees')
async def number_of_employees():
    return {'count': 100}
