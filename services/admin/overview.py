from datetime import date

from sqlalchemy.orm import Session

from core.error.http import AdminOnlyError
from models.users import Services, User
from repositories.users import TxnRepository, UserRepository, WalletRepository


def admin_overview_function(
    user: User,
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None
):
    if not user.is_admin:
        raise AdminOnlyError()

    user_repo = UserRepository(db)
    wallet_repo = WalletRepository(db)
    txn_repo = TxnRepository(db)

    total_user = user_repo.get_total(start_date, end_date)
    total_balance = wallet_repo.get_total()
    total_txn = txn_repo.get_total(start_date, end_date)

    success_rate = (
        round(
            (
                (total_txn.total_success or 0)
                + (total_txn.total_completed or 0)
            )
            / total_txn.total_txn
            * 100,
            2
        )
        if total_txn.total_txn
        else 0
    )

    return {
        "user": {
            "total": total_user.total_users,
            "active": total_user.active_users,
            "smart": total_user.smart_users,
            "agent": total_user.agent_users,
            "admin": total_user.total_admin
        },
        "wallet": {
            "total_balance": f"₦{total_balance.total_balance or 0: ,}",
            "total_bonus": f"₦{total_balance.total_bonus_balance or 0: ,}"
        },
        "transaction": {
            "total": total_txn.total_txn,
            "total_success": total_txn.total_success,
            "total_failed": total_txn.total_failed,
            "total_pending": total_txn.total_pending,
            "total_reversed": total_txn.total_reversed,
            "total_completed": total_txn.total_completed,
            "success_rate": f"{success_rate: ,}%",
            "total_funding": f"₦{total_txn.total_funding or 0: ,}",
            "total_sold": f"₦{total_txn.total_sold or 0: ,}",
            "airtime_sold": f"₦{total_txn.airtime_sold or 0: ,}",
            "data_sold": f"{total_txn.data_sold or 0: ,} GB",
            "cable_sold": f"₦{total_txn.cable_sold or 0: ,}",
            "disco_sold": f"₦{total_txn.disco_sold or 0: ,}",
        }
    }


def sales_overview_function(
    user: User,
    db: Session,
    limit: int = 20,
    start_date: date | None = None,
    end_date: date | None = None
):
    if not user.is_admin:
        raise AdminOnlyError()

    txn_repo = TxnRepository(db)
    user_repo = UserRepository(db)

    sales = txn_repo.sales(start_date=start_date, end_date=end_date)
    total_txn = txn_repo.get_total(start_date, end_date)
    leader_board = user_repo.user_leaderboard(
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )

    success_rate = (
        round(
            (
                (total_txn.total_success or 0)
                + (total_txn.total_completed or 0)
            )
            / total_txn.total_txn
            * 100,
            2
        )
        if total_txn.total_txn
        else 0
    )

    return {
        "transaction": {
            "total": total_txn.total_txn,
            "total_success": total_txn.total_success,
            "total_failed": total_txn.total_failed,
            "total_pending": total_txn.total_pending,
            "total_reversed": total_txn.total_reversed,
            "total_completed": total_txn.total_completed,
            "success_rate": f"{success_rate: ,}%",
            "total_funding": f"₦{total_txn.total_funding or 0:,}",
            "total_sold": f"₦{total_txn.total_sold or 0:,}",
            "airtime_sold": f"₦{total_txn.airtime_sold or 0:,}",
            "data_sold": f"{total_txn.data_sold or 0:,} GB",
            "cable_sold": f"₦{total_txn.cable_sold or 0:,}",
            "disco_sold": f"₦{total_txn.disco_sold or 0:,}",
        },
        "airtime_sales": [{
            "network": sale["biller"],
            "airtime_type": sale["biller_type"],
            "value": f"₦{sale['airtime_value'] or 0:,}",
            "amount": f"₦{sale['airtime_amount'] or 0:,}"
        } for sale in sales if sale["service"] == Services.AIRTIME.value],
        "data_sales": [{
            "network": sale["biller"],
            "data_type": sale["biller_type"],
            "value": f"{sale['data_value'] or 0:,} GB",
            "amount": f"₦{sale['data_amount'] or 0:,}"
        } for sale in sales if sale["service"] == Services.DATA.value],
        "cable_sales": [{
            "cable": sale["biller"],
            "value": f"₦{sale['cable_value'] or 0:,}",
            "amount": f"₦{sale['cable_amount'] or 0:,}"
        } for sale in sales if sale["service"] == Services.CABLE.value],
        "disco_sales": [{
            "disco": sale["biller"] or "",
            "disco_type": sale["biller_type"] or "",
            "value": f"₦{sale['airtime_value'] or 0:,}",
            "amount": f"₦{sale['airtime_amount'] or 0:,}"
        } for sale in sales if sale["service"] == Services.DISCO.value],
        "top_users": [{
            "name": board.name,
            "email": board.email,
            "total": board.total,
            "amount": f"₦{board.amount or 0: ,}"
        } for board in leader_board]
    }