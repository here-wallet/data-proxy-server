import json

from fastapi import APIRouter
from pynear import transactions
from pynear.constants import TGAS
from pynear.dapps.core import NEAR
from starlette.responses import RedirectResponse

from connection_manager import (
    actions_to_link,
)

router = APIRouter()


@router.get("/keypom/{password}")
def redirect_to_keypom(
    password: str,
):
    link = actions_to_link(
        [
            (
                "keypom.near",
                [
                    transactions.create_function_call_action(
                        "claim",
                        json.dumps({"password": password}).encode("utf8"),
                        50 * TGAS,
                        0,
                    )
                ],
            )
        ]
    )
    return RedirectResponse(url=link)


@router.get("/sent/{reciver_id}")
def redirect_to_sent(
    reciver_id: str,
    amount: int = NEAR // 10,
):
    link = actions_to_link(
        [
            (
                reciver_id,
                [transactions.create_transfer_action(amount)],
            )
        ]
    )
    return RedirectResponse(url=link)


@router.get("/test/sent2/{reciver_id}")
def redirect_to_sent(
    reciver_id: str,
    amount: int = NEAR // 10,
):
    link = actions_to_link(
        [
            (
                reciver_id,
                [
                    transactions.create_transfer_action(amount),
                    transactions.create_transfer_action(amount),
                ],
            )
        ]
    )
    return RedirectResponse(url=link)


@router.get("/test/3/{receiver_id}")
def redirect_to_sent(
    receiver_id: str,
    amount: int = NEAR // 10,
):
    link = actions_to_link(
        [
            (
                receiver_id,
                [
                    transactions.create_transfer_action(amount),
                ],
            ),
            (
                "a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.factory.bridge.near",
                [
                    transactions.create_function_call_action(
                        "ft_transfer",
                        json.dumps(
                            {"receiver_id": receiver_id, "amount": "100"}
                        ).encode("utf8"),
                        25 * TGAS,
                        1,
                    ),
                ],
            ),
            (
                "{{signer_id}}",
                [
                    transactions.create_function_call_access_key_action(
                        "F5KkCsjjbiS2NXuJBEChYWWP1JLvRra7yKzLGbqPnPJG",
                        25 * TGAS,
                        "storage.herewallet.near",
                        [],
                    ),
                ],
            ),
        ]
    )
    return RedirectResponse(url=link)
