# Entitlements System Rollout Plan

## Overview

This document outlines the phased rollout strategy for the org-level entitlements system with entitlement-first, RBAC-second enforcement.

## Feature Flag

### Configuration

**Location**: `app/api/deps/entitlements.py`

```python
# Feature flag for entitlements gating
ENABLE_ENTITLEMENTS_GATING = True  # Default: True for rollout
```

**Environment Variable** (optional):
```bash
ENABLE_ENTITLEMENTS_GATING=false  # Override via environment
```

### States

- `False`: Entitlement checks bypassed, system behaves as before
- `True`: Full entitlement enforcement active

## Rollout Phases

### Phase 0: Pre-Rollout (Preparation)

**Timeline**: Before deployment

**Goals**:
- Code complete and tested
- Database migrations applied
- Documentation reviewed
- Rollback plan ready

**Tasks**:
- [ ] Run all unit tests
- [ ] Run integration tests
- [ ] Test ModuleSelectionModal flows
- [ ] Verify API contract compatibility
- [ ] Review and approve documentation
- [ ] Prepare rollback script
- [ ] Brief support team
- [ ] Create monitoring dashboards

**Success Criteria**:
- All tests passing
- No breaking API changes
- Documentation approved
- Team trained

---

### Phase 1: Deploy with Flag Disabled

**Timeline**: Day 1 (Deploy to Production)

**Flag State**: `ENABLE_ENTITLEMENTS_GATING = False`

**Goals**:
- Deploy code safely without changing behavior
- Verify deployment stability
- Validate API endpoints exist and respond

**Tasks**:
1. Deploy application with feature flag disabled
2. Run smoke tests on production
3. Verify existing functionality unaffected
4. Check logs for any errors
5. Monitor performance metrics

**Validation**:
```bash
# Test entitlements API exists
curl -H "Authorization: Bearer $TOKEN" \
  https://api.prod.example.com/api/v1/orgs/1/entitlements

# Expected: 200 OK with entitlements data

# Test admin API
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://api.prod.example.com/api/v1/admin/modules

# Expected: 200 OK with modules list
```

**Monitoring**:
- Application error rate
- API response times
- Database query performance
- No spike in 403 errors

**Rollback Trigger**:
- Deployment failures
- Increased error rate
- API unavailability

**Duration**: 24-48 hours

---

### Phase 2: Enable in Development/Staging

**Timeline**: Day 3 (After Phase 1 stability confirmed)

**Flag State**: `ENABLE_ENTITLEMENTS_GATING = True` (dev/staging only)

**Goals**:
- Test full enforcement in safe environment
- Validate ModuleSelectionModal flows
- Test all exception cases
- Gather metrics on enforcement behavior

**Tasks**:
1. Enable flag in dev/staging environments
2. Create test organizations with various module configurations
3. Test module selection flows
4. Test super admin bypass
5. Test always-on modules (Email)
6. Test RBAC-only modules (Settings)
7. Verify error responses format
8. Test cache invalidation

**Test Scenarios**:

**Scenario 1: CRM Only**
```
1. Create test org
2. Enable only CRM module
3. Verify CRM menu items visible
4. Verify other modules disabled/locked
5. Test API access (expect 403 for non-CRM)
```

**Scenario 2: All Modules Disabled**
```
1. Create test org with no modules
2. Verify Email still visible and functional
3. Verify Settings visible to admin
4. Verify all other modules disabled
5. Test API access (expect 403 for all except email/settings)
```

**Scenario 3: Trial Module**
```
1. Create test org with Manufacturing in trial
2. Set trial_expires_at to future date
3. Verify Manufacturing accessible with "Trial" badge
4. Set trial_expires_at to past date
5. Verify Manufacturing disabled with expiry message
```

**Scenario 4: Super Admin**
```
1. Log in as super admin
2. Select org with all modules disabled
3. Verify all menu items enabled
4. Test API access (expect 200 for all)
5. Verify bypass logged in audit
```

**Scenario 5: Module Selection**
```
1. Log in as super admin
2. Open ModuleSelectionModal
3. Select CRM + ERP bundles
4. Save changes
5. Verify menu updates (within cache TTL)
6. Test API access matches selection
```

**Monitoring**:
- Entitlement_denied vs permission_denied ratio
- Super admin bypass frequency
- Cache hit rate
- API endpoint coverage (which routes have entitlement guards)

