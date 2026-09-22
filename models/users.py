from datetime import datetime, date

from sqlalchemy import String, Enum, Numeric, ForeignKey, Text, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from core.database import Base

from enum import Enum as pyEnum

from models.admin import PaymentProvider

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(50))
    middle_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50), nullable=False, index=True, unique=True)
    number: Mapped[str] = mapped_column(String(20), nullable=False, index=True, unique=True)
    pin: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_agent: Mapped[bool] = mapped_column(default=False, nullable=True)
    is_admin: Mapped[bool] =  mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    wallet: Mapped['Wallet'] = relationship('Wallet', uselist=False, back_populates='user')
    transactions: Mapped[list['Transaction']] = relationship('Transaction', back_populates='user')
    bonus_transactions: Mapped[list['BonusTransaction']] = relationship('BonusTransaction', back_populates='user', order_by=lambda: BonusTransaction.created_at.desc(),)
    accounts: Mapped[list['VirtualAccount']] = relationship('VirtualAccount', back_populates='user')
    user_kyc: Mapped['UserKYC'] = relationship('UserKYC', uselist=False, back_populates='user')
    user_api_key: Mapped['UserAPIKey'] = relationship('UserAPIKey', uselist=False)

class UserKYC(Base):
    __tablename__ = 'user_kycs'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True, unique=True)
    first_name: Mapped[str | None] = mapped_column(String(50))
    middle_name: Mapped[str | None] = mapped_column(String(20))
    last_name: Mapped[str | None] = mapped_column(String(20))
    full_name: Mapped[str | None] = mapped_column(String(100))
    phone_number: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(20))
    gender: Mapped[str | None] = mapped_column(String(10))
    state_of_origin: Mapped[str | None] = mapped_column(String(20))
    lga_of_origin: Mapped[str | None] = mapped_column(String(30))
    residential_address: Mapped[str | None] = mapped_column(String(20))
    nationality: Mapped[str | None] = mapped_column(String(20))
    nin: Mapped[str | None] = mapped_column(String(250), nullable=True)
    bvn: Mapped[str | None] = mapped_column(String(250), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20))
    nin_is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    bvn_is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)

    user: Mapped['User'] = relationship('User', back_populates='user_kyc')


class UserAPIKey(Base):
    __tablename__ = 'users_api_key'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True, unique=True)
    api_key: Mapped[str] = mapped_column(String(250), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
 
    user: Mapped['User'] = relationship('User', back_populates='user_api_key')

class Wallet(Base):
    __tablename__ = 'walletes'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index= True, nullable=False, unique=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0.0)
    bonus: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0.0)

    user: Mapped['User'] = relationship('User', back_populates='wallet')

class OTP(Base):
    __tablename__ = 'otps'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index= True, nullable=False)
    otp: Mapped[str] = mapped_column(String(250))
    expiry_time: Mapped[datetime] = mapped_column()
    token: Mapped[str | None] = mapped_column(String(250))
    token_expiry_time: Mapped[datetime | None] = mapped_column()
    is_used: Mapped[bool] = mapped_column(default=False)

class VirtualAccount(Base):
    __tablename__ = 'virtual_accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index= True, nullable=False)
    provider: Mapped[str] = mapped_column(ForeignKey('payment_providers.name', ondelete='CASCADE'))
    bank_code: Mapped[str] = mapped_column(default='1')
    bank_name: Mapped[str] = mapped_column(String(50), nullable=False)
    account_number: Mapped[str] = mapped_column(String(20), nullable=False)
    account_name: Mapped[str] = mapped_column(String(50), nullable=False)
    account_reference: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    user: Mapped['User'] = relationship('User', back_populates='accounts', passive_deletes=True)
    payment_provider: Mapped['PaymentProvider'] = relationship('PaymentProvider', passive_deletes=True)

class Gender(str, pyEnum):
    MALE = 'male'
    FEMALE = 'female'

class IDType(str, pyEnum):
    NIN = 'nin'
    BVN = 'bvn'

class KYCStatus(str, pyEnum):
    VERIFIED = 'verified'
    PENDING = 'pending'
    REJECTED = 'rejected'

class Services(str, pyEnum):
    NETWORK = "network"
    AIRTIME = 'airtime'
    DATA = 'data'
    CABLE = 'cable'
    DISCO = 'disco'
    EXAM = 'exam'
    FUNDING = 'funding'
    KYC = 'kyc'

class Status(str, pyEnum):
    SUCCESS = 'successful'
    FAIL = 'failed'
    PENDING = 'pending'
    REVERSED = 'reversed'
    COMPLETED = 'completed'

class TxnType(str, pyEnum):
    CREDIT = 'credit'
    DEBIT = 'debit'

class UpdateTxntype(str, pyEnum):
    COMPLETE = 'complete'
    REFUND = 'refund'

class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    reference: Mapped[str] = mapped_column(String(250), nullable=False, index=True, unique=True)
    request_id: Mapped[str | None] = mapped_column(String(250), nullable=True)
    provider_reference: Mapped[str | None] = mapped_column(String(250), nullable=True)
    service: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    service_provider: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(String(20), nullable=True, index=True)
    product: Mapped[str] = mapped_column(String(50), nullable=True)
    beneficiary: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    message: Mapped[str] = mapped_column(String(100), nullable=False)
    api_response: Mapped[str] = mapped_column(Text, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    old_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    new_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    token: Mapped[str] = mapped_column(String(100), nullable=True)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    service_from: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    user: Mapped['User'] = relationship('User', back_populates='transactions')

class BonusTransaction(Base):
    __tablename__ = 'bonus_transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    reference: Mapped[str] = mapped_column(String(250), nullable=False, index=True, unique=True)
    message: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    old_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    new_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    txn_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    user: Mapped['User'] = relationship('User', back_populates='bonus_transactions')