# Requirements: Production-Ready КиберЛомбард

## Functional Requirements

### FR-1: Multi-Source Price Aggregation
**Priority:** Critical  
**Status:** Partially Implemented

The system must aggregate prices from three sources:
1. **Steam Market** - Reference price (справочная цена)
2. **Lis-Skins** - Instant sell price (приоритет)
3. **market.csgo** - Market/instant price (резерв)

**Rules:**
- `instant_price = min(lis_price, market_csgo_price)`
- Accept item only if: `lis_price > 0 AND instant_price >= 20₽`
- Cache prices for 1 hour
- Fallback to cached prices if APIs unavailable

**Current State:**
- ✅ Services created: `lisskins_service.py`, `market_csgo_service.py`, `price_aggregator.py`
- ⚠️ Using demo data, not real API calls
- ✅ Caching implemented
- ✅ Fallback logic exists

**Remaining Work:**
- Get real API keys
- Implement actual API calls
- Test with production data

---

### FR-2: Dynamic Loan Percentage
**Priority:** Critical  
**Status:** Implemented

Loan percentage varies by item price:
- 0-500₽ → 60%
- 500-5000₽ → 65%
- 5000+₽ → 70%

**Current State:**
- ✅ Implemented in `pricing_service.py`
- ✅ Configurable in `config.py`

---

### FR-3: Flexible Term Selection
**Priority:** Critical  
**Status:** Backend Ready, Frontend Missing

Users can select buyback term from 7-30 days with 1-day increments.

**Interest & Premium by Term:**
- 7 days: 10% interest + 5% premium
- 14 days: 15% interest + 7% premium
- 21 days: 20% interest + 9% premium
- 30 days: 25% interest + 10% premium

**Intermediate values:** Linear interpolation

**Formula:**
```
loan_amount = sum(item.instant_price * get_loan_percent(item.instant_price))
base_buyback = loan_amount * (1 + interest)
buyback_price = base_buyback * (1 + premium)
```

**Current State:**
- ✅ Backend logic in `pricing_service.py`
- ✅ Interpolation implemented
- ❌ Frontend slider missing

**Remaining Work:**
- Create TermSlider component
- Add real-time calculation
- Display breakdown

---

### FR-4: Phone Verification
**Priority:** Critical  
**Status:** Backend Ready, Frontend Missing

**Flow:**
1. User enters phone (+7XXXXXXXXXX)
2. System sends 6-digit SMS code
3. User enters code (TTL: 5 minutes)
4. System verifies and marks phone as verified

**Security:**
- Codes are hashed (SHA-256) before storage
- Rate limit: 1 SMS per minute per phone
- Codes expire after 5 minutes

**Current State:**
- ✅ `sms_service.py` created
- ✅ Supports fake, sms.ru, smsc.ru providers
- ✅ Endpoints exist in `main.py`
- ❌ Frontend component missing

**Remaining Work:**
- Create PhoneVerification component
- Get SMS provider API key
- Test with real SMS

---

### FR-5: Passport Verification (KYC)
**Priority:** Critical  
**Status:** Backend Ready, Frontend Missing

**Required Fields:**
- Full name (3 fields: last, first, middle)
- Birth date
- Passport series & number
- Issued by
- Issue date
- Department code
- Photo of passport scan

**Verification Flow:**
1. User submits form with photo
2. Data sent to KYC provider (Sumsub)
3. Provider checks document authenticity
4. Status: pending → passed/failed
5. User cannot create deals without passed status

**Current State:**
- ✅ `kyc_service.py` created
- ✅ Supports fake, sumsub providers
- ✅ Basic endpoints exist
- ❌ Frontend form missing
- ❌ Photo upload not implemented

**Remaining Work:**
- Create PassportForm component
- Implement photo upload
- Get Sumsub API key
- Add status polling

---

### FR-6: Electronic Contract Signing
**Priority:** Critical  
**Status:** Backend Ready, Frontend Missing

**Signing Flow:**
1. User reviews contract (PDF)
2. Checks "I agree" checkbox
3. Clicks "Sign" → SMS code sent
4. User enters signature code
5. System creates signature record
6. Contract PDF generated with signature details

**Signature Record:**
- User ID, deal ID, phone
- Signature code hash
- Timestamp, IP address, user-agent
- Contract hash (SHA-256)
- Contract version
- KYC verification ID

**Current State:**
- ✅ `contract_service.py` created
- ✅ HTML contract generation
- ✅ Hash calculation
- ❌ PDF generation not implemented
- ❌ Frontend component missing
- ❌ DealSignature model missing

