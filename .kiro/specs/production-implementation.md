# Spec: Production Implementation - Live Pricing & Full KYC

## Overview
Complete the production-ready implementation of КиберЛомбард with live pricing from multiple sources, full KYC verification, flexible term selection, and legal compliance for court proceedings.

## Current Status
- ✅ Phase 1-5 services created (pricing, KYC, contracts, payouts)
- ✅ Basic database models exist
- ⚠️ Missing: New database models for KYC, signatures, audit logs
- ⚠️ Missing: API endpoints for KYC, contract signing, payouts
- ⚠️ Missing: Frontend components for term slider, KYC forms, contract signing
- ⚠️ Using demo prices instead of real API integrations

## User Stories

### US-1: Live Pricing from Multiple Sources
**As a** user  
**I want** to see real-time prices from Lis-Skins, market.csgo, and Steam Market  
**So that** I know the exact value of my items and the loan amount I'll receive

**Acceptance Criteria:**
- Item cards display 3 prices: Steam Market, Lis-Skins, market.csgo
- Instant price is calculated as min(lis_price, market_csgo_price)
- Items without Lis-Skins instant sell price are marked as "not acceptable"
- Items with instant_price < 20₽ are not accepted
- Prices are cached for 1 hour
- Clear error messages when price APIs are unavailable

### US-2: Flexible Term Selection (7-30 Days)
**As a** user  
**I want** to choose my buyback term between 7-30 days using a slider  
**So that** I can select terms that fit my financial situation

**Acceptance Criteria:**
- Slider allows selection from 7 to 30 days (1-day increments)
- Buyback price updates in real-time as slider moves
- Interest and premium are interpolated for intermediate values
- Expiry date is calculated and displayed
- Detailed breakdown shows: loan percent, interest, premium

### US-3: Phone Verification via SMS
**As a** user  
**I want** to verify my phone number via SMS code  
**So that** I can proceed with creating deals

**Acceptance Criteria:**
- User enters phone number (+7XXXXXXXXXX format)
- 6-digit SMS code is sent (TTL: 5 minutes)
- User enters code to verify
- Rate limit: 1 SMS per minute per phone
- Code is hashed before storage
- Clear error messages for invalid/expired codes

### US-4: Passport Verification (KYC)
**As a** user  
**I want** to submit my passport details  
**So that** I can complete KYC verification for deals

**Acceptance Criteria:**
- Form collects: full name, birth date, passport series/number, issued by, issue date, department code
- Photo upload for passport scan
- Data is sent to KYC provider (sumsub or fake for dev)
- Status tracking: pending → passed/failed
- User cannot proceed without passed KYC
- Clear feedback on verification status

### US-5: Electronic Contract Signing
**As a** user  
**I want** to sign the deal contract electronically via SMS  
**So that** the deal is legally binding

**Acceptance Criteria:**
- User reviews full contract with all terms
- Checkbox: "I agree to the terms"
- "Sign" button sends SMS with signature code
- User enters signature code to complete signing
- Contract PDF is generated with signature details
- Contract hash (SHA-256) is stored for immutability
- All signing details logged: timestamp, IP, user-agent, phone

### US-6: SBP Payout
**As a** user  
**I want** to receive my loan amount via SBP (Fast Payment System)  
**So that** I get money quickly without fees

**Acceptance Criteria:**
- User selects SBP as payout method
- Payout is created via provider (modulbank or fake for dev)
- Status tracking: pending → processing → completed/failed
- Clear error messages if payout fails
- Payout limits: 100₽ - 600,000₽

### US-7: Audit Logging for Legal Compliance
**As a** system administrator  
**I want** all critical actions logged with full context  
**So that** we have evidence for court proceedings if needed

**Acceptance Criteria:**
- All critical actions logged: login, deal creation, contract signing, trades, payouts
- Each log includes: user_id, deal_id, action, timestamp, IP, user-agent, details (JSON)
- Admin endpoint to export full legal package for a deal
- Legal package includes: deal data, user data, KYC verification, signature details, trades, payouts, audit logs

## Technical Requirements

### Database Models to Add

```python
class KYCVerification(Base):
    """Passport verification records"""
    id: int
    user_id: int
    verification_id: str  # External provider ID
    status: str  # pending, passed, failed
    full_name: str
    birth_date: date
    passport_series: str
    passport_number: str
    issued_by: str
    issue_date: date
    department_code: str
    photo_url: str
    provider_response: JSON
    created_at: datetime
    verified_at: datetime

class DealSignature(Base):
    """Electronic signature records"""
    id: int
    deal_id: int
    user_id: int
    phone: str
    signature_code_hash: str
    signature_timestamp: datetime
    ip_address: str
    user_agent: str
    contract_hash: str
    contract_version: str
    contract_pdf_url: str
    kyc_verification_id: str
    terms_accepted_at: datetime

class SBPPayout(Base):
    """SBP payout records"""
    id: int
    deal_id: int
    payout_id: str  # External provider ID
    phone: str
    amount: float
    status: str  # pending, processing, completed, failed
    error_code: str
    error_message: str
    provider_response: JSON
    created_at: datetime
    updated_at: datetime
    completed_at: datetime
```

