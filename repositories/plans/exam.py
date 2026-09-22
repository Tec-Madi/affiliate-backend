from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.plans.exam import ExamPlan, Exam

class ExamRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, id: int, name: str, is_active: bool):
        exam = Exam(
            id=id, 
            name=name, 
            is_active=is_active
        )
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get_by_id(self, id: int):
        return self.db.execute(select(Exam).where(Exam.id == id)).scalar_one_or_none()

class ExamPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, exam_id: int, amount: Decimal, discount: Decimal, discount_type: str, agent_dicount: Decimal, agent_dicount_type: str, api_discount: Decimal, api_discount_type: str, is_active: bool):
        exam_plan = ExamPlan(
            exam_id=exam_id,
            amount=amount,
            discount=discount,
            discount_type=discount_type,
            agent_dicount=agent_dicount,
            agent_dicount_type=agent_dicount_type,
            api_discount=api_discount,
            api_discount_type=api_discount_type,
            is_active=is_active
        )
        self.db.add(exam_plan)
        self.db.commit()
        self.db.refresh(exam_plan)
        return exam_plan

    def get_by_id(self, id: int):
        return self.db.execute(select(ExamPlan).where(ExamPlan.id == id)).scalar_one_or_none()

    def get_by_exam_id(self, exam_id: int):
        return self.db.execute(select(ExamPlan).where(ExamPlan.exam_id == exam_id)).scalar_one_or_none()

    