**Remaining Work:**
- Add DealSignature model
- Implement PDF generation (weasyprint)
- Create ContractSigning component
- Add signature endpoints

---

### FR-7: SBP Payouts
**Priority:** Critical  
**Status:** Backend Ready, Frontend Missing

**Payout Flow:**
1. Deal is signed and trade accepted
2. System creates SBP payout
3. Money sent to user's phone number
4. Status tracked: pending → processing → completed/failed

**Limits:**
- Min: 100₽
- Max: 600,000₽

**Current State:**
- ✅ `sbp_service.py` created
- ✅ Supports fake, modulbank providers
- ❌ SBPPayout model missing
- ❌ Payout endpoints missing
- ❌ Frontend integration missing

**Remaining Work:**
- Add SBPPayout model
- Add payout endpoints
- Get Modulbank API key
- Implement webhook handler
- Add status polling

---

### FR-8: Audit Logging
**Priority:** Critical  
**Status:** Partially Implemented

**Requirements:**
- Log all critical actions
- Include: user_id, deal_id, action, timestamp, IP, user-agent, details (JSON)
- Immutable logs (append-only)
- Admin endpoint to export legal package

**Actions to Log:**
- steam_login
- phone_verified
- kyc_submitted
- kyc_verified
- deal_created
- contract_signed
- trade_sent
- trade_accepted
- payout_created
- payout_completed
- buyback_initiated
- buyback_completed
- deal_defaulted

**Current State:**
- ✅ AuditLog model exists
- ✅ Some actions logged
- ❌ Not all critical actions logged
- ❌ IP/user-agent not captured everywhere
- ❌ Legal package endpoint missing

**Remaining Work:**
- Add middleware to capture IP/user-agent
- Log all critical actions
- Create legal package endpoint
- Test log completeness

---

## Non-Functional Requirements

### NFR-1: Performance
- Price fetching: < 3 seconds for 50 items
- API response time: < 500ms (95th percentile)
- Database queries: < 100ms
- Cache hit rate: > 80% for prices

### NFR-2: Reliability
- API uptime: 99.5%
- Fallback to cached prices if external APIs down
- Graceful degradation (show estimated prices if needed)
- Retry logic for transient failures

### NFR-3: Security
- All sensitive data encrypted at rest
- SMS codes hashed before storage
- Contract hashes for immutability
- Rate limiting on SMS endpoints
- Input validation on all endpoints
- SQL injection prevention (using ORM)

### NFR-4: Legal Compliance
- All contracts versioned
- All signatures logged with full context
- Audit logs immutable
- Data retention: 5 years minimum
- GDPR compliance (data export/deletion)

### NFR-5: Usability
- Clear error messages in Russian
- Loading indicators for async operations
- Real-time price updates
- Mobile-responsive UI
- Accessibility (WCAG 2.1 AA)

---

## Data Requirements

### DR-1: Price Data
**Source:** Lis-Skins, market.csgo, Steam Market  
**Update Frequency:** On-demand with 1-hour cache  
**Retention:** 30 days of historical prices  
**Volume:** ~10,000 items × 3 sources = 30,000 price records

### DR-2: User Data
**PII:** Phone, passport details, full name  
**Retention:** Active users + 5 years after last deal  
**Encryption:** At rest and in transit  
**Backup:** Daily, 30-day retention

### DR-3: Deal Data
**Retention:** Permanent (legal requirement)  
**Backup:** Daily, permanent retention  
**Audit:** All changes logged

### DR-4: Audit Logs
**Retention:** Permanent  
**Immutability:** Append-only  
**Backup:** Daily, permanent retention

---

## Integration Requirements

### INT-1: Lis-Skins API
**Purpose:** Get instant sell prices  
**Authentication:** API key  
**Rate Limit:** TBD (check docs)  
**Endpoint:** `https://lis-skins.ru/api/v2/prices`  
**Status:** Not integrated (using demo data)

### INT-2: market.csgo API
**Purpose:** Get market/instant prices  
**Authentication:** API key  
**Rate Limit:** TBD (check docs)  
**Endpoint:** `https://market.csgo.com/api/v2/prices`  
**Status:** Not integrated (using demo data)

### INT-3: SMS Provider (sms.ru or smsc.ru)
**Purpose:** Send verification and signature codes  
**Authentication:** API key  
**Rate Limit:** Per account limits  
**Cost:** ~3₽ per SMS  
**Status:** Fake provider for dev

### INT-4: KYC Provider (Sumsub)
**Purpose:** Verify passport documents  
**Authentication:** API key + secret  
**Cost:** Per verification  
**Status:** Fake provider for dev

