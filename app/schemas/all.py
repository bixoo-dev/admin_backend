from pydantic import BaseModel, model_validator

from typing import Optional

from datetime import datetime



class Token(BaseModel):

    access_token: str

    token_type: str



class TokenData(BaseModel):

    id: Optional[str] = None



class AdminResponse(BaseModel):

    id: str

    name: str

    email: str

    role: str



from pydantic import BaseModel, model_validator

from typing import Optional

from datetime import datetime



class AccountBase(BaseModel):

    id: str

    entity_type: str

    business_name: str

    contact_number: Optional[str] = None

    email: Optional[str] = None

    gstin: Optional[str] = None

    registration_number: Optional[str] = None

    address: Optional[str] = None

    fleet_docs_status: Optional[str] = None

    verification_status: str



class AccountCreate(AccountBase):

    pass



class AccountUpdate(BaseModel):

    business_name: Optional[str] = None

    contact_number: Optional[str] = None

    email: Optional[str] = None

    gstin: Optional[str] = None

    registration_number: Optional[str] = None

    address: Optional[str] = None

    fleet_docs_status: Optional[str] = None

    verification_status: Optional[str] = None



class AccountResponse(AccountBase):

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None

    

    type: str = ''

    businessName: str = ''

    contactMasked: str = ''

    verificationStatus: str = ''

    contactNumber: str = ''

    registrationNumber: str = ''

    fleetDocsStatus: str = ''



    @model_validator(mode='after')

    def map_fields(self):

        self.type = self.entity_type

        self.businessName = self.business_name

        self.verificationStatus = self.verification_status

        self.contactNumber = self.contact_number or ''

        self.registrationNumber = self.registration_number or ''

        self.fleetDocsStatus = self.fleet_docs_status or ''

        

        if self.contact_number and len(self.contact_number) > 4:

            self.contactMasked = '*' * (len(self.contact_number) - 4) + self.contact_number[-4:]

        else:

            self.contactMasked = self.contact_number or ''

        return self

        

    class Config:

        from_attributes = True



class DecisionRequest(BaseModel):

    actionType: str

    reasonCode: Optional[str] = None

    notes: Optional[str] = None

    timestamp: Optional[str] = None



class ActionResponse(BaseModel):

    success: bool

    message: str




class BidResponse(BaseModel):
    id: str
    auction_id: str
    buyer_id: str
    amount: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AuctionDetailResponse(BaseModel):
    id: str
    seller_id: str
    product: str
    qty: Optional[str] = None
    unit: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str
    winner_computed: bool
    winning_buyer_id: Optional[str]
    winning_amount: Optional[str]
    winning_timestamp: Optional[datetime]
    linked_order_id: Optional[str]
    is_flagged: bool
    
    # frontend mapped fields
    lotId: str = ''
    sellerId: str = ''
    winnerComputed: bool = False
    winningBid: Optional[dict] = None
    linkedOrder: Optional[str] = None
    flagged: bool = False
    bidCount: int = 0
    bids: list[BidResponse] = []
    
    @model_validator(mode='after')
    def map_fields(self):
        self.lotId = self.id
        self.sellerId = self.seller_id
        self.winnerComputed = self.winner_computed
        if self.winning_amount and self.winning_buyer_id:
            self.winningBid = {'amount': self.winning_amount, 'buyerId': self.winning_buyer_id}
        self.linkedOrder = self.linked_order_id
        self.flagged = self.is_flagged
        return self

    class Config:
        from_attributes = True

class VoidLotRequest(BaseModel):
    reason: str
class Config:

        from_attributes = True



class ListingResponse(BaseModel):

    id: str

    seller_id: str

    category: Optional[str]

    product_name: Optional[str]

    unit_price: Optional[str]

    status: Optional[str]

    is_flagged: bool

    sellerId: str = ''

    productName: str = ''

    unitPrice: str = ''

    flagged: bool = False

    

    @model_validator(mode='after')

    def map_fields(self):

        self.sellerId = self.seller_id

        self.productName = self.product_name or ''

        self.unitPrice = self.unit_price or ''

        self.flagged = self.is_flagged

        return self



    class Config:

        from_attributes = True



class RequirementResponse(BaseModel):

    id: str

    buyer_id: str

    product: str

    total_requested: float

    unit: str

    remaining_qty: float

    status: str

    is_flagged: bool

    offers: list = []

    

    buyerId: str = ''

    totalRequested: float = 0

    remainingQty: float = 0

    flagged: bool = False

    

    @model_validator(mode='after')

    def map_fields(self):

        self.buyerId = self.buyer_id

        self.totalRequested = float(self.total_requested)

        self.remainingQty = float(self.remaining_qty)

        self.flagged = self.is_flagged

        return self



    class Config:

        from_attributes = True



class OrderResponse(BaseModel):

    id: str

    buyer_id: str

    seller_id: str

    source_type: str

    source_ref: str

    agreed_qty: str

    total_value: str

    logistics_linked: Optional[str]

    status: str

    

    buyerId: str = ''

    sellerId: str = ''

    sourceType: str = ''

    sourceRef: str = ''

    agreedQty: str = ''

    totalValue: str = ''

    logisticsLinked: Optional[str] = None

    

    @model_validator(mode='after')

    def map_fields(self):

        self.buyerId = self.buyer_id

        self.sellerId = self.seller_id

        self.sourceType = self.source_type

        self.sourceRef = self.source_ref

        self.agreedQty = self.agreed_qty

        self.totalValue = self.total_value

        self.logisticsLinked = self.logistics_linked

        return self



    class Config:

        from_attributes = True