**Success Criteria**:
- All test scenarios pass
- No unexpected 403 errors on always-on modules
- Super admin bypass working
- ModuleSelectionModal updates reflected correctly
- Error responses match specification

**Rollback Trigger**:
- Critical bugs discovered
- Unexpected behavior in enforcement
- Performance degradation

**Duration**: 3-5 days (allow time for thorough testing)

---

### Phase 3: Gradual Production Rollout

**Timeline**: Day 8+ (After Phase 2 success)

**Flag State**: `ENABLE_ENTITLEMENTS_GATING = True` (production)

**Goals**:
- Enable enforcement in production with minimal risk
- Monitor real-world behavior
- Gather production metrics
- Validate with real users

**Rollout Strategy**: Canary deployment

#### Step 3a: Enable for 5% of Organizations

**Tasks**:
1. Enable flag for small subset of organizations
2. Monitor for 24 hours
3. Collect user feedback
4. Review metrics

**Selection Criteria** for initial orgs:
- Internal testing organizations
- Early adopter customers (pre-notified)
- Organizations with simple module configurations
- High engagement organizations (will report issues quickly)

**Monitoring**:
- User-reported issues
- 403 error rates (entitlement vs permission)
- API latency
- Database load
- Cache performance

#### Step 3b: Enable for 25% of Organizations

**Timeline**: +2 days after 3a success

**Tasks**:
1. Expand to 25% of organizations
2. Monitor for 48 hours
3. Review accumulated metrics
4. Adjust if needed

#### Step 3c: Enable for 100% of Organizations

**Timeline**: +3 days after 3b success

**Tasks**:
1. Enable for all remaining organizations
2. Monitor for 72 hours
3. Issue all-clear or rollback

**Success Criteria**:
- < 0.1% unexpected 403 errors
- No performance degradation
- User satisfaction maintained
- Support ticket volume normal

**Rollback Trigger**:
- > 1% unexpected 403 errors
- API response time > 2x baseline
- Critical bugs affecting core functionality
- High volume of support tickets

---

### Phase 4: Post-Rollout Optimization

**Timeline**: Week 2-3

**Goals**:
- Optimize based on real-world data
- Fine-tune cache settings
- Document learnings
- Plan future enhancements

**Tasks**:
1. Analyze enforcement patterns
2. Optimize cache TTL based on usage
3. Review and update documentation
4. Conduct retrospective
5. Plan deprecation of legacy enabled_modules

---

## Rollback Procedures

### Quick Rollback (Emergency)

**Trigger**: Critical bug, widespread 403 errors, or system instability

**Steps**:
1. Set `ENABLE_ENTITLEMENTS_GATING = False` in configuration
2. Deploy configuration change (no code change needed)
3. Restart application servers
4. Verify functionality restored
5. Investigate root cause

**Time to rollback**: < 15 minutes

### Partial Rollback

**Trigger**: Issues with specific module or subset of organizations

**Option 1**: Disable for specific organizations
```python
# Add to enforcement logic
if org_id in DISABLED_ORGS:
    return True, 'enabled', 'Entitlements disabled for this org'
```

**Option 2**: Disable for specific modules
```python
# Add to enforcement logic
if module_key in DISABLED_MODULES:
    return True, 'enabled', 'Entitlements disabled for this module'
```

### Full Rollback (Code revert)

**Trigger**: Fundamental architectural issues

**Steps**:
1. Revert deployment to previous version
2. Remove entitlement guards from endpoints
3. Notify affected users
4. Plan rework

**Time to rollback**: 1-2 hours

---

## Monitoring & Alerts

### Key Metrics

**Application Metrics**:
- `entitlement_checks_total`: Total entitlement checks performed
- `entitlement_denied_total`: Number of entitlement denials
- `permission_denied_total`: Number of permission denials
- `super_admin_bypass_total`: Number of super admin bypasses
- `entitlement_cache_hit_rate`: Cache efficiency

**API Metrics**:
- Response time for `/orgs/{orgId}/entitlements` endpoint
- Response time for `/admin/orgs/{orgId}/entitlements` endpoint
- Error rate (5xx)
- 403 error rate

**Business Metrics**:
- Module selection frequency
- Most/least used modules
- Trial conversion rate
- Support ticket volume

### Alerts

**Critical** (page on-call):
- Entitlement API error rate > 5%
- 403 error spike (> 10x baseline)
- Cache service unavailable