### INT-5: SBP Provider (Modulbank)
**Purpose:** Send payouts  
**Authentication:** API key  
**Limits:** 100₽ - 600,000₽  
**Cost:** Commission per payout  
**Status:** Fake provider for dev

### INT-6: Steam Bot API
**Purpose:** Create trade offers  
**Authentication:** Internal  
**Endpoint:** `http://localhost:3001/api/trade/*`  
**Status:** Implemented

---

## Configuration Requirements

### Environment Variables Needed

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/cyberlombard

# Steam
STEAM_API_KEY=xxx
STEAM_BOT_API_URL=http://localhost:3001

# Pricing
LIS_SKINS_API_KEY=xxx
MARKET_CSGO_API_KEY=xxx

# SMS
SMS_PROVIDER=fake  # or sms.ru, smsc.ru
SMS_API_KEY=xxx

# KYC
KYC_PROVIDER=fake  # or sumsub
KYC_API_KEY=xxx
KYC_API_SECRET=xxx

# Payouts
SBP_PROVIDER=fake  # or modulbank
SBP_API_KEY=xxx

# Security
SECRET_KEY=xxx
JWT_SECRET=xxx

# Limits
MIN_INSTANT_PRICE=20.0
MIN_TERM_DAYS=7
MAX_TERM_DAYS=30
```

---

## Testing Requirements

### Unit Tests
- [ ] Pricing calculations (all formulas)
- [ ] Term interpolation
- [ ] SMS code generation/verification
- [ ] Contract hash calculation
- [ ] Price aggregation logic

### Integration Tests
- [ ] Full deal creation flow
- [ ] KYC verification flow
- [ ] Contract signing flow
- [ ] Payout flow
- [ ] Price fetching with fallback

### E2E Tests
- [ ] User creates account
- [ ] User verifies phone
- [ ] User submits KYC
- [ ] User creates deal with real prices
- [ ] User signs contract
- [ ] User receives payout
- [ ] User initiates buyback

### Performance Tests
- [ ] Load 100 items with prices
- [ ] 100 concurrent users
- [ ] Database query performance
- [ ] Cache effectiveness

---

## Deployment Requirements

### Infrastructure
- PostgreSQL 14+
- Redis (for caching)
- File storage (for contracts, photos)
- HTTPS/SSL certificate
- Domain name

### Monitoring
- Error tracking (Sentry)
- Log aggregation (ELK/Loki)
- Uptime monitoring
- Performance monitoring (APM)

### Backup
- Database: Daily, 30-day retention
- Files: Daily, permanent retention
- Audit logs: Real-time replication

---

## Documentation Requirements

- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide (Russian)
- [ ] Admin guide
- [ ] Integration guide (for external APIs)
- [ ] Deployment guide
- [ ] Troubleshooting guide

---

## Acceptance Criteria Summary

The system is production-ready when:

1. ✅ All database models created and migrated
2. ✅ All API endpoints implemented and tested
3. ✅ All frontend components created and integrated
4. ✅ Real API integrations working (or clearly marked as demo)
5. ✅ Full deal flow works end-to-end
6. ✅ All critical actions logged with full context
7. ✅ Error handling comprehensive with user-friendly messages
8. ✅ All tests passing (unit, integration, E2E)
9. ✅ Documentation complete
10. ✅ Security review passed
11. ✅ Legal review passed
12. ✅ Performance benchmarks met

---

## Priority Matrix

| Feature | Priority | Complexity | Status |
|---------|----------|------------|--------|
| Multi-source pricing | Critical | Medium | 70% |
| Term slider | Critical | Low | 50% |
| Phone verification | Critical | Medium | 70% |
| KYC verification | Critical | High | 60% |
| Contract signing | Critical | High | 60% |
| SBP payouts | Critical | Medium | 60% |
| Audit logging | Critical | Medium | 50% |
| Real API integrations | Critical | Medium | 0% |
| Frontend components | Critical | Medium | 20% |
| Testing | High | High | 10% |
| Documentation | High | Low | 30% |

---

## Next Steps

1. **Immediate (Today):**
   - Add missing database models (KYCVerification, DealSignature, SBPPayout)
   - Create database migration
   - Test models

2. **Short-term (This Week):**
   - Implement missing API endpoints
   - Create frontend components
   - Integrate components into deal flow

3. **Medium-term (Next Week):**
   - Get real API keys
   - Implement real API integrations
   - Comprehensive testing

4. **Before Production:**
   - Security audit
   - Legal review
   - Performance testing
   - Documentation complete