### API Endpoints to Add

```
POST /api/kyc/phone/send-code
POST /api/kyc/phone/verify-code
POST /api/kyc/passport/submit
GET  /api/kyc/passport/status/{verification_id}

POST /api/deals/{deal_id}/sign/init
POST /api/deals/{deal_id}/sign/complete
GET  /api/deals/{deal_id}/contract

POST /api/deals/{deal_id}/payout/create
GET  /api/deals/{deal_id}/payout/status

GET  /api/admin/deals/{deal_id}/legal-package
```

### Frontend Components to Create

```
components/TermSlider.tsx
  - Range input 7-30 days
  - Real-time buyback calculation
  - Expiry date display
  - Breakdown of interest/premium

components/PhoneVerification.tsx
  - Phone input with validation
  - Send code button
  - Code input (6 digits)
  - Verify button
  - Status feedback

components/PassportForm.tsx
  - All passport fields
  - Photo upload
  - Submit button
  - Status display

components/ContractSigning.tsx
  - Contract PDF viewer
  - Terms checkbox
  - Sign button (sends SMS)
  - Signature code input
  - Complete button

components/ItemCard.tsx (update)
  - Display 3 prices
  - Show instant price
  - Mark unacceptable items
  - Visual indicators
```

## Implementation Plan

### Phase 1: Database Models (2-4 hours)
1. Add KYCVerification, DealSignature, SBPPayout models to `backend/models.py`
2. Create Alembic migration
3. Run migration on dev database
4. Test model relationships

### Phase 2: API Endpoints (4-6 hours)
1. Implement KYC endpoints in `backend/main.py`
2. Implement contract signing endpoints
3. Implement payout endpoints
4. Add middleware for IP/user-agent logging
5. Test all endpoints with Postman/curl

### Phase 3: Frontend Components (6-8 hours)
1. Create TermSlider component with live calculation
2. Create PhoneVerification component
3. Create PassportForm component
4. Create ContractSigning component
5. Update ItemCard to show multiple prices
6. Integrate components into deal flow

### Phase 4: Real API Integrations (4-6 hours)
1. Get API keys from Lis-Skins, market.csgo
2. Update `lisskins_service.py` with real API calls
3. Update `market_csgo_service.py` with real API calls
4. Test price fetching with real data
5. Verify fallback logic works

### Phase 5: Testing (4-6 hours)
1. Unit tests for pricing calculations
2. Unit tests for KYC services
3. Integration tests for full deal flow
4. E2E test: create deal with real prices
5. Test error scenarios

### Phase 6: Configuration & Deployment (2-4 hours)
1. Update `.env.example` with all required keys
2. Document API key acquisition process
3. Test with fake providers
4. Test with real providers (staging)
5. Deploy to production

## Definition of Done

- [ ] All database models created and migrated
- [ ] All API endpoints implemented and tested
- [ ] All frontend components created and integrated
- [ ] Real API integrations working (or fake providers for dev)
- [ ] Full deal flow works end-to-end
- [ ] All critical actions are logged
- [ ] Error handling is comprehensive
- [ ] Documentation is updated
- [ ] Code is reviewed and approved

## Risks & Mitigations

**Risk:** API keys not available  
**Mitigation:** Use fake providers for development, clearly mark demo mode in UI

**Risk:** KYC provider integration complex  
**Mitigation:** Start with fake provider, document integration requirements

**Risk:** SMS costs too high  
**Mitigation:** Implement rate limiting, use fake provider for dev/testing

**Risk:** Legal compliance requirements change  
**Mitigation:** Make contract templates configurable, version all contracts

## Success Metrics

- All items show real prices from 3 sources
- Users can select any term from 7-30 days
- KYC verification completes in < 5 minutes
- Contract signing works via SMS
- Payouts complete in < 5 minutes
- 100% of critical actions are logged
- Zero data loss in audit logs

## Notes

- All services support fake providers for development
- Real integrations require API keys from external providers
- Legal compliance is critical - all actions must be logged
- Contract language avoids prohibited terms (ломбард, залог, кредит)
- Use "выкуп цифровых прав" and "опцион" terminology