**Warning** (notify team):
- Entitlement API response time > 500ms (p99)
- Cache hit rate < 80%
- Unusual spike in super admin bypasses

### Dashboards

Create dashboards for:
1. **Enforcement Overview**: Entitlement checks, denials, bypasses
2. **API Health**: Response times, error rates, cache performance
3. **Module Usage**: Popular modules, trial conversions
4. **User Impact**: Organizations affected, support tickets

---

## Communication Plan

### Pre-Rollout

**Audience**: All users

**Message**:
"We're rolling out improved module management that will give you more control over your feature access. No action required on your part."

**Channels**:
- In-app notification
- Email to admin users
- Documentation update

### During Rollout

**Audience**: Early adopter organizations (Phase 3a)

**Message**:
"Your organization has been selected for early access to our new module management system. If you experience any issues, please contact support."

**Channels**:
- Direct email to org admins
- In-app notification
- Support team briefed

### Post-Rollout

**Audience**: All users

**Message**:
"Module management system is now live for all organizations. Visit Settings > Modules to manage your features."

**Channels**:
- In-app announcement
- Email to admin users
- Blog post / changelog

### Rollback Communication

**Audience**: Affected users (if partial) or all users (if full)

**Message**:
"We temporarily disabled a new feature due to technical issues. Your service is unaffected. We'll notify you when it's re-enabled."

**Channels**:
- In-app notification
- Email (if significant impact)
- Status page

---

## Success Metrics

### Phase 1
- ✅ Zero increase in error rate after deployment
- ✅ All smoke tests passing
- ✅ No performance regression

### Phase 2
- ✅ All test scenarios passing in staging
- ✅ ModuleSelectionModal working end-to-end
- ✅ Error responses match specification
- ✅ No false denials (email, settings, super admin)

### Phase 3
- ✅ < 0.1% unexpected 403 errors in production
- ✅ API response time within SLA
- ✅ < 5 support tickets related to entitlements per day
- ✅ User feedback mostly positive

### Phase 4
- ✅ Legacy enabled_modules deprecated
- ✅ Documentation complete
- ✅ Team trained on new system
- ✅ Monitoring dashboards in use

---

## Risk Mitigation

### Risk: False Denials

**Impact**: Users blocked from legitimate access

**Mitigation**:
- Extensive testing in staging
- Always-on modules (email) exempt
- Super admin bypass for emergencies
- Quick rollback procedure

### Risk: Performance Degradation

**Impact**: Slow API responses

**Mitigation**:
- Entitlements cached (TTL: 5 minutes)
- Database indexes on entitlement tables
- Load testing before production rollout
- Monitor response times in real-time

### Risk: Cache Inconsistency

**Impact**: Stale entitlements shown in UI

**Mitigation**:
- Cache invalidation on updates
- Manual refresh option
- Short TTL (5 minutes max)
- Monitor cache hit rate

### Risk: Migration Issues

**Impact**: Data inconsistency between enabled_modules and entitlements

**Mitigation**:
- Dual-write to both systems during transition
- Automated sync on entitlement updates
- Verification scripts to check consistency
- Plan gradual deprecation

---

## Timeline Summary

| Phase | Duration | Flag State | Risk Level |
|-------|----------|------------|------------|
| Phase 0 | 3-5 days | N/A | Low |
| Phase 1 | 1-2 days | False (Prod) | Low |
| Phase 2 | 3-5 days | True (Dev/Staging) | Medium |
| Phase 3a | 2-3 days | True (5% Prod) | Medium |
| Phase 3b | 2-3 days | True (25% Prod) | Medium-Low |
| Phase 3c | 3-5 days | True (100% Prod) | Low |
| Phase 4 | Ongoing | True (All) | Low |

**Total Duration**: 14-23 days from deployment to full rollout

---

## Sign-off

Before proceeding to each phase, obtain sign-off from:

- [ ] Engineering Lead: Code quality, test coverage
- [ ] Product Manager: Feature completeness, user impact
- [ ] DevOps Lead: Infrastructure readiness, monitoring
- [ ] Support Lead: Team training, escalation procedures
- [ ] Security Lead: Audit logging, bypass controls

---

## Lessons Learned (Post-Rollout)

_To be filled after completion_

### What Went Well

### What Could Be Improved

### Action Items for Next Rollout