class TripResponse(BaseModel):

    id: str

    order_id: str

    transporter: str

    route: str

    current_milestone: str

    gps_last_seen: str

    is_gps_stale: bool

    consignee_proof_submitted: bool

    

    tripId: str = ''

    orderId: str = ''

    currentMilestone: str = ''

    gpsLastSeen: str = ''

    isGpsStale: bool = False

    consigneeProofSubmitted: bool = False

    

    @model_validator(mode='after')

    def map_fields(self):

        self.tripId = self.id

        self.orderId = self.order_id

        self.currentMilestone = self.current_milestone

        self.gpsLastSeen = self.gps_last_seen

        self.isGpsStale = self.is_gps_stale

        self.consigneeProofSubmitted = self.consignee_proof_submitted

        return self



    class Config:

        from_attributes = True



class SettlementResponse(BaseModel):

    id: str

    trip_id: str

    payee: str

    amount: str

    proof_status: str

    settlement_status: str

    bank_ref_masked: str

    

    settlementId: str = ''

    tripId: str = ''

    proofStatus: str = ''

    settlementStatus: str = ''

    bankRefMasked: str = ''

    

    @model_validator(mode='after')

    def map_fields(self):

        self.settlementId = self.id

        self.tripId = self.trip_id

        self.proofStatus = self.proof_status

        self.settlementStatus = self.settlement_status

        self.bankRefMasked = self.bank_ref_masked

        return self



    class Config:

        from_attributes = True



class CaseResponse(BaseModel):

    id: str

    type: str

    linked_entity: str

    reporter_id: str

    status: str

    sla: str

    evidence_attached: bool

    

    caseId: str = ''

    linkedEntity: str = ''

    reporterId: str = ''

    evidenceAttached: bool = False

    

    @model_validator(mode='after')

    def map_fields(self):

        self.caseId = self.id

        self.linkedEntity = self.linked_entity

        self.reporterId = self.reporter_id

        self.evidenceAttached = self.evidence_attached

        return self



    class Config:

        from_attributes = True



class DashboardMetricsResponse(BaseModel):

    verification_backlog: int

    overdue_trips: int

    pending_settlements_value: str

    open_disputes: int

    matching_engine_lag: str

    auction_close_failures: int

    pending_settlement_age: str

    recent_overrides: list

    

    # Additional Analytics

    total_buyers: int

    total_sellers: int

    verified_buyers: int

    verified_sellers: int

    total_requirements: int

    completed_trips: int



class AuditLogResponse(BaseModel):

    id: str

    actor_id: str

    action: str

    target_id: str

    reason: Optional[str] = None

    ip_address: Optional[str] = None

    timestamp: datetime



    actorId: str = ''

    targetId: str = ''

    reasonCode: Optional[str] = None

    ipAddress: Optional[str] = None



    @model_validator(mode='after')

    def map_fields(self):

        self.actorId = self.actor_id

        self.targetId = self.target_id

        self.reasonCode = self.reason

        self.ipAddress = self.ip_address

        return self



    class Config:

        from_attributes = True

import json


class AdminResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    department: Optional[str] = None
    roleTitle: Optional[str] = None
    employeeId: Optional[str] = None
    status: Optional[str] = None
    joinedDate: Optional[str] = None
    lastActive: Optional[str] = None
    loginIp: Optional[str] = None
    twoFactorEnabled: bool = False
    onboardingStep: Optional[str] = None
    inviteLink: Optional[str] = None
    inviteSentAt: Optional[str] = None
    modules: dict = {}
    activitySummary: list = []
    notes: Optional[str] = None
    
    @model_validator(mode='before')
    def map_from_db(cls, values):
        if not isinstance(values, dict):
            values = values.__dict__
        return {
            'id': values.get('id'),
            'name': values.get('name'),
            'email': values.get('email'),
            'role': values.get('role'),
            'phone': values.get('phone'),
            'department': values.get('department'),
            'roleTitle': values.get('role_title'),
            'employeeId': values.get('employee_id'),
            'status': values.get('status'),
            'joinedDate': str(values.get('joined_date'))[:10] if values.get('joined_date') else None,
            'lastActive': values.get('last_active'),
            'loginIp': values.get('login_ip'),
            'twoFactorEnabled': values.get('two_factor_enabled') or False,
            'onboardingStep': values.get('onboarding_step'),
            'inviteLink': values.get('invite_link'),
            'inviteSentAt': str(values.get('invite_sent_at')) if values.get('invite_sent_at') else None,
            'modules': json.loads(values.get('modules')) if values.get('modules') else {},
            'activitySummary': json.loads(values.get('activity_summary')) if values.get('activity_summary') else [],
            'notes': values.get('notes'),
        }

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class AdminCreateRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    department: Optional[str] = None
    roleTitle: Optional[str] = None
    employeeId: Optional[str] = None
    requireTwoFactor: Optional[bool] = False
    modules: Optional[dict] = {}
    notes: Optional[str] = None

class AdminActionRequest(BaseModel):
    action: str
    moduleId: Optional[str] = None
    forcedValue: Optional[bool] = None
    modulesPreset: Optional[dict] = None
    presetName: Optional[str] = None
    status: Optional[str] = None


