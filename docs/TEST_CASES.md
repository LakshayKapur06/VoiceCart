# VoiceCart test case records

Current execution: 2026-11-03T04:03:26.345007+00:00. Evidence: [20261103_S21_final_cases/TEST_EXECUTION.json](../docs/evidence/20261103_S21_final_cases/TEST_EXECUTION.json). Source design dates are historical where known; current mappings were reviewed on 2026-11-03.

Generated from actual source tests and a new recorded execution. Source methods contain exact fixture arrangements, inputs and expected assertions. A case is Pass only when that method actually completed successfully; skipped/unexecuted cases are Not Run. Test data is fabricated only in explicitly guarded test files/databases. This record does not mark real-device, Docker or human acceptance as passed.

Design technique mapping and concrete decision/partition/loop scenarios are in [TESTING_GUIDE.md](TESTING_GUIDE.md); white-box graphs and independent-path designs are in [CFG_ANALYSIS.md](CFG_ANALYSIS.md).


## VC-E14F4459 — create variant and deactivate preserve source contract

**Test Case ID:** VC-E14F4459

**Test Case Name:** AdminHTTPTests.test_create_variant_and_deactivate_preserve_source_contract

**System/Sub-system:** tests.test_admin

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:12.560594+00:00

**Description:** Executable contract [tests.test_admin.AdminHTTPTests.test_create_variant_and_deactivate_preserve_source_contract](../tests/test_admin.py#L112), lines 112–148.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `headers = {'Authorization': 'Bearer ' + TOKEN}; document = self.request('export', headers=headers)[1]['snapshot']; document['previous_revision'] = document['revision']`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_admin.AdminHTTPTests.test_create_variant_and_deactivate_preserve_source_contract` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.request('import', document, headers=headers)[0], 200); self.assertEqual(self.database.inspect()['product_count'], 4); self.assertEqual(self.request('import', updated, headers=headers)[0], 200); self.assertEqual(self.request('catalogue', {'category': 'test-only'}, headers=headers)[1]['total'], 0)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.6126 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-233F38A2 — duplicate import rolls back and bearer enforced

**Test Case ID:** VC-233F38A2

**Test Case Name:** AdminHTTPTests.test_duplicate_import_rolls_back_and_bearer_enforced

**System/Sub-system:** tests.test_admin

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:13.173376+00:00

**Description:** Executable contract [tests.test_admin.AdminHTTPTests.test_duplicate_import_rolls_back_and_bearer_enforced](../tests/test_admin.py#L95), lines 95–110.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `document = self.request('export', headers={'Authorization': 'Bearer ' + TOKEN})[1]['snapshot']; document['previous_revision'] = document['revision']; document['revision'] = 'invalid-test'`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_admin.AdminHTTPTests.test_duplicate_import_rolls_back_and_bearer_enforced` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.request('export', headers={'Authorization': 'Bearer bad'})[0], 403); self.assertEqual(status, 400); self.assertTrue(result['issues']); self.assertEqual(self.database.inspect()['revision'], 'fixture-1')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5601 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-6E37DB5C — event privacy environment and retention

**Test Case ID:** VC-6E37DB5C

**Test Case Name:** AdminHTTPTests.test_event_privacy_environment_and_retention

**System/Sub-system:** tests.test_admin

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:13.733574+00:00

**Description:** Executable contract [tests.test_admin.AdminHTTPTests.test_event_privacy_environment_and_retention](../tests/test_admin.py#L150), lines 150–162.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `events = EventStore(self.database, 'test'); summary = events.summary()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_admin.AdminHTTPTests.test_event_privacy_environment_and_retention` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(summary['events'][0]['count'], 1); self.assertNotIn('query', str(summary['events'])); self.assertEqual(EventStore(self.database, 'merchant').summary()['events'], []); self.assertEqual(events.summary()['events'], [])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5542 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-CD257E98 — roles login export atomic edit conflict and metrics

**Test Case ID:** VC-CD257E98

**Test Case Name:** AdminHTTPTests.test_roles_login_export_atomic_edit_conflict_and_metrics

**System/Sub-system:** tests.test_admin

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:14.287971+00:00

**Description:** Executable contract [tests.test_admin.AdminHTTPTests.test_roles_login_export_atomic_edit_conflict_and_metrics](../tests/test_admin.py#L73), lines 73–93.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `document = self.request('export')[1]['snapshot']; document['previous_revision'] = document['revision']; document['revision'] = 'admin-test-2'`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_admin.AdminHTTPTests.test_roles_login_export_atomic_edit_conflict_and_metrics` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.request('export')[0], 403); self.assertEqual(self.request('login', {'token': 'bad'})[0], 403); self.assertEqual(self.request('login', {'token': TOKEN})[0], 200); self.assertEqual(self.request('import', document)[0], 200); self.assertEqual(self.request('import', document)[0], 400); self.assertEqual(self.database.inspect()['revision'], 'admin-test-2'); self.assertEqual(analytics['environment'], 'test'); self.assertEqual(analytics['coverage']['variants'], 3); self.assertIn('Not collected', analytics['popular_queries']); self.assertEqual(self.request('health')[1]['database'], 'ok'); self.assertGreaterEqual(len(self.request('imports')[1]['imports']), 1); self.assertEqual(self.request('export')[0], 403)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5851 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-3AA11BCB — cancel during interpretation fences late error response

**Test Case ID:** VC-3AA11BCB

**Test Case Name:** ApplicationSystemTests.test_cancel_during_interpretation_fences_late_error_response

**System/Sub-system:** tests.test_application

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:14.885760+00:00

**Description:** Executable contract [tests.test_application.ApplicationSystemTests.test_cancel_during_interpretation_fences_late_error_response](../tests/test_application.py#L144), lines 144–156.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `app = self.app; app.interpreter = CancelledInterpreter(); response = app.text(self.session, 'find backpack')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_application.ApplicationSystemTests.test_cancel_during_interpretation_fences_late_error_response` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(response.code, 'cancelled'); self.assertEqual(response.text, ''); self.assertEqual(app.cart.items(self.session), {})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0541 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-4FB3B1E1 — duplicate final is claimed once in persistent session

**Test Case ID:** VC-4FB3B1E1

**Test Case Name:** ApplicationSystemTests.test_duplicate_final_is_claimed_once_in_persistent_session

**System/Sub-system:** tests.test_application

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:14.939879+00:00

**Description:** Executable contract [tests.test_application.ApplicationSystemTests.test_duplicate_final_is_claimed_once_in_persistent_session](../tests/test_application.py#L91), lines 91–100.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `turn = self.app.begin(self.session); final = Transcript(TranscriptKind.FINAL, 'cheapest black backpack under 2000 and add', turn); first = self.app.final(self.session, final)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_application.ApplicationSystemTests.test_duplicate_final_is_claimed_once_in_persistent_session` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(first.operation_id, repeated.operation_id); self.assertEqual(self.interpreter.calls, 1); self.assertEqual(self.app.cart.items(self.session), {'v-cheap': 1})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0489 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-1E72E7A7 — partial blank cancelled and malformed requests do not add

**Test Case ID:** VC-1E72E7A7

**Test Case Name:** ApplicationSystemTests.test_partial_blank_cancelled_and_malformed_requests_do_not_add

**System/Sub-system:** tests.test_application

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:14.988836+00:00

**Description:** Executable contract [tests.test_application.ApplicationSystemTests.test_partial_blank_cancelled_and_malformed_requests_do_not_add](../tests/test_application.py#L102), lines 102–116.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `turn = self.app.begin(self.session); stale = self.app.final(self.session, Transcript(TranscriptKind.FINAL, 'add second', turn)); result = self.app.text(self.session, 'drop constraints')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_application.ApplicationSystemTests.test_partial_blank_cancelled_and_malformed_requests_do_not_add` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(stale.code, 'cancelled'); self.assertEqual(result.code, 'clarify'); self.assertEqual(self.app.cart.items(self.session), {})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0342 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-33B9B54A — real cli search add and repeated invocation are idempotent

**Test Case ID:** VC-33B9B54A

**Test Case Name:** ApplicationSystemTests.test_real_cli_search_add_and_repeated_invocation_are_idempotent

**System/Sub-system:** tests.test_application

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.023009+00:00

**Description:** Executable contract [tests.test_application.ApplicationSystemTests.test_real_cli_search_add_and_repeated_invocation_are_idempotent](../tests/test_application.py#L171), lines 171–205.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `environment = dict(os.environ, VOICECART_DATABASE_URL=os.environ['VOICECART_TEST_DSN']); result = invoke('search', '--category', 'backpack', '--colour', 'black'); session = result['session_id']`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_application.ApplicationSystemTests.test_real_cli_search_add_and_repeated_invocation_are_idempotent` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(first, replay); self.assertEqual(self.app.cart.items(session), {'v-cheap': 1}); self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.4282 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-76C0E6BA — search complete list select add and repeat without mutation

**Test Case ID:** VC-76C0E6BA

**Test Case Name:** ApplicationSystemTests.test_search_complete_list_select_add_and_repeat_without_mutation

**System/Sub-system:** tests.test_application

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.451232+00:00

**Description:** Executable contract [tests.test_application.ApplicationSystemTests.test_search_complete_list_select_add_and_repeat_without_mutation](../tests/test_application.py#L73), lines 73–89.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = self.app.text(self.session, 'find backpack'); chosen = result.listing.offers[1]; added = self.app.text(self.session, 'add second')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_application.ApplicationSystemTests.test_search_complete_list_select_add_and_repeat_without_mutation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.code, 'results'); self.assertIn('rupees', result.text); self.assertTrue(self.app.sessions.mark_presented(self.session, result.listing.list_id, result.turn_id)); self.assertEqual(added.code, 'added'); self.assertEqual(added.receipt.variant_id, chosen.variant_id); self.assertEqual(self.app.text(self.session, 'repeat'), added); self.assertEqual(self.interpreter.calls, calls); self.assertEqual(self.app.cart.items(self.session), {chosen.variant_id: 1})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0637 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C5D8DC32 — template error after commit preserves authoritative confirmation

**Test Case ID:** VC-C5D8DC32

**Test Case Name:** ApplicationSystemTests.test_template_error_after_commit_preserves_authoritative_confirmation

**System/Sub-system:** tests.test_application

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.514906+00:00

**Description:** Executable contract [tests.test_application.ApplicationSystemTests.test_template_error_after_commit_preserves_authoritative_confirmation](../tests/test_application.py#L158), lines 158–169.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.app.confirmed_receipt = broken; result = self.app.text(self.session, 'cheapest black backpack under 2000 and add')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_application.ApplicationSystemTests.test_template_error_after_commit_preserves_authoritative_confirmation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.code, 'added'); self.assertIsNotNone(result.receipt); self.assertIn('committed', result.text); self.assertEqual(self.app.cart.items(self.session), {'v-cheap': 1})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0393 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-F24722FF — unacknowledged list and other session cannot redirect add

**Test Case ID:** VC-F24722FF

**Test Case Name:** ApplicationSystemTests.test_unacknowledged_list_and_other_session_cannot_redirect_add

**System/Sub-system:** tests.test_application

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.554243+00:00

**Description:** Executable contract [tests.test_application.ApplicationSystemTests.test_unacknowledged_list_and_other_session_cannot_redirect_add](../tests/test_application.py#L118), lines 118–128.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = self.app.text(self.session, 'find backpack'); rejected = self.app.text(self.session, 'add second'); other = self.app.sessions.create()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_application.ApplicationSystemTests.test_unacknowledged_list_and_other_session_cannot_redirect_add` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertNotEqual(rejected.code, 'added'); self.assertFalse(self.app.sessions.mark_presented(other, result.listing.list_id, result.turn_id)); self.assertEqual(self.app.cart.items(self.session), {})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0551 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-832FDC14 — unpopulated stale and no match are different

**Test Case ID:** VC-832FDC14

**Test Case Name:** ApplicationSystemTests.test_unpopulated_stale_and_no_match_are_different

**System/Sub-system:** tests.test_application

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.609364+00:00

**Description:** Executable contract [tests.test_application.ApplicationSystemTests.test_unpopulated_stale_and_no_match_are_different](../tests/test_application.py#L130), lines 130–142.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `none = self.app.text(self.session, 'backpack under 1'); stale = self.app.text(self.session, 'find backpack'); empty = self.app.text(self.session, 'find backpack')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_application.ApplicationSystemTests.test_unpopulated_stale_and_no_match_are_different` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(none.code, 'no_match'); self.assertEqual(stale.code, 'catalogue_stale'); self.assertEqual(empty.code, 'catalogue_not_populated'); self.assertFalse(self.app.cart.items(self.session))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0561 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-BF51BFC0 — full denominator disjoint outcomes and percentiles

**Test Case ID:** VC-BF51BFC0

**Test Case Name:** AudibleLatencyTelemetryTests.test_full_denominator_disjoint_outcomes_and_percentiles

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.665513+00:00

**Description:** Executable contract [tests.test_audio.AudibleLatencyTelemetryTests.test_full_denominator_disjoint_outcomes_and_percentiles](../tests/test_audio.py#L637), lines 637–655.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `recorder = LatencyBenchmarkRecorder(); summary = recorder.summarize()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudibleLatencyTelemetryTests.test_full_denominator_disjoint_outcomes_and_percentiles` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(summary.total_turns, 7); self.assertEqual(summary.successful_turns, 4); self.assertEqual(summary.failed_turns, 1); self.assertEqual(summary.timeout_turns, 1); self.assertEqual(summary.cancelled_turns, 1); self.assertEqual(summary.cold_turns, 1); self.assertAlmostEqual(summary.target_1500ms_pass_rate, 2 / 7); self.assertAlmostEqual(summary.p50_audible_onset_s, 1.35); self.assertEqual(summary.p95_audible_onset_s, 2.0)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-25FFE269 — intervals and zero clock are valid

**Test Case ID:** VC-25FFE269

**Test Case Name:** AudibleLatencyTelemetryTests.test_intervals_and_zero_clock_are_valid

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.665688+00:00

**Description:** Executable contract [tests.test_audio.AudibleLatencyTelemetryTests.test_intervals_and_zero_clock_are_valid](../tests/test_audio.py#L594), lines 594–609.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `trace = LatencyTrace('t', t_speech_end=0, t_endpoint_detected=0.1, t_asr_start=0.1, t_asr_end=0.4, t_tts_start=0.5, t_first_pcm_chunk=0.8, t_audible_onset=1.0)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudibleLatencyTelemetryTests.test_intervals_and_zero_clock_are_valid` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertAlmostEqual(trace.endpoint_delay_s, 0.1); self.assertAlmostEqual(trace.asr_latency_s, 0.3); self.assertAlmostEqual(trace.tts_to_first_audio_s, 0.3); self.assertEqual(trace.audible_onset_latency_s, 1); self.assertTrue(trace.meets_1500ms_target)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-F47EDA43 — missing reversed nonfinite and bool times never pass

**Test Case ID:** VC-F47EDA43

**Test Case Name:** AudibleLatencyTelemetryTests.test_missing_reversed_nonfinite_and_bool_times_never_pass

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.665723+00:00

**Description:** Executable contract [tests.test_audio.AudibleLatencyTelemetryTests.test_missing_reversed_nonfinite_and_bool_times_never_pass](../tests/test_audio.py#L611), lines 611–635.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `invalid = (LatencyTrace('missing'), LatencyTrace('end', t_audible_onset=11), LatencyTrace('reverse', t_speech_end=10, t_audible_onset=9), LatencyTrace('nan', t_speech_end=float('nan'), t_audible_onset=11), LatencyTrace('inf', t_speech_end=10, t_audible_onset=float('inf')), LatencyTrace('bool', t_speech_end=False, t_audible_onset=1), LatencyTrace('stage', t_speech_end=10, t_asr_start=12, t_asr_end=11, t_audible_onset=13)); recorder = LatencyBenchmarkRecorder(); summary = recorder.summarize()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudibleLatencyTelemetryTests.test_missing_reversed_nonfinite_and_bool_times_never_pass` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(summary.successful_turns, 0); self.assertEqual(summary.failed_turns, len(invalid)); self.assertIsNone(summary.p50_audible_onset_s); self.assertEqual(summary.target_1500ms_pass_rate, 0); self.assertFalse(trace.meets_1500ms_target, trace.turn_id)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-EF7C96A2 — recorder freezes snapshots and rejects duplicate ids

**Test Case ID:** VC-EF7C96A2

**Test Case Name:** AudibleLatencyTelemetryTests.test_recorder_freezes_snapshots_and_rejects_duplicate_ids

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.665833+00:00

**Description:** Executable contract [tests.test_audio.AudibleLatencyTelemetryTests.test_recorder_freezes_snapshots_and_rejects_duplicate_ids](../tests/test_audio.py#L657), lines 657–666.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `trace = LatencyTrace('t', t_speech_end=10, t_audible_onset=11); recorder = LatencyBenchmarkRecorder(); trace.failed = True`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudibleLatencyTelemetryTests.test_recorder_freezes_snapshots_and_rejects_duplicate_ids` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(recorder.summarize().successful_turns, 1); self.assertIsNone(LatencyBenchmarkRecorder().summarize().max_audible_onset_s); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-DDE65571 — asr wrong turn and unknown fixture cannot reach template

**Test Case ID:** VC-DDE65571

**Test Case Name:** AudioPipelineSliceTests.test_asr_wrong_turn_and_unknown_fixture_cannot_reach_template

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.665909+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_asr_wrong_turn_and_unknown_fixture_cannot_reach_template](../tests/test_audio.py#L579), lines 579–590.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_asr_wrong_turn_and_unknown_fixture_cannot_reach_template` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.trace.failure_reason, 'asr_turn_mismatch'); self.assertEqual(self.tts.spoken_texts, []); self.assertEqual(self.trace.failure_reason, 'asr_error'); self.assertEqual(self.tts.spoken_texts, [])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-6BFAB213 — cached asset is injected and failure does not claim original success

**Test Case ID:** VC-6BFAB213

**Test Case Name:** AudioPipelineSliceTests.test_cached_asset_is_injected_and_failure_does_not_claim_original_success

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666020+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_cached_asset_is_injected_and_failure_does_not_claim_original_success](../tests/test_audio.py#L419), lines 419–434.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `fallback = CachedSpeechPrompt('Speech unavailable. Try again.', AudioChunk(b'\x00\x00' * 160, 16000)); _, response, chunks = self.run_slice(tts=MockSpeechSynthesizer(should_fail=True), fallback=fallback)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_cached_asset_is_injected_and_failure_does_not_claim_original_success` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(response, fallback.text); self.assertEqual(chunks, [fallback.chunk]); self.assertTrue(self.trace.failed); self.assertFalse(self.trace.meets_1500ms_target); self.assertEqual(self.controller.repeat(), fallback.text); self.assertTrue(any((fallback.text in m.text for m in self.controller.status_messages)))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-0358555B — deadline and missing output remain in denominator

**Test Case ID:** VC-0358555B

**Test Case Name:** AudioPipelineSliceTests.test_deadline_and_missing_output_remain_in_denominator

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666098+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_deadline_and_missing_output_remain_in_denominator](../tests/test_audio.py#L521), lines 521–531.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `recorder = LatencyBenchmarkRecorder()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_deadline_and_missing_output_remain_in_denominator` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(self.trace.timed_out); self.assertEqual(recorder.summarize().timeout_turns, 1); self.assertEqual(recorder.summarize().target_1500ms_pass_rate, 0)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-48AAB0B8 — late old drain cannot finish new playback

**Test Case ID:** VC-48AAB0B8

**Test Case Name:** AudioPipelineSliceTests.test_late_old_drain_cannot_finish_new_playback

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666162+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_late_old_drain_cannot_finish_new_playback](../tests/test_audio.py#L463), lines 463–490.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `entered, release = (threading.Event(), threading.Event()); self.output.on_drain = wait_for_cancel; worker = threading.Thread(target=self.run_slice)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_late_old_drain_cannot_finish_new_playback` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(worker.is_alive()); self.assertTrue(self.output.is_playing()); self.assertEqual(self.controller.state, TurnState.SPEAKING); self.assertEqual(self.controller.current_turn_id, 'new'); self.assertTrue(self.trace.cancelled); self.assertTrue(self.controller.finish_speaking('new')[0]); self.assertTrue(entered.wait(3))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-BEDFA613 — no device onset is not a successful benchmark

**Test Case ID:** VC-BEDFA613

**Test Case Name:** AudioPipelineSliceTests.test_no_device_onset_is_not_a_successful_benchmark

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666362+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_no_device_onset_is_not_a_successful_benchmark](../tests/test_audio.py#L447), lines 447–455.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.output.drain = lambda turn_id: None; self.output.on_play = self.output.stop_playback; recorder = LatencyBenchmarkRecorder()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_no_device_onset_is_not_a_successful_benchmark` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(self.trace.is_successful); self.assertEqual(recorder.summarize().failed_turns, 1)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C3A83B50 — output begin and drain failures recover

**Test Case ID:** VC-C3A83B50

**Test Case Name:** AudioPipelineSliceTests.test_output_begin_and_drain_failures_recover

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666447+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_output_begin_and_drain_failures_recover](../tests/test_audio.py#L508), lines 508–519.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_output_begin_and_drain_failures_recover` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(response, AudioPipelineSlice.ERROR_RESPONSE); self.assertEqual(chunks, []); self.assertEqual(self.trace.failure_reason, 'output_error'); self.assertEqual(self.controller.state, TurnState.IDLE)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-1EFFDFD0 — output failure and dead assistive channel mark session unusable

**Test Case ID:** VC-1EFFDFD0

**Test Case Name:** AudioPipelineSliceTests.test_output_failure_and_dead_assistive_channel_mark_session_unusable

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666536+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_output_failure_and_dead_assistive_channel_mark_session_unusable](../tests/test_audio.py#L436), lines 436–445.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.output.play_chunk = broken_play`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_output_failure_and_dead_assistive_channel_mark_session_unusable` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.trace.failure_reason, 'output_error'); self.assertFalse(self.controller.is_session_usable()); self.assertEqual(self.controller.state, TurnState.FAILED)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-A108AE47 — partial and invalid final never render

**Test Case ID:** VC-A108AE47

**Test Case Name:** AudioPipelineSliceTests.test_partial_and_invalid_final_never_render

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666580+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_partial_and_invalid_final_never_render](../tests/test_audio.py#L379), lines 379–399.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_partial_and_invalid_final_never_render` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.output.played_chunks, []); self.assertEqual(self.controller.state, TurnState.PROCESSING); self.assertTrue(self.trace.failed); self.assertEqual(self.controller.state, TurnState.IDLE)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-CE6D89A6 — pause inside enqueue cancels without finishing

**Test Case ID:** VC-CE6D89A6

**Test Case Name:** AudioPipelineSliceTests.test_pause_inside_enqueue_cancels_without_finishing

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666658+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_pause_inside_enqueue_cancels_without_finishing](../tests/test_audio.py#L310), lines 310–316.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.output.on_play = self.controller.pause`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_pause_inside_enqueue_cancels_without_finishing` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(len(self.output.played_chunks), 1); self.assertEqual(self.controller.state, TurnState.PAUSED); self.assertTrue(self.trace.cancelled); self.assertIsNone(self.controller.repeat())
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-984CD7FA — pipeline ends capture before asr and rejects consumed turn

**Test Case ID:** VC-984CD7FA

**Test Case Name:** AudioPipelineSliceTests.test_pipeline_ends_capture_before_asr_and_rejects_consumed_turn

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666702+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_pipeline_ends_capture_before_asr_and_rejects_consumed_turn](../tests/test_audio.py#L492), lines 492–506.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `capture = MockAudioInput(); controller = HalfDuplexTurnController(audio_input=capture); asr = CaptureCheckingASR()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_pipeline_ends_capture_before_asr_and_rejects_consumed_turn` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(asr.calls, 1); self.assertFalse(capture.capturing)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-376DB163 — scripted pcm runs through asr template tts and output

**Test Case ID:** VC-376DB163

**Test Case Name:** AudioPipelineSliceTests.test_scripted_pcm_runs_through_asr_template_tts_and_output

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666761+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_scripted_pcm_runs_through_asr_template_tts_and_output](../tests/test_audio.py#L266), lines 266–292.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `expected_slots = (('under', '1500', 'rupees'), ('at most', '2000', 'rupees'), ('SKU-BLK-101',), ("don't add",)); responses = []`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_scripted_pcm_runs_through_asr_template_tts_and_output` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(len(set(responses)), 4); self.assertEqual(asr.calls, 1); self.assertEqual(tts.spoken_texts, [response]); self.assertEqual(chunks, output.played_chunks); self.assertIn(slot, transcript.text); self.assertIn(slot, response)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-0FA455C7 — status sink failure then output failure disables session

**Test Case ID:** VC-0FA455C7

**Test Case Name:** AudioPipelineSliceTests.test_status_sink_failure_then_output_failure_disables_session

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666887+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_status_sink_failure_then_output_failure_disables_session](../tests/test_audio.py#L564), lines 564–577.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.controller = HalfDuplexTurnController(status_sink=broken_sink); self.output.play_chunk = broken_play`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_status_sink_failure_then_output_failure_disables_session` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(self.controller.is_session_usable()); self.assertEqual(self.controller.state, TurnState.FAILED)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-87347A6B — stop during asr does not render template

**Test Case ID:** VC-87347A6B

**Test Case Name:** AudioPipelineSliceTests.test_stop_during_asr_does_not_render_template

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666932+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_stop_during_asr_does_not_render_template](../tests/test_audio.py#L344), lines 344–357.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `controller = self.controller`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_stop_during_asr_does_not_render_template` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(self.trace.cancelled); self.assertEqual(self.output.played_chunks, [])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-4082B9E4 — stop during drain allows concurrent control and fences completion

**Test Case ID:** VC-4082B9E4

**Test Case Name:** AudioPipelineSliceTests.test_stop_during_drain_allows_concurrent_control_and_fences_completion

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.666976+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_stop_during_drain_allows_concurrent_control_and_fences_completion](../tests/test_audio.py#L318), lines 318–342.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `entered, release = (threading.Event(), threading.Event()); self.output.on_drain = drain; results = []`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_stop_during_drain_allows_concurrent_control_and_fences_completion` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(worker.is_alive()); self.assertEqual(len(results), 1); self.assertEqual(self.controller.current_turn_id, 'new'); self.assertEqual(self.controller.state, TurnState.LISTENING); self.assertTrue(self.trace.cancelled); self.assertIsNone(self.trace.t_audible_onset); self.assertTrue(entered.wait(3))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-3BADC18C — stop during synthesis fences remaining chunks

**Test Case ID:** VC-3BADC18C

**Test Case Name:** AudioPipelineSliceTests.test_stop_during_synthesis_fences_remaining_chunks

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667086+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_stop_during_synthesis_fences_remaining_chunks](../tests/test_audio.py#L294), lines 294–308.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `controller = self.controller; _, response, chunks = self.run_slice(tts=InterruptedTTS())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_stop_during_synthesis_fences_remaining_chunks` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(response, ''); self.assertEqual(len(chunks), 1); self.assertEqual(len(self.output.played_chunks), 1); self.assertTrue(self.trace.cancelled); self.assertEqual(self.controller.state, TurnState.STOPPED)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-2A0A95A1 — stop followed by asr error is cancellation

**Test Case ID:** VC-2A0A95A1

**Test Case Name:** AudioPipelineSliceTests.test_stop_followed_by_asr_error_is_cancellation

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667139+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_stop_followed_by_asr_error_is_cancellation](../tests/test_audio.py#L533), lines 533–545.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `controller = self.controller; _, response, _ = self.run_slice(asr=CancelledASR())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_stop_followed_by_asr_error_is_cancellation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(response, ''); self.assertTrue(self.trace.cancelled); self.assertFalse(self.trace.failed); self.assertEqual(self.controller.state, TurnState.STOPPED)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-CE50223C — success plays output and records simulated onset

**Test Case ID:** VC-CE50223C

**Test Case Name:** AudioPipelineSliceTests.test_success_plays_output_and_records_simulated_onset

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667174+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_success_plays_output_and_records_simulated_onset](../tests/test_audio.py#L256), lines 256–264.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `transcript, response, chunks = self.run_slice()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_success_plays_output_and_records_simulated_onset` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(transcript.text, self.asr.text); self.assertEqual(response, verified_template(self.asr.text)); self.assertEqual(chunks, self.output.played_chunks); self.assertEqual(self.trace.t_audible_onset, self.output.audible_onset_time); self.assertTrue(self.trace.is_successful); self.assertFalse(self.output.is_playing()); self.assertEqual(self.controller.state, TurnState.IDLE)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-F5B91426 — template failure and asr failure recover with status

**Test Case ID:** VC-F5B91426

**Test Case Name:** AudioPipelineSliceTests.test_template_failure_and_asr_failure_recover_with_status

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667225+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_template_failure_and_asr_failure_recover_with_status](../tests/test_audio.py#L359), lines 359–377.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_template_failure_and_asr_failure_recover_with_status` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.trace.failure_reason, 'template_error'); self.assertEqual(self.controller.state, TurnState.IDLE); self.assertTrue(any(('unavailable' in m.text for m in self.controller.status_messages))); self.assertEqual(self.trace.failure_reason, 'asr_error'); self.assertEqual(self.output.played_chunks, [])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-EE854677 — tts fails after partial stream flushes before cached prompt

**Test Case ID:** VC-EE854677

**Test Case Name:** AudioPipelineSliceTests.test_tts_fails_after_partial_stream_flushes_before_cached_prompt

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667279+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_tts_fails_after_partial_stream_flushes_before_cached_prompt](../tests/test_audio.py#L547), lines 547–562.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `fallback = CachedSpeechPrompt('Please retry', AudioChunk(b'\x02\x00' * 160, 16000)); count = self.output.stop_calls; _, response, chunks = self.run_slice(tts=PartialFailure(), fallback=fallback)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_tts_fails_after_partial_stream_flushes_before_cached_prompt` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(response, fallback.text); self.assertEqual(chunks, [fallback.chunk]); self.assertEqual(self.output.begin_calls, ['t', 't']); self.assertGreater(self.output.stop_calls, count); self.assertTrue(self.trace.failed); self.assertFalse(self.trace.is_successful)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-775F3133 — tts failure and empty stream have explicit recovery without fake audio

**Test Case ID:** VC-775F3133

**Test Case Name:** AudioPipelineSliceTests.test_tts_failure_and_empty_stream_have_explicit_recovery_without_fake_audio

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667335+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_tts_failure_and_empty_stream_have_explicit_recovery_without_fake_audio](../tests/test_audio.py#L401), lines 401–417.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_tts_failure_and_empty_stream_have_explicit_recovery_without_fake_audio` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(response, AudioPipelineSlice.ERROR_RESPONSE); self.assertEqual(chunks, []); self.assertTrue(self.trace.failed); self.assertFalse(self.trace.meets_1500ms_target); self.assertTrue(any(('unavailable' in m.text for m in self.controller.status_messages))); self.assertEqual(self.controller.state, TurnState.IDLE)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-AA335B4B — wrong trace rejected before asr

**Test Case ID:** VC-AA335B4B

**Test Case Name:** AudioPipelineSliceTests.test_wrong_trace_rejected_before_asr

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667400+00:00

**Description:** Executable contract [tests.test_audio.AudioPipelineSliceTests.test_wrong_trace_rejected_before_asr](../tests/test_audio.py#L457), lines 457–461.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.trace.turn_id = 'other'`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioPipelineSliceTests.test_wrong_trace_rejected_before_asr` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.asr.calls, 0); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-E214F6D2 — capture failure retires turn and emits recovery

**Test Case ID:** VC-E214F6D2

**Test Case Name:** AudioTurnManagementTests.test_capture_failure_retires_turn_and_emits_recovery

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667434+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_capture_failure_retires_turn_and_emits_recovery](../tests/test_audio.py#L220), lines 220–232.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.capture.start_capture = broken_capture`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_capture_failure_retires_turn_and_emits_recovery` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIsNone(self.controller.current_turn_id); self.assertFalse(self.controller.process_transcript(final())); self.assertTrue(any(('capture unavailable' in m.text for m in self.controller.status_messages)))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-9BFECA87 — empty and nonfinal terminal events retire turn

**Test Case ID:** VC-9BFECA87

**Test Case Name:** AudioTurnManagementTests.test_empty_and_nonfinal_terminal_events_retire_turn

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667464+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_empty_and_nonfinal_terminal_events_retire_turn](../tests/test_audio.py#L86), lines 86–104.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_empty_and_nonfinal_terminal_events_retire_turn` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(self.controller.process_transcript(Transcript(kind, '  ', turn_id))); self.assertEqual(self.controller.state, TurnState.IDLE); self.assertIsNone(self.controller.current_turn_id); self.assertFalse(self.capture.capturing); self.assertFalse(self.controller.process_transcript(final(turn_id)))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C6E51AA2 — empty playback cannot be promoted to repeat

**Test Case ID:** VC-C6E51AA2

**Test Case Name:** AudioTurnManagementTests.test_empty_playback_cannot_be_promoted_to_repeat

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667550+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_empty_playback_cannot_be_promoted_to_repeat](../tests/test_audio.py#L214), lines 214–218.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_empty_playback_cannot_be_promoted_to_repeat` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIsNone(self.controller.repeat()); self.assertRaises(RuntimeError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-1DA3ECF8 — failed device stop reports failure and keeps capture gated

**Test Case ID:** VC-1DA3ECF8

**Test Case Name:** AudioTurnManagementTests.test_failed_device_stop_reports_failure_and_keeps_capture_gated

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667581+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_failed_device_stop_reports_failure_and_keeps_capture_gated](../tests/test_audio.py#L196), lines 196–212.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.output.stop_playback = broken_stop; outcome = self.controller.stop()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_failed_device_stop_reports_failure_and_keeps_capture_gated` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(outcome.success); self.assertFalse(outcome.stopped_playback); self.assertFalse(outcome.action_undone); self.assertEqual(self.controller.state, TurnState.FAILED); self.assertTrue(self.controller.is_capture_gated); self.assertFalse(self.controller.resume().success); self.assertRaises(RuntimeError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-E37A69EB — initial and listening states

**Test Case ID:** VC-E37A69EB

**Test Case Name:** AudioTurnManagementTests.test_initial_and_listening_states

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667618+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_initial_and_listening_states](../tests/test_audio.py#L60), lines 60–65.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_initial_and_listening_states` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.controller.state, TurnState.IDLE); self.assertFalse(self.controller.is_capture_gated); self.assertTrue(self.capture.capturing); self.assertFalse(self.controller.is_capture_gated)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-FBA7663D — manual and vad end stop capture and wait for final

**Test Case ID:** VC-FBA7663D

**Test Case Name:** AudioTurnManagementTests.test_manual_and_vad_end_stop_capture_and_wait_for_final

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667636+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_manual_and_vad_end_stop_capture_and_wait_for_final](../tests/test_audio.py#L67), lines 67–76.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_manual_and_vad_end_stop_capture_and_wait_for_final` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(self.capture.capturing); self.assertTrue(self.controller.is_capture_gated); self.assertTrue(self.controller.process_transcript(final(turn_id)))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-D266D50A — partial does not authorize or consume final

**Test Case ID:** VC-D266D50A

**Test Case Name:** AudioTurnManagementTests.test_partial_does_not_authorize_or_consume_final

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667667+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_partial_does_not_authorize_or_consume_final](../tests/test_audio.py#L78), lines 78–84.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `partial = Transcript(TranscriptKind.PARTIAL, 'find', 't')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_partial_does_not_authorize_or_consume_final` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(partial.can_authorize_action); self.assertFalse(self.controller.process_transcript(partial)); self.assertTrue(self.controller.process_transcript(final())); self.assertFalse(self.controller.process_transcript(final()))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-877272F7 — repeat only returns completed response

**Test Case ID:** VC-877272F7

**Test Case Name:** AudioTurnManagementTests.test_repeat_only_returns_completed_response

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667691+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_repeat_only_returns_completed_response](../tests/test_audio.py#L157), lines 157–164.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_repeat_only_returns_completed_response` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIsNone(self.controller.repeat()); self.assertIsNone(self.controller.repeat()); self.assertEqual(self.controller.repeat(), 'Found two options'); self.assertIsNone(self.controller.current_turn_id)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-4C81366A — speaking gates until device drain completes

**Test Case ID:** VC-4C81366A

**Test Case Name:** AudioTurnManagementTests.test_speaking_gates_until_device_drain_completes

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667722+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_speaking_gates_until_device_drain_completes](../tests/test_audio.py#L131), lines 131–141.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.output.on_drain = lambda: self.assertTrue(self.controller.is_capture_gated); completed, onset = self.controller.finish_speaking('t')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_speaking_gates_until_device_drain_completes` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(self.capture.capturing); self.assertTrue(completed); self.assertIsNotNone(onset); self.assertEqual(self.controller.state, TurnState.IDLE); self.assertFalse(self.controller.is_capture_gated); self.assertFalse(self.output.is_playing()); self.assertTrue(self.controller.is_capture_gated)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-1786699E — stale callbacks have no effect

**Test Case ID:** VC-1786699E

**Test Case Name:** AudioTurnManagementTests.test_stale_callbacks_have_no_effect

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667750+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_stale_callbacks_have_no_effect](../tests/test_audio.py#L106), lines 106–113.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `before = self.controller.status_messages`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_stale_callbacks_have_no_effect` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(self.controller.process_transcript(final('old'))); self.assertEqual(self.controller.finish_speaking('old'), (False, None)); self.assertEqual(self.controller.status_messages, before); self.assertEqual(self.controller.state, TurnState.LISTENING)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-225CDE0B — status delivery failure and audio failure fail closed

**Test Case ID:** VC-225CDE0B

**Test Case Name:** AudioTurnManagementTests.test_status_delivery_failure_and_audio_failure_fail_closed

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667777+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_status_delivery_failure_and_audio_failure_fail_closed](../tests/test_audio.py#L185), lines 185–194.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `controller = HalfDuplexTurnController(status_sink=broken_sink)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_status_delivery_failure_and_audio_failure_fail_closed` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(controller.is_session_usable()); self.assertEqual(controller.state, TurnState.FAILED); self.assertIsNone(controller.current_turn_id)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-96DCCCB9 — stop and pause flush playback and never undo action

**Test Case ID:** VC-96DCCCB9

**Test Case Name:** AudioTurnManagementTests.test_stop_and_pause_flush_playback_and_never_undo_action

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667799+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_stop_and_pause_flush_playback_and_never_undo_action](../tests/test_audio.py#L143), lines 143–155.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_stop_and_pause_flush_playback_and_never_undo_action` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.output.stop_calls, count + 1); self.assertTrue(result.stopped_playback); self.assertFalse(result.action_undone); self.assertFalse(self.output.is_playing()); self.assertEqual(self.controller.finish_speaking('t'), (False, None)); self.assertIsNone(self.controller.repeat())
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-14FEABCD — stop pause and dead channels reject late final

**Test Case ID:** VC-14FEABCD

**Test Case Name:** AudioTurnManagementTests.test_stop_pause_and_dead_channels_reject_late_final

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667849+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_stop_pause_and_dead_channels_reject_late_final](../tests/test_audio.py#L115), lines 115–129.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_stop_pause_and_dead_channels_reject_late_final` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(self.controller.process_transcript(final())); self.assertEqual((self.controller.state, self.controller.status_messages), before); self.assertFalse(self.capture.capturing)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-6AFBC663 — unique ids and explicit resume

**Test Case ID:** VC-6AFBC663

**Test Case Name:** AudioTurnManagementTests.test_unique_ids_and_explicit_resume

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667901+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_unique_ids_and_explicit_resume](../tests/test_audio.py#L166), lines 166–174.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_unique_ids_and_explicit_resume` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(RuntimeError); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-0660A652 — unusable session requires health recovery

**Test Case ID:** VC-0660A652

**Test Case Name:** AudioTurnManagementTests.test_unusable_session_requires_health_recovery

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667936+00:00

**Description:** Executable contract [tests.test_audio.AudioTurnManagementTests.test_unusable_session_requires_health_recovery](../tests/test_audio.py#L176), lines 176–183.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioTurnManagementTests.test_unusable_session_requires_health_recovery` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(self.controller.resume().success); self.assertRaises(RuntimeError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-618B1CC2 — candidate runtime and voice metadata are distinct and unpinned

**Test Case ID:** VC-618B1CC2

**Test Case Name:** AudioValueContractTests.test_candidate_runtime_and_voice_metadata_are_distinct_and_unpinned

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.667991+00:00

**Description:** Executable contract [tests.test_audio.AudioValueContractTests.test_candidate_runtime_and_voice_metadata_are_distinct_and_unpinned](../tests/test_audio.py#L698), lines 698–717.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioValueContractTests.test_candidate_runtime_and_voice_metadata_are_distinct_and_unpinned` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(REFERENCE_WHISPER_BASE_EN.licence, 'MIT'); self.assertEqual(REFERENCE_PIPER_RUNTIME.licence, 'GPL-3.0'); self.assertIsNone(REFERENCE_PIPER_RUNTIME.sample_rate_hz); self.assertEqual(REFERENCE_LJ_VOICE.sample_rate_hz, 22050); self.assertTrue(replace(REFERENCE_LJ_VOICE, sha256='a' * 64).is_pinned); self.assertIsNone(ArtifactMetadata('test', 'test', 'unknown', 'en', None).is_commercial_eligible); self.assertFalse(metadata.is_pinned); self.assertIsNone(metadata.is_commercial_eligible); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-CA8F348C — pcm and timestamp validation

**Test Case ID:** VC-CA8F348C

**Test Case Name:** AudioValueContractTests.test_pcm_and_timestamp_validation

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.668062+00:00

**Description:** Executable contract [tests.test_audio.AudioValueContractTests.test_pcm_and_timestamp_validation](../tests/test_audio.py#L670), lines 670–681.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioValueContractTests.test_pcm_and_timestamp_validation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(AudioChunk(b'\x00\x00' * 160, 16000).duration_s, 0.01); self.assertRaises(ValueError); self.assertRaises(ValueError); self.assertRaises(ValueError); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-791CB09D — vad fixture and reset

**Test Case ID:** VC-791CB09D

**Test Case Name:** AudioValueContractTests.test_vad_fixture_and_reset

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.668150+00:00

**Description:** Executable contract [tests.test_audio.AudioValueContractTests.test_vad_fixture_and_reset](../tests/test_audio.py#L719), lines 719–727.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `vad = MockVAD(speech_frames=1, silence_frames_for_endpoint=2); chunk = AudioChunk(b'\x00\x00', 16000)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioValueContractTests.test_vad_fixture_and_reset` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual([vad.process_frame(chunk).state for _ in range(3)], [VADState.SPEECH, VADState.SILENCE, VADState.ENDPOINT_DETECTED]); self.assertEqual(vad.process_frame(chunk).state, VADState.SPEECH)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-15122476 — wav fallback rejects fake and truncated recordings

**Test Case ID:** VC-15122476

**Test Case Name:** AudioValueContractTests.test_wav_fallback_rejects_fake_and_truncated_recordings

**System/Sub-system:** tests.test_audio

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.668184+00:00

**Description:** Executable contract [tests.test_audio.AudioValueContractTests.test_wav_fallback_rejects_fake_and_truncated_recordings](../tests/test_audio.py#L683), lines 683–696.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `buffer = io.BytesIO(); asset = CachedSpeechPrompt.from_wav('Synthetic fixture only', buffer.getvalue())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_audio.AudioValueContractTests.test_wav_fallback_rejects_fake_and_truncated_recordings` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(asset.chunk.duration_s, 0.01); self.assertRaises(ValueError); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C226E37D — aggregate stock blocks fourth add

**Test Case ID:** VC-C226E37D

**Test Case Name:** CartIntegrationTests.test_aggregate_stock_blocks_fourth_add

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.670866+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_aggregate_stock_blocks_fourth_add](../tests/test_cart.py#L117), lines 117–122.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_aggregate_stock_blocks_fourth_add` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.items(self.session), {'v-cheap': 3}); self.assertIsNone(self.cart.pending(self.session)); self.assertRaises(CartError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0367 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-26544BE8 — changed offer and partial coverage never commit

**Test Case ID:** VC-26544BE8

**Test Case Name:** CartIntegrationTests.test_changed_offer_and_partial_coverage_never_commit

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.707608+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_changed_offer_and_partial_coverage_never_commit](../tests/test_cart.py#L143), lines 143–151.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = replace(self.command(), expected_revision='old-revision')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_changed_offer_and_partial_coverage_never_commit` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.items(self.session), {}); self.assertRaises(CartError); self.assertRaises(CartError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0351 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C9DD9C28 — cheapest accounts for existing cart quantity

**Test Case ID:** VC-C9DD9C28

**Test Case Name:** CartIntegrationTests.test_cheapest_accounts_for_existing_cart_quantity

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.742691+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_cheapest_accounts_for_existing_cart_quantity](../tests/test_cart.py#L138), lines 138–141.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `receipt = self.cart.add(self.command(selection='cheapest'))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_cheapest_accounts_for_existing_cart_quantity` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(receipt.variant_id, 'v-best')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0333 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C779BB64 — cheapest replay is before new query selection

**Test Case ID:** VC-C779BB64

**Test Case Name:** CartIntegrationTests.test_cheapest_replay_is_before_new_query_selection

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.776026+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_cheapest_replay_is_before_new_query_selection](../tests/test_cart.py#L124), lines 124–136.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command(selection='cheapest'); first = self.cart.add(command); raw = fabricated_document('fixture-2', 'fixture-1')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_cheapest_replay_is_before_new_query_selection` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(replay.variant_id, first.variant_id); self.assertEqual(replay.unit_price_minor, first.unit_price_minor); self.assertEqual(self.cart.items(self.session), {'v-cheap': 1}); self.assertEqual(self.cart.add(self.command(selection='cheapest')).variant_id, 'v-best')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0447 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-959E7A94 — commit reply loss reconciles original receipt

**Test Case ID:** VC-959E7A94

**Test Case Name:** CartIntegrationTests.test_commit_reply_loss_reconciles_original_receipt

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.820731+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_commit_reply_loss_reconciles_original_receipt](../tests/test_cart.py#L180), lines 180–189.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command(); receipt = LostReply(self.database).add(command)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_commit_reply_loss_reconciles_original_receipt` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(receipt.operation_id, command.operation_id); self.assertEqual(self.cart.items(self.session), {'v-cheap': 1})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0266 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-73E28456 — commit verified by immutable receipt and retry exactly once

**Test Case ID:** VC-73E28456

**Test Case Name:** CartIntegrationTests.test_commit_verified_by_immutable_receipt_and_retry_exactly_once

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.847366+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_commit_verified_by_immutable_receipt_and_retry_exactly_once](../tests/test_cart.py#L63), lines 63–79.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command(); receipt = self.cart.add(command)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_commit_verified_by_immutable_receipt_and_retry_exactly_once` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(receipt.added_quantity, 1); self.assertEqual(receipt.line_price_minor, 50000); self.assertEqual(self.cart.add(command), receipt); self.assertEqual(CartService(self.database).retry(self.session, command.operation_id), receipt); self.assertEqual(self.cart.items(self.session), {'v-cheap': 1}); self.assertRaises(psycopg.Error)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0459 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-9ACC9FD9 — late turn cancel and precommit cancellation do not add

**Test Case ID:** VC-9ACC9FD9

**Test Case Name:** CartIntegrationTests.test_late_turn_cancel_and_precommit_cancellation_do_not_add

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.893315+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_late_turn_cancel_and_precommit_cancellation_do_not_add](../tests/test_cart.py#L153), lines 153–169.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `stale = self.command(); self.turn = self.sessions.begin_turn(self.session); command = self.command()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_late_turn_cancel_and_precommit_cancellation_do_not_add` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.items(self.session), {}); self.assertRaises(CartError); self.assertRaises(CartError); self.assertRaises(CartError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0461 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-36152B4B — new intentional add and old receipt remain distinct

**Test Case ID:** VC-36152B4B

**Test Case Name:** CartIntegrationTests.test_new_intentional_add_and_old_receipt_remain_distinct

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.939402+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_new_intentional_add_and_old_receipt_remain_distinct](../tests/test_cart.py#L92), lines 92–100.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `original = self.command(); first = self.cart.add(original); replay = self.cart.add(original)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_new_intentional_add_and_old_receipt_remain_distinct` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.items(self.session), {'v-cheap': 2}); self.assertEqual(replay.resulting_quantity, first.resulting_quantity); self.assertEqual(replay.resulting_quantity, 1); self.assertEqual(self.cart.items(self.session), {'v-cheap': 2})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0434 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-AEF2F77F — parallel duplicate workers apply one increment

**Test Case ID:** VC-AEF2F77F

**Test Case Name:** CartIntegrationTests.test_parallel_duplicate_workers_apply_one_increment

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:15.982793+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_parallel_duplicate_workers_apply_one_increment](../tests/test_cart.py#L81), lines 81–90.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_parallel_duplicate_workers_apply_one_increment` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(set(receipts), {command.operation_id}); self.assertEqual(self.cart.items(self.session), {'v-cheap': 1})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0633 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-E90B1EFD — pending precommit outage blocks replacement operation

**Test Case ID:** VC-E90B1EFD

**Test Case Name:** CartIntegrationTests.test_pending_precommit_outage_blocks_replacement_operation

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.046107+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_pending_precommit_outage_blocks_replacement_operation](../tests/test_cart.py#L207), lines 207–219.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_pending_precommit_outage_blocks_replacement_operation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.pending(self.session), command.operation_id); self.assertEqual(self.cart.items(self.session), {'v-cheap': 1}); self.assertRaises(OutcomeUnknown); self.assertRaises(CartError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0396 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-7A00C9D1 — result ordinals require current complete presentation

**Test Case ID:** VC-7A00C9D1

**Test Case Name:** CartIntegrationTests.test_result_ordinals_require_current_complete_presentation

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.085707+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_result_ordinals_require_current_complete_presentation](../tests/test_cart.py#L269), lines 269–288.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = PostgresCatalogue(self.database).search(SearchRequest(HardConstraints('INR', category='backpack'))); listing = self.sessions.publish_results(self.session, self.turn, result); first = self.sessions.resolve(self.session, 1)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_result_ordinals_require_current_complete_presentation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(self.sessions.mark_presented(self.session, listing.list_id, self.turn)); self.assertEqual(first.variant_id, listing.offers[0].variant_id); self.assertFalse(self.sessions.mark_presented(self.session, listing.list_id, self.turn)); self.assertNotEqual(replacement.list_id, listing.list_id); self.assertRaises(SessionError); self.assertRaises(SessionError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0343 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-FDC3DA87 — same operation different payload or session is conflict

**Test Case ID:** VC-FDC3DA87

**Test Case Name:** CartIntegrationTests.test_same_operation_different_payload_or_session_is_conflict

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.119986+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_same_operation_different_payload_or_session_is_conflict](../tests/test_cart.py#L102), lines 102–115.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command(); other = self.sessions.create(); turn = self.sessions.begin_turn(other)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_same_operation_different_payload_or_session_is_conflict` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.items(other), {}); self.assertRaises(CartError); self.assertRaises(CartError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0399 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-FDC950F1 — session isolation and expiry cleanup

**Test Case ID:** VC-FDC950F1

**Test Case Name:** CartIntegrationTests.test_session_isolation_and_expiry_cleanup

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.159916+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_session_isolation_and_expiry_cleanup](../tests/test_cart.py#L238), lines 238–267.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command(); other = self.sessions.create()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_session_isolation_and_expiry_cleanup` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.items(other), {}); self.assertIsNone(self.cart.read_receipt(other, command.operation_id)); self.assertEqual(self.sessions.cleanup_expired(), 1); self.assertEqual(self.database.inspect()['product_count'], 3); self.assertRaises(SessionError); self.assertEqual(connection.execute('SELECT count(*) AS n FROM commands WHERE session_id=%s', (self.session,)).fetchone()['n'], 0); self.assertEqual(connection.execute('SELECT count(*) AS n FROM operation_receipts WHERE session_id=%s', (self.session,)).fetchone()['n'], 0)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0398 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-6E126180 — stop after commit does not undo receipt

**Test Case ID:** VC-6E126180

**Test Case Name:** CartIntegrationTests.test_stop_after_commit_does_not_undo_receipt

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.199755+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_stop_after_commit_does_not_undo_receipt](../tests/test_cart.py#L171), lines 171–178.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command(); receipt = self.cart.add(command)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_stop_after_commit_does_not_undo_receipt` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.read_receipt(self.session, command.operation_id), receipt); self.assertEqual(self.cart.items(self.session), {'v-cheap': 1})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0318 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-9825AF5C — unknown outcome keeps identity and can be recovered after restart

**Test Case ID:** VC-9825AF5C

**Test Case Name:** CartIntegrationTests.test_unknown_outcome_keeps_identity_and_can_be_recovered_after_restart

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.231622+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_unknown_outcome_keeps_identity_and_can_be_recovered_after_restart](../tests/test_cart.py#L191), lines 191–205.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command(); receipt = CartService(self.database).retry(self.session, command.operation_id)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_unknown_outcome_keeps_identity_and_can_be_recovered_after_restart` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(receipt.operation_id, command.operation_id); self.assertEqual(self.cart.items(self.session), {'v-cheap': 1}); self.assertRaises(OutcomeUnknown)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0337 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-4AE5774C — whole transaction retry uses original operation

**Test Case ID:** VC-4AE5774C

**Test Case Name:** CartIntegrationTests.test_whole_transaction_retry_uses_original_operation

**System/Sub-system:** tests.test_cart

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.265379+00:00

**Description:** Executable contract [tests.test_cart.CartIntegrationTests.test_whole_transaction_retry_uses_original_operation](../tests/test_cart.py#L221), lines 221–236.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `service = Transient(self.database)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_cart.CartIntegrationTests.test_whole_transaction_retry_uses_original_operation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(service.calls, 2); self.assertEqual(self.cart.items(self.session), {'v-cheap': 1})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0419 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-E8ADA651 — duplicate ids skus and orphan variants fail snapshot creation

**Test Case ID:** VC-E8ADA651

**Test Case Name:** ExactLookupAndSnapshotTests.test_duplicate_ids_skus_and_orphan_variants_fail_snapshot_creation

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307353+00:00

**Description:** Executable contract [tests.test_catalogue.ExactLookupAndSnapshotTests.test_duplicate_ids_skus_and_orphan_variants_fail_snapshot_creation](../tests/test_catalogue.py#L386), lines 386–395.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.ExactLookupAndSnapshotTests.test_duplicate_ids_skus_and_orphan_variants_fail_snapshot_creation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-479ADEB7 — exact lookup resolves each supported identifier kind

**Test Case ID:** VC-479ADEB7

**Test Case Name:** ExactLookupAndSnapshotTests.test_exact_lookup_resolves_each_supported_identifier_kind

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307486+00:00

**Description:** Executable contract [tests.test_catalogue.ExactLookupAndSnapshotTests.test_exact_lookup_resolves_each_supported_identifier_kind](../tests/test_catalogue.py#L333), lines 333–344.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `cases = ((IdentifierKind.VARIANT_ID, 'black', ('black',)), (IdentifierKind.SKU, 'SKU-BLU', ('blue',)), (IdentifierKind.PRODUCT_ID, 'p1', ('black', 'blue')), (IdentifierKind.MODEL_NUMBER, 'MODEL-X', ('black', 'blue')))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.ExactLookupAndSnapshotTests.test_exact_lookup_resolves_each_supported_identifier_kind` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(ids(self.db.lookup(ExactIdentifier(kind, value))), expected)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-72B6EB81 — exact search still enforces constraints and scopes identity

**Test Case ID:** VC-72B6EB81

**Test Case Name:** ExactLookupAndSnapshotTests.test_exact_search_still_enforces_constraints_and_scopes_identity

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307567+00:00

**Description:** Executable contract [tests.test_catalogue.ExactLookupAndSnapshotTests.test_exact_search_still_enforces_constraints_and_scopes_identity](../tests/test_catalogue.py#L354), lines 354–367.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `exact = replace(request(), route=RetrievalRoute.EXACT, identifier=ExactIdentifier(IdentifierKind.VARIANT_ID, 'blue')); black = replace(exact, identifier=ExactIdentifier(IdentifierKind.VARIANT_ID, 'black')); result = self.db.search(black)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.ExactLookupAndSnapshotTests.test_exact_search_still_enforces_constraints_and_scopes_identity` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.db.search(exact).status, SearchStatus.NO_MATCH); self.assertEqual(result.scope, ClaimScope.EXACT_IDENTIFIER); self.assertFalse(result.can_claim_catalogue_minimum); self.assertEqual(ids(result.matches), ('black',))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-020453B9 — lookup is case sensitive and does not fuzzily substitute

**Test Case ID:** VC-020453B9

**Test Case Name:** ExactLookupAndSnapshotTests.test_lookup_is_case_sensitive_and_does_not_fuzzily_substitute

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307639+00:00

**Description:** Executable contract [tests.test_catalogue.ExactLookupAndSnapshotTests.test_lookup_is_case_sensitive_and_does_not_fuzzily_substitute](../tests/test_catalogue.py#L346), lines 346–352.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.ExactLookupAndSnapshotTests.test_lookup_is_case_sensitive_and_does_not_fuzzily_substitute` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.db.lookup(ExactIdentifier(IdentifierKind.SKU, 'sku-blk')), ()); self.assertEqual(self.db.lookup(ExactIdentifier(IdentifierKind.MODEL_NUMBER, 'MODEL')), ())
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-D07F39ED — raw lookup does not assert availability

**Test Case ID:** VC-D07F39ED

**Test Case Name:** ExactLookupAndSnapshotTests.test_raw_lookup_does_not_assert_availability

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307673+00:00

**Description:** Executable contract [tests.test_catalogue.ExactLookupAndSnapshotTests.test_raw_lookup_does_not_assert_availability](../tests/test_catalogue.py#L379), lines 379–384.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `db = catalogue([variant(available=False)]); identifier = ExactIdentifier(IdentifierKind.VARIANT_ID, 'v1'); exact = replace(request(), route=RetrievalRoute.EXACT, identifier=identifier)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.ExactLookupAndSnapshotTests.test_raw_lookup_does_not_assert_availability` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(ids(db.lookup(identifier)), ('v1',)); self.assertTrue(db.search(exact).can_claim_no_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-BF79AC7F — unknown identifier in complete and incomplete sources

**Test Case ID:** VC-BF79AC7F

**Test Case Name:** ExactLookupAndSnapshotTests.test_unknown_identifier_in_complete_and_incomplete_sources

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307727+00:00

**Description:** Executable contract [tests.test_catalogue.ExactLookupAndSnapshotTests.test_unknown_identifier_in_complete_and_incomplete_sources](../tests/test_catalogue.py#L369), lines 369–377.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `exact = replace(request(), route=RetrievalRoute.EXACT, identifier=ExactIdentifier(IdentifierKind.SKU, 'missing')); partial = catalogue([variant()], coverage=Coverage.PARTIAL)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.ExactLookupAndSnapshotTests.test_unknown_identifier_in_complete_and_incomplete_sources` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(self.db.search(exact).can_claim_no_match); self.assertEqual(partial.search(exact).status, SearchStatus.INCOMPLETE)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-D15E9F3C — untyped coverage and invalid records fail instead of being dropped

**Test Case ID:** VC-D15E9F3C

**Test Case Name:** ExactLookupAndSnapshotTests.test_untyped_coverage_and_invalid_records_fail_instead_of_being_dropped

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307777+00:00

**Description:** Executable contract [tests.test_catalogue.ExactLookupAndSnapshotTests.test_untyped_coverage_and_invalid_records_fail_instead_of_being_dropped](../tests/test_catalogue.py#L397), lines 397–401.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.ExactLookupAndSnapshotTests.test_untyped_coverage_and_invalid_records_fail_instead_of_being_dropped` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(TypeError); self.assertRaises(TypeError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-A269133A — active product without variants blocks complete claim

**Test Case ID:** VC-A269133A

**Test Case Name:** StructuredSelectionTests.test_active_product_without_variants_blocks_complete_claim

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307821+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_active_product_without_variants_blocks_complete_claim](../tests/test_catalogue.py#L65), lines 65–72.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `db = catalogue([variant()], [product(), product('missing', category='backpack')]); db = catalogue([variant()], [product(), product('unrelated', category='shirt')])`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_active_product_without_variants_blocks_complete_claim` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(db.search(request()).can_claim_catalogue_minimum); self.assertEqual(db.search(request()).status, SearchStatus.INCOMPLETE); self.assertTrue(db.search(request()).can_claim_catalogue_minimum)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-9E0DCB14 — all verified nonmatches prove no match

**Test Case ID:** VC-9E0DCB14

**Test Case Name:** StructuredSelectionTests.test_all_verified_nonmatches_prove_no_match

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307885+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_all_verified_nonmatches_prove_no_match](../tests/test_catalogue.py#L195), lines 195–200.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = catalogue([variant(colour='red'), variant('costly', price=300000)]).search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_all_verified_nonmatches_prove_no_match` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.matches, ()); self.assertTrue(result.can_claim_no_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-1D5B470F — coverage defaults to unknown even for well formed records

**Test Case ID:** VC-1D5B470F

**Test Case Name:** StructuredSelectionTests.test_coverage_defaults_to_unknown_even_for_well_formed_records

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307924+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_coverage_defaults_to_unknown_even_for_well_formed_records](../tests/test_catalogue.py#L211), lines 211–216.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = InMemoryCatalogue([product()], [variant()], revision='v1').search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_coverage_defaults_to_unknown_even_for_well_formed_records` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertIn(IssueCode.UNKNOWN_COVERAGE, {i.code for i in result.issues})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-46F55A15 — currencies are not compared or converted

**Test Case ID:** VC-46F55A15

**Test Case Name:** StructuredSelectionTests.test_currencies_are_not_compared_or_converted

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307956+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_currencies_are_not_compared_or_converted](../tests/test_catalogue.py#L218), lines 218–222.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `db = catalogue([variant('usd', price=Money(1, 'USD')), variant('inr')]); result = db.search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_currencies_are_not_compared_or_converted` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(ids(result.matches), ('inr',)); self.assertTrue(result.can_claim_catalogue_minimum)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-7D44AE44 — description cannot fill a missing structured colour

**Test Case ID:** VC-7D44AE44

**Test Case Name:** StructuredSelectionTests.test_description_cannot_fill_a_missing_structured_colour

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.307993+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_description_cannot_fill_a_missing_structured_colour](../tests/test_catalogue.py#L137), lines 137–141.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `db = catalogue([variant(colour=None)], [product(description='solid black backpack')])`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_description_cannot_fill_a_missing_structured_colour` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(db.search(request()).status, SearchStatus.INCOMPLETE)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-E5E609FB — discovery is explicitly unsupported not structured fallback

**Test Case ID:** VC-E5E609FB

**Test Case Name:** StructuredSelectionTests.test_discovery_is_explicitly_unsupported_not_structured_fallback

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.308023+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_discovery_is_explicitly_unsupported_not_structured_fallback](../tests/test_catalogue.py#L257), lines 257–267.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `query = SearchRequest(HardConstraints('INR'), route=RetrievalRoute.DISCOVERY, semantic_query='good for college'); result = catalogue([variant()]).search(query)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_discovery_is_explicitly_unsupported_not_structured_fallback` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.status, SearchStatus.UNSUPPORTED); self.assertEqual(result.scope, ClaimScope.UNVERIFIED); self.assertEqual(result.matches, ()); self.assertFalse(result.can_claim_no_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-58226A25 — empty complete catalogue proves no match but not a minimum

**Test Case ID:** VC-58226A25

**Test Case Name:** StructuredSelectionTests.test_empty_complete_catalogue_proves_no_match_but_not_a_minimum

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.308051+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_empty_complete_catalogue_proves_no_match_but_not_a_minimum](../tests/test_catalogue.py#L189), lines 189–193.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = catalogue([], []).search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_empty_complete_catalogue_proves_no_match_but_not_a_minimum` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.status, SearchStatus.NO_MATCH); self.assertTrue(result.can_claim_no_match); self.assertFalse(result.can_claim_catalogue_minimum)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-01AB292F — full catalogue finds cheaper poorly described item beyond top k

**Test Case ID:** VC-01AB292F

**Test Case Name:** StructuredSelectionTests.test_full_catalogue_finds_cheaper_poorly_described_item_beyond_top_k

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.308078+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_full_catalogue_finds_cheaper_poorly_described_item_beyond_top_k](../tests/test_catalogue.py#L40), lines 40–63.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `products = [product('p-top1', description='Black backpack for college with laptop space'), product('p-top2', description='Popular black backpack, college daily bag'), product('p-omitted', name='R7', description='')]; variants = [variant('v-top1', 'p-top1', 120000), variant('v-top2', 'p-top2', 150000), variant('v-omitted', 'p-omitted', 90000)]; hypothetical_semantic_top_k = variants[:2]`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_full_catalogue_finds_cheaper_poorly_described_item_beyond_top_k` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(min((v.price.minor_units for v in hypothetical_semantic_top_k)), 120000); self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, 'v-omitted'); self.assertEqual(set(ids(result.matches)), {'v-top1', 'v-top2', 'v-omitted'}); self.assertTrue(result.can_claim_catalogue_minimum); self.assertEqual(result.catalogue_revision, 'synthetic-snapshot-v1')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-9DD8AA30 — generated complete catalogues agree with independent full set oracle

**Test Case ID:** VC-9DD8AA30

**Test Case Name:** StructuredSelectionTests.test_generated_complete_catalogues_agree_with_independent_full_set_oracle

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.308130+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_generated_complete_catalogues_agree_with_independent_full_set_oracle](../tests/test_catalogue.py#L269), lines 269–320.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `rng = random.Random(173)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_generated_complete_catalogues_agree_with_independent_full_set_oracle` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(pair, expected[0] if expected else None); self.assertEqual(set(ids(result.matches)), {key for _, key in expected}); self.assertEqual(result.can_claim_no_match, not expected)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0115 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-6204A547 — insufficient known stock and inactive records are excluded

**Test Case ID:** VC-6204A547

**Test Case Name:** StructuredSelectionTests.test_insufficient_known_stock_and_inactive_records_are_excluded

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.319610+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_insufficient_known_stock_and_inactive_records_are_excluded](../tests/test_catalogue.py#L240), lines 240–246.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `db = catalogue([variant('one', stock_quantity=1), variant('inactive', active=False)]); parent_inactive = catalogue([variant()], [product(active=False)])`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_insufficient_known_stock_and_inactive_records_are_excluded` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(db.search(request(quantity=2)).can_claim_no_match); self.assertTrue(parent_inactive.search(request()).can_claim_no_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-12E6A18B — known nonmatch dominates unrelated unknown facts

**Test Case ID:** VC-12E6A18B

**Test Case Name:** StructuredSelectionTests.test_known_nonmatch_dominates_unrelated_unknown_facts

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.319684+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_known_nonmatch_dominates_unrelated_unknown_facts](../tests/test_catalogue.py#L123), lines 123–131.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `db = catalogue([variant('backpack'), variant('shirt', 'p-shirt', price=None, colour=None)], [product(), product('p-shirt', category='shirt')]); result = db.search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_known_nonmatch_dominates_unrelated_unknown_facts` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(ids(result.matches), ('backpack',)); self.assertTrue(result.can_claim_catalogue_minimum); self.assertEqual(result.issues, ())
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-800B02E8 — known zero price is a valid minimum

**Test Case ID:** VC-800B02E8

**Test Case Name:** StructuredSelectionTests.test_known_zero_price_is_a_valid_minimum

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.319735+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_known_zero_price_is_a_valid_minimum](../tests/test_catalogue.py#L224), lines 224–228.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = catalogue([variant('paid'), variant('free', price=0)]).search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_known_zero_price_is_a_valid_minimum` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, 'free')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C0FE775C — missing price is unknown and blocks global claim

**Test Case ID:** VC-C0FE775C

**Test Case Name:** StructuredSelectionTests.test_missing_price_is_unknown_and_blocks_global_claim

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.319774+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_missing_price_is_unknown_and_blocks_global_claim](../tests/test_catalogue.py#L87), lines 87–96.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = catalogue([variant('known'), variant('missing', price=None)]).search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_missing_price_is_unknown_and_blocks_global_claim` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(ids(result.matches), ('known',)); self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertEqual(result.scope, ClaimScope.VERIFIED_RECORDS); self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, 'known'); self.assertFalse(result.can_claim_catalogue_minimum); self.assertIn(IssueCode.MISSING_PRICE, {issue.code for issue in result.issues})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-6D3589CA — only missing price is not a verified no match

**Test Case ID:** VC-6D3589CA

**Test Case Name:** StructuredSelectionTests.test_only_missing_price_is_not_a_verified_no_match

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.319815+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_only_missing_price_is_not_a_verified_no_match](../tests/test_catalogue.py#L98), lines 98–102.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = catalogue([variant(price=None)]).search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_only_missing_price_is_not_a_verified_no_match` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertIsNone(result.cheapest_qualifying_match); self.assertFalse(result.can_claim_no_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C313EDD8 — paise boundary uses integers without rounding

**Test Case ID:** VC-C313EDD8

**Test Case Name:** StructuredSelectionTests.test_paise_boundary_uses_integers_without_rounding

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.319853+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_paise_boundary_uses_integers_without_rounding](../tests/test_catalogue.py#L83), lines 83–85.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `db = catalogue([variant('below', price=199999), variant('at', price=200000)])`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_paise_boundary_uses_integers_without_rounding` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(ids(db.search(request()).matches), ('below',))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-8B5595C5 — partial and unknown coverage block global claims

**Test Case ID:** VC-8B5595C5

**Test Case Name:** StructuredSelectionTests.test_partial_and_unknown_coverage_block_global_claims

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.319890+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_partial_and_unknown_coverage_block_global_claims](../tests/test_catalogue.py#L202), lines 202–209.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_partial_and_unknown_coverage_block_global_claims` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertFalse(result.can_claim_catalogue_minimum); self.assertFalse(result.can_claim_no_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-FF3BDEB9 — price ties are stable for every input permutation

**Test Case ID:** VC-FF3BDEB9

**Test Case Name:** StructuredSelectionTests.test_price_ties_are_stable_for_every_input_permutation

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.319976+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_price_ties_are_stable_for_every_input_permutation](../tests/test_catalogue.py#L182), lines 182–187.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `variants = [variant('b'), variant('a'), variant('c', price=120000)]`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_price_ties_are_stable_for_every_input_permutation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, 'a'); self.assertEqual(ids(result.matches), ('a', 'b', 'c'))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-E6DDC213 — snapshot does not change when input lists change

**Test Case ID:** VC-E6DDC213

**Test Case Name:** StructuredSelectionTests.test_snapshot_does_not_change_when_input_lists_change

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.320091+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_snapshot_does_not_change_when_input_lists_change](../tests/test_catalogue.py#L248), lines 248–255.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `source = [variant('original')]; db = catalogue(source)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_snapshot_does_not_change_when_input_lists_change` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(db.search(request()).cheapest_qualifying_match.variant.variant_id, 'original')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-27B998AE — stale above budget price cannot prove nonmatch

**Test Case ID:** VC-27B998AE

**Test Case Name:** StructuredSelectionTests.test_stale_above_budget_price_cannot_prove_nonmatch

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.320125+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_stale_above_budget_price_cannot_prove_nonmatch](../tests/test_catalogue.py#L153), lines 153–158.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = catalogue([variant(price=900000, price_freshness=Freshness.STALE)]).search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_stale_above_budget_price_cannot_prove_nonmatch` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertFalse(result.can_claim_no_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-800ABBCD — stale and unverified prices are not qualified

**Test Case ID:** VC-800ABBCD

**Test Case Name:** StructuredSelectionTests.test_stale_and_unverified_prices_are_not_qualified

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.320158+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_stale_and_unverified_prices_are_not_qualified](../tests/test_catalogue.py#L143), lines 143–151.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_stale_and_unverified_prices_are_not_qualified` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertIsNone(result.cheapest_qualifying_match); self.assertFalse(result.can_claim_no_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-FE907B97 — strict and inclusive price boundaries

**Test Case ID:** VC-FE907B97

**Test Case Name:** StructuredSelectionTests.test_strict_and_inclusive_price_boundaries

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.320216+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_strict_and_inclusive_price_boundaries](../tests/test_catalogue.py#L74), lines 74–81.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `db = catalogue([variant('at', price=200000), variant('over', price=200001)]); strict = db.search(request(operator=PriceOperator.LT)); inclusive = db.search(request(operator=PriceOperator.LTE))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_strict_and_inclusive_price_boundaries` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(strict.status, SearchStatus.NO_MATCH); self.assertTrue(strict.can_claim_no_match); self.assertEqual(ids(inclusive.matches), ('at',)); self.assertTrue(inclusive.can_claim_catalogue_minimum)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-0E8E4863 — unknown availability and multi unit stock block claims

**Test Case ID:** VC-0E8E4863

**Test Case Name:** StructuredSelectionTests.test_unknown_availability_and_multi_unit_stock_block_claims

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.320263+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_unknown_availability_and_multi_unit_stock_block_claims](../tests/test_catalogue.py#L230), lines 230–238.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `single = catalogue([variant(stock_quantity=None)]).search(request(quantity=1))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_unknown_availability_and_multi_unit_stock_block_claims` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(single.can_claim_catalogue_minimum); self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertFalse(result.can_claim_no_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-031D5FA2 — unknown required category colour or size never matches

**Test Case ID:** VC-031D5FA2

**Test Case Name:** StructuredSelectionTests.test_unknown_required_category_colour_or_size_never_matches

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.320331+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_unknown_required_category_colour_or_size_never_matches](../tests/test_catalogue.py#L104), lines 104–117.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_unknown_required_category_colour_or_size_never_matches` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.matches, ()); self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertFalse(result.can_claim_no_match); self.assertIn(IssueCode.UNKNOWN_ATTRIBUTE, {i.code for i in result.issues})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-476080D9 — unknown unrequested size does not block selection

**Test Case ID:** VC-476080D9

**Test Case Name:** StructuredSelectionTests.test_unknown_unrequested_size_does_not_block_selection

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.320407+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_unknown_unrequested_size_does_not_block_selection](../tests/test_catalogue.py#L119), lines 119–121.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = catalogue([variant(size=None)]).search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_unknown_unrequested_size_does_not_block_selection` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(result.can_claim_catalogue_minimum)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-43D52612 — variant identity does not borrow other colour price or stock

**Test Case ID:** VC-43D52612

**Test Case Name:** StructuredSelectionTests.test_variant_identity_does_not_borrow_other_colour_price_or_stock

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.320436+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_variant_identity_does_not_borrow_other_colour_price_or_stock](../tests/test_catalogue.py#L160), lines 160–180.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `db = catalogue([variant('black-small', price=150000, size='small', stock_quantity=0, available=False), variant('blue-small', price=1000, colour='blue', size='small'), variant('black-large', price=170000, size='large')]); small = db.search(request(size='small')); any_size = db.search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_variant_identity_does_not_borrow_other_colour_price_or_stock` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(small.can_claim_no_match); self.assertEqual(ids(any_size.matches), ('black-large',)); self.assertEqual(any_size.cheapest_qualifying_match.variant.price.minor_units, 170000)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-050FAB42 — wrong colour dominates unknown category

**Test Case ID:** VC-050FAB42

**Test Case Name:** StructuredSelectionTests.test_wrong_colour_dominates_unknown_category

**System/Sub-system:** tests.test_catalogue

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.320492+00:00

**Description:** Executable contract [tests.test_catalogue.StructuredSelectionTests.test_wrong_colour_dominates_unknown_category](../tests/test_catalogue.py#L133), lines 133–135.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `item = CatalogueItem(product(category=None), variant(colour='blue', price=None))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_catalogue.StructuredSelectionTests.test_wrong_colour_dominates_unknown_category` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIs(qualify(item, request().constraints).state, Eligibility.REJECTED)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-19B3246F — expired source never displays verified availability

**Test Case ID:** VC-19B3246F

**Test Case Name:** BrowserDatabaseTests.test_expired_source_never_displays_verified_availability

**System/Sub-system:** tests.test_dataset

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.323351+00:00

**Description:** Executable contract [tests.test_dataset.BrowserDatabaseTests.test_expired_source_never_displays_verified_availability](../tests/test_dataset.py#L79), lines 79–95.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = CatalogueBrowser(self.database).search('backpack', currency='INR')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_dataset.BrowserDatabaseTests.test_expired_source_never_displays_verified_availability` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(result['items']); self.assertTrue(all((row['available'] is None and (not row['can_add']) for row in result['items']))); self.assertTrue(all((row['price_freshness'] == 'stale' for row in result['items'])))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0157 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-38714622 — historical metadata browsable but cannot add

**Test Case ID:** VC-38714622

**Test Case Name:** BrowserDatabaseTests.test_historical_metadata_browsable_but_cannot_add

**System/Sub-system:** tests.test_dataset

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.339015+00:00

**Description:** Executable contract [tests.test_dataset.BrowserDatabaseTests.test_historical_metadata_browsable_but_cannot_add](../tests/test_dataset.py#L109), lines 109–142.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = fabricated_document(); raw['variants'][0]['price'] = None; raw['metadata'] = {'p-best': {'source_url': 'https://example.invalid/TEST', 'source_record_id': 'TEST', 'brand': 'Fixture', 'historical': True, 'price_currency': 'INR'}}`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_dataset.BrowserDatabaseTests.test_historical_metadata_browsable_but_cannot_add` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertGreater(result['total'], 1); self.assertEqual(len(result['items']), 1); self.assertFalse(result['items'][0]['can_add']); self.assertFalse(result['can_claim_global_minimum']); self.assertIsNotNone(result['cheapest']); self.assertEqual(CatalogueBrowser(self.database).search('', brand='Fixture', currency='INR')['total'], 1); self.assertEqual(CatalogueBrowser(self.database).search('', brand='Fixture')['total'], 1); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0191 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-778A674C — metadata hybrid generation and minimum are scoped

**Test Case ID:** VC-778A674C

**Test Case Name:** BrowserDatabaseTests.test_metadata_hybrid_generation_and_minimum_are_scoped

**System/Sub-system:** tests.test_dataset

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.358171+00:00

**Description:** Executable contract [tests.test_dataset.BrowserDatabaseTests.test_metadata_hybrid_generation_and_minimum_are_scoped](../tests/test_dataset.py#L97), lines 97–107.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `encoder = FixtureEncoder(); result = CatalogueBrowser(self.database, encoder).search('college backpack', currency='INR')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_dataset.BrowserDatabaseTests.test_metadata_hybrid_generation_and_minimum_are_scoped` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIn('exact semantic', result['semantic_status']); self.assertFalse(result['can_claim_global_minimum']); self.assertIsNotNone(result['cheapest'])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0137 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-076210B9 — historical amount equivalence and minor boundaries

**Test Case ID:** VC-076210B9

**Test Case Name:** DatasetTests.test_historical_amount_equivalence_and_minor_boundaries

**System/Sub-system:** tests.test_dataset

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.371903+00:00

**Description:** Executable contract [tests.test_dataset.DatasetTests.test_historical_amount_equivalence_and_minor_boundaries](../tests/test_dataset.py#L16), lines 16–29.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_dataset.DatasetTests.test_historical_amount_equivalence_and_minor_boundaries` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(historical_usd(value), expected)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-8BB83A7B — real schema normalization provenance duplicates unknowns and hash

**Test Case ID:** VC-8BB83A7B

**Test Case Name:** DatasetTests.test_real_schema_normalization_provenance_duplicates_unknowns_and_hash

**System/Sub-system:** tests.test_dataset

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.371995+00:00

**Description:** Executable contract [tests.test_dataset.DatasetTests.test_real_schema_normalization_provenance_duplicates_unknowns_and_hash](../tests/test_dataset.py#L31), lines 31–63.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = {'parent_asin': 'TEST-ONLY', 'title': 'Fabricated test appliance', 'main_category': 'test', 'price': '4.25', 'description': ['test'], 'features': [], 'details': {'Brand': 'Test-only', 'Size': 'large'}}`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_dataset.DatasetTests.test_real_schema_normalization_provenance_duplicates_unknowns_and_hash` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual((report['imported'], report['duplicates'], report['rejected']), (1, 1, 1)); self.assertEqual(snapshot['variants'][0]['price']['currency'], 'USD'); self.assertIsNone(snapshot['variants'][0]['available']); self.assertEqual(snapshot['variants'][0]['price_freshness'], 'stale'); self.assertEqual(snapshot['metadata']['TEST-ONLY']['raw_price'], '4.25'); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0009 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-B847743B — conflicting budget currency is rejected

**Test Case ID:** VC-B847743B

**Test Case Name:** MoneyAndContractTests.test_conflicting_budget_currency_is_rejected

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.372939+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_conflicting_budget_currency_is_rejected](../tests/test_domain.py#L50), lines 50–55.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_conflicting_budget_currency_is_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C50344CB — contracts are immutable

**Test Case ID:** VC-C50344CB

**Test Case Name:** MoneyAndContractTests.test_contracts_are_immutable

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.372973+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_contracts_are_immutable](../tests/test_domain.py#L95), lines 95–98.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `item = variant()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_contracts_are_immutable` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(FrozenInstanceError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-0162A220 — currency is explicit and not silently normalized

**Test Case ID:** VC-0162A220

**Test Case Name:** MoneyAndContractTests.test_currency_is_explicit_and_not_silently_normalized

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373007+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_currency_is_explicit_and_not_silently_normalized](../tests/test_domain.py#L33), lines 33–36.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_currency_is_explicit_and_not_silently_normalized` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-8EEBAC8F — descriptive text cannot be silently treated as structured

**Test Case ID:** VC-8EEBAC8F

**Test Case Name:** MoneyAndContractTests.test_descriptive_text_cannot_be_silently_treated_as_structured

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373062+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_descriptive_text_cannot_be_silently_treated_as_structured](../tests/test_domain.py#L123), lines 123–127.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_descriptive_text_cannot_be_silently_treated_as_structured` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError); self.assertRaises(TypeError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-17EFDC65 — exact route requires typed identifier

**Test Case ID:** VC-17EFDC65

**Test Case Name:** MoneyAndContractTests.test_exact_route_requires_typed_identifier

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373088+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_exact_route_requires_typed_identifier](../tests/test_domain.py#L104), lines 104–110.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_exact_route_requires_typed_identifier` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError); self.assertRaises(TypeError); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-D38A886D — identity attributes and boolean fields are validated

**Test Case ID:** VC-D38A886D

**Test Case Name:** MoneyAndContractTests.test_identity_attributes_and_boolean_fields_are_validated

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373113+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_identity_attributes_and_boolean_fields_are_validated](../tests/test_domain.py#L72), lines 72–89.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_identity_attributes_and_boolean_fields_are_validated` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError); self.assertRaises((TypeError, ValueError))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-2A814D25 — money is nonnegative bounded integer

**Test Case ID:** VC-2A814D25

**Test Case Name:** MoneyAndContractTests.test_money_is_nonnegative_bounded_integer

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373202+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_money_is_nonnegative_bounded_integer](../tests/test_domain.py#L26), lines 26–31.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_money_is_nonnegative_bounded_integer` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(Money(0, 'INR').minor_units, 0); self.assertEqual(Money(MAX_MINOR_UNITS, 'INR').minor_units, MAX_MINOR_UNITS); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-33D0E44B — money rejects float bool and string

**Test Case ID:** VC-33D0E44B

**Test Case Name:** MoneyAndContractTests.test_money_rejects_float_bool_and_string

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373233+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_money_rejects_float_bool_and_string](../tests/test_domain.py#L21), lines 21–24.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_money_rejects_float_bool_and_string` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(TypeError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-B1B87370 — price operators have different boundary semantics

**Test Case ID:** VC-B1B87370

**Test Case Name:** MoneyAndContractTests.test_price_operators_have_different_boundary_semantics

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373270+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_price_operators_have_different_boundary_semantics](../tests/test_domain.py#L38), lines 38–42.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `amount = Money(200000, 'INR')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_price_operators_have_different_boundary_semantics` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(PriceLimit(amount, PriceOperator.LT).permits(amount)); self.assertTrue(PriceLimit(amount, PriceOperator.LTE).permits(amount)); self.assertFalse(PriceLimit(amount, PriceOperator.LTE).permits(Money(1, 'USD')))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-1224B819 — quantity must be positive integer

**Test Case ID:** VC-1224B819

**Test Case Name:** MoneyAndContractTests.test_quantity_must_be_positive_integer

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373289+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_quantity_must_be_positive_integer](../tests/test_domain.py#L57), lines 57–60.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_quantity_must_be_positive_integer` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises((TypeError, ValueError))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-10259DF3 — route mismatch and unsupported fields fail explicitly

**Test Case ID:** VC-10259DF3

**Test Case Name:** MoneyAndContractTests.test_route_mismatch_and_unsupported_fields_fail_explicitly

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373336+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_route_mismatch_and_unsupported_fields_fail_explicitly](../tests/test_domain.py#L112), lines 112–121.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_route_mismatch_and_unsupported_fields_fail_explicitly` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError); self.assertRaises(TypeError); self.assertRaises(TypeError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-3B1FF4BE — unknowns stay explicit and default freshness is unknown

**Test Case ID:** VC-3B1FF4BE

**Test Case Name:** MoneyAndContractTests.test_unknowns_stay_explicit_and_default_freshness_is_unknown

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373362+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_unknowns_stay_explicit_and_default_freshness_is_unknown](../tests/test_domain.py#L62), lines 62–70.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `item = variant(price=None, colour=None, available=None)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_unknowns_stay_explicit_and_default_freshness_is_unknown` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIsNone(item.price); self.assertIsNone(item.colour); self.assertIsNone(item.available); self.assertIs(type(item)(item.variant_id, item.product_id).price_freshness, Freshness.UNKNOWN)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-558C416D — untyped operator or money is rejected

**Test Case ID:** VC-558C416D

**Test Case Name:** MoneyAndContractTests.test_untyped_operator_or_money_is_rejected

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373382+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_untyped_operator_or_money_is_rejected](../tests/test_domain.py#L44), lines 44–48.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_untyped_operator_or_money_is_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(TypeError); self.assertRaises(TypeError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-A5D40722 — variant cannot be joined to wrong parent

**Test Case ID:** VC-A5D40722

**Test Case Name:** MoneyAndContractTests.test_variant_cannot_be_joined_to_wrong_parent

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373401+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_variant_cannot_be_joined_to_wrong_parent](../tests/test_domain.py#L100), lines 100–102.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_variant_cannot_be_joined_to_wrong_parent` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-ED8676EC — zero stock cannot be asserted available

**Test Case ID:** VC-ED8676EC

**Test Case Name:** MoneyAndContractTests.test_zero_stock_cannot_be_asserted_available

**System/Sub-system:** tests.test_domain

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373423+00:00

**Description:** Executable contract [tests.test_domain.MoneyAndContractTests.test_zero_stock_cannot_be_asserted_available](../tests/test_domain.py#L91), lines 91–93.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_domain.MoneyAndContractTests.test_zero_stock_cannot_be_asserted_available` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-740B10AC — browser node and static summaries preserve scope

**Test Case ID:** VC-740B10AC

**Test Case Name:** EvidenceIntegrityTests.test_browser_node_and_static_summaries_preserve_scope

**System/Sub-system:** tests.test_evidence_tools

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373451+00:00

**Description:** Executable contract [tests.test_evidence_tools.EvidenceIntegrityTests.test_browser_node_and_static_summaries_preserve_scope](../tests/test_evidence_tools.py#L26), lines 26–35.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = test_counts('  1 failed\n  7 passed (36.2s)\n')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_evidence_tools.EvidenceIntegrityTests.test_browser_node_and_static_summaries_preserve_scope` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual((result['executed'], result['passed'], result['failed']), (8, 7, 1)); self.assertIsNone(result['errored']); self.assertEqual(test_counts('ℹ tests 2\nℹ pass 1\nℹ fail 1\nℹ skipped 0\n')['failed'], 1); self.assertIsNone(test_counts('Success: no issues found in 30 source files'))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0003 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-843F64E4 — evidence write refuses overwrite and preserves original

**Test Case ID:** VC-843F64E4

**Test Case Name:** EvidenceIntegrityTests.test_evidence_write_refuses_overwrite_and_preserves_original

**System/Sub-system:** tests.test_evidence_tools

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.373802+00:00

**Description:** Executable contract [tests.test_evidence_tools.EvidenceIntegrityTests.test_evidence_write_refuses_overwrite_and_preserves_original](../tests/test_evidence_tools.py#L37), lines 37–44.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_evidence_tools.EvidenceIntegrityTests.test_evidence_write_refuses_overwrite_and_preserves_original` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(path.read_bytes(), original); self.assertRaises(FileExistsError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0004 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-81E8C2C6 — source wheel counts are executions with failure skip and error

**Test Case ID:** VC-81E8C2C6

**Test Case Name:** EvidenceIntegrityTests.test_source_wheel_counts_are_executions_with_failure_skip_and_error

**System/Sub-system:** tests.test_evidence_tools

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.374250+00:00

**Description:** Executable contract [tests.test_evidence_tools.EvidenceIntegrityTests.test_source_wheel_counts_are_executions_with_failure_skip_and_error](../tests/test_evidence_tools.py#L11), lines 11–24.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `output = 'Ran 5 tests in 1.0s\n\nFAILED (failures=1, errors=1, skipped=1)\nRan 5 tests in 1.1s\n\nOK\n'`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_evidence_tools.EvidenceIntegrityTests.test_source_wheel_counts_are_executions_with_failure_skip_and_error` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(test_counts(output), {'framework': 'unittest', 'scope': 'execution totals, not distinct methods across source/wheel runs', 'executed': 10, 'passed': 7, 'failed': 1, 'errored': 1, 'skipped': 1})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-5BD81C06 — duplicate database tenants rejected

**Test Case ID:** VC-5BD81C06

**Test Case Name:** HTTPFoundationTests.test_duplicate_database_tenants_rejected

**System/Sub-system:** tests.test_http_foundation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.376844+00:00

**Description:** Executable contract [tests.test_http_foundation.HTTPFoundationTests.test_duplicate_database_tenants_rejected](../tests/test_http_foundation.py#L109), lines 109–118.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `settings = Settings(os.environ['VOICECART_TEST_DSN'])`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_http_foundation.HTTPFoundationTests.test_duplicate_database_tenants_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0106 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-28AE125B — health origin host and no fake endpoints

**Test Case ID:** VC-28AE125B

**Test Case Name:** HTTPFoundationTests.test_health_origin_host_and_no_fake_endpoints

**System/Sub-system:** tests.test_http_foundation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.387425+00:00

**Description:** Executable contract [tests.test_http_foundation.HTTPFoundationTests.test_health_origin_host_and_no_fake_endpoints](../tests/test_http_foundation.py#L68), lines 68–107.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `settings = Settings(os.environ['VOICECART_TEST_DSN']); application = WebApplication({'local': Merchant(settings, hashlib.sha256(b'not-a-real-admin-key').hexdigest())}, b'x' * 32); server = Server(('127.0.0.1', 0), application)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_http_foundation.HTTPFoundationTests.test_health_origin_host_and_no_fake_endpoints` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(reply.status, 200); self.assertEqual(json.loads(reply.read())['status'], 'ok'); self.assertEqual(reply.status, 403); self.assertEqual(reply.status, 403)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5145 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-87E27F8C — capability equivalence tampering roles tenants and expiry

**Test Case ID:** VC-87E27F8C

**Test Case Name:** SecurityTests.test_capability_equivalence_tampering_roles_tenants_and_expiry

**System/Sub-system:** tests.test_http_foundation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.901968+00:00

**Description:** Executable contract [tests.test_http_foundation.SecurityTests.test_capability_equivalence_tampering_roles_tenants_and_expiry](../tests/test_http_foundation.py#L20), lines 20–37.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `auth = Capabilities(b'x' * 32); token = auth.issue('one', 'session', 'customer')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_http_foundation.SecurityTests.test_capability_equivalence_tampering_roles_tenants_and_expiry` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(auth.verify(token, 'one', 'customer'), 'session'); self.assertRaises(ValueError); self.assertRaises(AccessDenied)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0006 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-FDBCFE9D — rate limit boundaries and bounded storage

**Test Case ID:** VC-FDBCFE9D

**Test Case Name:** SecurityTests.test_rate_limit_boundaries_and_bounded_storage

**System/Sub-system:** tests.test_http_foundation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.902609+00:00

**Description:** Executable contract [tests.test_http_foundation.SecurityTests.test_rate_limit_boundaries_and_bounded_storage](../tests/test_http_foundation.py#L39), lines 39–46.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `rate = RateLimiter()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_http_foundation.SecurityTests.test_rate_limit_boundaries_and_bounded_storage` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(rate.allow(('test',), 1, now=0)); self.assertFalse(rate.allow(('test',), 1, now=59.999)); self.assertTrue(rate.allow(('test',), 1, now=60)); self.assertLessEqual(len(rate.windows), 4096)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0091 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-DFC606F8 — trusted service hosts are explicit and not default

**Test Case ID:** VC-DFC606F8

**Test Case Name:** SecurityTests.test_trusted_service_hosts_are_explicit_and_not_default

**System/Sub-system:** tests.test_http_foundation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.911764+00:00

**Description:** Executable contract [tests.test_http_foundation.SecurityTests.test_trusted_service_hosts_are_explicit_and_not_default](../tests/test_http_foundation.py#L48), lines 48–59.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_http_foundation.SecurityTests.test_trusted_service_hosts_are_explicit_and_not_default` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError); self.assertEqual(parse_local_dsn('postgresql://db/test')['host'], 'db'); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0121 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-134D7A45 — adapter exact snapshot add replay refresh and operation

**Test Case ID:** VC-134D7A45

**Test Case Name:** MerchantTests.test_adapter_exact_snapshot_add_replay_refresh_and_operation

**System/Sub-system:** tests.test_merchant

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.929472+00:00

**Description:** Executable contract [tests.test_merchant.MerchantTests.test_adapter_exact_snapshot_add_replay_refresh_and_operation](../tests/test_merchant.py#L43), lines 43–61.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `app = ShoppingApplication(self.database, None); adapter = LocalMerchantAdapter(app); session = app.sessions.create()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_merchant.MerchantTests.test_adapter_exact_snapshot_add_replay_refresh_and_operation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(first, second); self.assertEqual(adapter.cart(session)['items'][0]['quantity'], 1); self.assertEqual(adapter.operation(session, operation)['status'], 'committed'); self.assertEqual(adapter.lookup('p-best')['revision'], 'fixture-1'); self.assertEqual(adapter.refresh_offers(['v-best'])[0]['offer']['price']['minor_units'], 150000); self.assertEqual(adapter.operation(session, str(uuid.uuid4()))['status'], 'unknown')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0692 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-7390048B — real tenant database auth session and catalogue isolation

**Test Case ID:** VC-7390048B

**Test Case Name:** MerchantTests.test_real_tenant_database_auth_session_and_catalogue_isolation

**System/Sub-system:** tests.test_merchant

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:16.998658+00:00

**Description:** Executable contract [tests.test_merchant.MerchantTests.test_real_tenant_database_auth_session_and_catalogue_isolation](../tests/test_merchant.py#L63), lines 63–131.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_merchant.MerchantTests.test_real_tenant_database_auth_session_and_catalogue_isolation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(request('two', 'sessions', {}, TOKEN)[0], 403); self.assertEqual(status, 201); self.assertEqual(request('two', 'cart', {'session_id': result['session_id']}, second_token)[0], 409); self.assertEqual(request('two', 'lookup', {'product_id': 'p-best'}, second_token)[1]['product']['name'], 'Other tenant test-only product'); self.assertEqual(request('one', 'lookup', {'product_id': 'p-best'}, TOKEN)[1]['product']['name'], 'College backpack')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.8431 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-A7946435 — action evidence cannot be a substring of address

**Test Case ID:** VC-A7946435

**Test Case Name:** InterpretationTests.test_action_evidence_cannot_be_a_substring_of_address

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.841819+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_action_evidence_cannot_be_a_substring_of_address](../tests/test_nlu.py#L176), lines 176–185.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = extraction(intent='add', query=None, category=None, add_evidence='add', identifier={'kind': 'sku', 'value': 'SKU-BEST', 'evidence': 'SKU-BEST'})`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_action_evidence_cannot_be_a_substring_of_address` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-D46EA7FC — bool extra keys and fabricated evidence are rejected

**Test Case ID:** VC-D46EA7FC

**Test Case Name:** InterpretationTests.test_bool_extra_keys_and_fabricated_evidence_are_rejected

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.841906+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_bool_extra_keys_and_fabricated_evidence_are_rejected](../tests/test_nlu.py#L121), lines 121–129.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_bool_extra_keys_and_fabricated_evidence_are_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-D8133ED0 — control requests are narrow and do not reuse search state

**Test Case ID:** VC-D8133ED0

**Test Case Name:** InterpretationTests.test_control_requests_are_narrow_and_do_not_reuse_search_state

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.842061+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_control_requests_are_narrow_and_do_not_reuse_search_state](../tests/test_nlu.py#L196), lines 196–203.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = validate_interpretation(extraction(intent='cancel'), 'cancel', VOCAB)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_control_requests_are_narrow_and_do_not_reuse_search_state` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.kind, 'cancel'); self.assertIsNone(result.search); self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-0E87D467 — critical field loss and operator drift are rejected

**Test Case ID:** VC-0E87D467

**Test Case Name:** InterpretationTests.test_critical_field_loss_and_operator_drift_are_rejected

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.842109+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_critical_field_loss_and_operator_drift_are_rejected](../tests/test_nlu.py#L92), lines 92–106.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `price = {'amount': '2000', 'operator': 'lt', 'evidence': 'under 2000'}`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_critical_field_loss_and_operator_drift_are_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(InterpretationError); self.assertRaises(InterpretationError); self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0003 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-ADFA528D — exact identifier and ordinal require literal evidence

**Test Case ID:** VC-ADFA528D

**Test Case Name:** InterpretationTests.test_exact_identifier_and_ordinal_require_literal_evidence

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.842368+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_exact_identifier_and_ordinal_require_literal_evidence](../tests/test_nlu.py#L148), lines 148–174.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = extraction(intent='add', query=None, category=None, add_evidence='add', identifier={'kind': 'sku', 'value': 'SKU-BLK-101', 'evidence': 'SKU-BLK-101'}); result = validate_interpretation(raw, 'add SKU-BLK-101', VOCAB); raw['identifier']['value'] = 'SKU-BLK-10'`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_exact_identifier_and_ordinal_require_literal_evidence` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.search.identifier.value, 'SKU-BLK-101'); self.assertEqual(result.ordinal, 2); self.assertIsNone(result.search); self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-56E9B744 — integer money and strict inclusive bounds

**Test Case ID:** VC-56E9B744

**Test Case Name:** InterpretationTests.test_integer_money_and_strict_inclusive_bounds

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.842605+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_integer_money_and_strict_inclusive_bounds](../tests/test_nlu.py#L58), lines 58–90.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_integer_money_and_strict_inclusive_bounds` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(rupees_to_minor('1,50,000.25'), 15000025); self.assertEqual(result.search.constraints.price_limit.amount.minor_units, 200000); self.assertEqual(result.search.constraints.price_limit.operator, PriceOperator(operator)); self.assertRaises((ValueError, TypeError))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0003 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-0BDE75C3 — negation cannot authorize add or invert colour

**Test Case ID:** VC-0BDE75C3

**Test Case Name:** InterpretationTests.test_negation_cannot_authorize_add_or_invert_colour

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.842931+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_negation_cannot_authorize_add_or_invert_colour](../tests/test_nlu.py#L108), lines 108–119.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = extraction(intent='search_and_add', add_evidence='add'); raw = extraction(colour={'value': 'blue', 'evidence': 'blue'})`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_negation_cannot_authorize_add_or_invert_colour` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(InterpretationError); self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-1055E006 — quantity and total budget semantics

**Test Case ID:** VC-1055E006

**Test Case Name:** InterpretationTests.test_quantity_and_total_budget_semantics

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.843018+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_quantity_and_total_budget_semantics](../tests/test_nlu.py#L131), lines 131–146.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = extraction(intent='search_and_add', add_evidence='add', quantity={'value': 2, 'evidence': 'two'}, price={'amount': '100.01', 'operator': 'lt', 'evidence': 'under 100.01'}); result = validate_interpretation(raw, 'add two backpack under 100.01 total', VOCAB); raw['quantity'] = None`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_quantity_and_total_budget_semantics` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.search.constraints.price_limit.amount.minor_units, 5001); self.assertRaises(InterpretationError); self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-5FD3A9F9 — structured and discovery scopes remain distinct

**Test Case ID:** VC-5FD3A9F9

**Test Case Name:** InterpretationTests.test_structured_and_discovery_scopes_remain_distinct

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.843254+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_structured_and_discovery_scopes_remain_distinct](../tests/test_nlu.py#L44), lines 44–56.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = validate_interpretation(extraction(), 'find backpack', VOCAB); result = validate_interpretation(extraction(query='backpack for college'), 'find backpack for college', VOCAB); result = validate_interpretation(extraction(), 'find waterproof backpack', VOCAB)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_structured_and_discovery_scopes_remain_distinct` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.search.route, RetrievalRoute.STRUCTURED); self.assertEqual(result.search.route, RetrievalRoute.DISCOVERY); self.assertEqual(result.search.route, RetrievalRoute.DISCOVERY); self.assertIn('waterproof', result.search.semantic_query)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-9BB9DA4B — unknown currency and ambiguous bounds need clarification

**Test Case ID:** VC-9BB9DA4B

**Test Case Name:** InterpretationTests.test_unknown_currency_and_ambiguous_bounds_need_clarification

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.843398+00:00

**Description:** Executable contract [tests.test_nlu.InterpretationTests.test_unknown_currency_and_ambiguous_bounds_need_clarification](../tests/test_nlu.py#L187), lines 187–194.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.InterpretationTests.test_unknown_currency_and_ambiguous_bounds_need_clarification` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-17785A51 — evidence enums are independent and base schema is unchanged

**Test Case ID:** VC-17785A51

**Test Case Name:** LiteralSchemaTests.test_evidence_enums_are_independent_and_base_schema_is_unchanged

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.843495+00:00

**Description:** Executable contract [tests.test_nlu.LiteralSchemaTests.test_evidence_enums_are_independent_and_base_schema_is_unchanged](../tests/test_nlu.py#L335), lines 335–351.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `schema = extraction_schema('red bags under 1,000 rupees', {'category': {'bags': 'bag'}, 'colour': {'red': 'red'}}); fields = schema['properties']`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.LiteralSchemaTests.test_evidence_enums_are_independent_and_base_schema_is_unchanged` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(fields['category']['properties']['evidence']['enum'], ['bags']); self.assertEqual(fields['category']['properties']['value']['enum'], ['bag']); self.assertEqual(fields['price']['anyOf'][0]['properties']['amount']['enum'], ['1,000']); self.assertNotIn('enum', SCHEMA['properties']['category']['anyOf'][0]['properties']['evidence'])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-31A5BE09 — external url credentials paths and nonfinite timeouts rejected

**Test Case ID:** VC-31A5BE09

**Test Case Name:** LocalTransportTests.test_external_url_credentials_paths_and_nonfinite_timeouts_rejected

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.843689+00:00

**Description:** Executable contract [tests.test_nlu.LocalTransportTests.test_external_url_credentials_paths_and_nonfinite_timeouts_rejected](../tests/test_nlu.py#L207), lines 207–221.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.LocalTransportTests.test_external_url_credentials_paths_and_nonfinite_timeouts_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError); self.assertRaises(ValueError); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-54B07EF0 — actual transport schema and independent validation

**Test Case ID:** VC-54B07EF0

**Test Case Name:** OllamaProtocolIntegrationTests.test_actual_transport_schema_and_independent_validation

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.849868+00:00

**Description:** Executable contract [tests.test_nlu.OllamaProtocolIntegrationTests.test_actual_transport_schema_and_independent_validation](../tests/test_nlu.py#L270), lines 270–275.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `interpreter = OllamaInterpreter(self.client, 'fixture-model', 'a' * 64)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.OllamaProtocolIntegrationTests.test_actual_transport_schema_and_independent_validation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(interpreter.interpret('find backpack', VOCAB).kind, 'search'); self.assertFalse(self.server.payload['stream']); self.assertFalse(self.server.payload['format']['additionalProperties']); self.assertEqual(self.server.payload['options']['num_predict'], 768)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0019 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-A5993DBB — embedding http shape and generation are checked

**Test Case ID:** VC-A5993DBB

**Test Case Name:** OllamaProtocolIntegrationTests.test_embedding_http_shape_and_generation_are_checked

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.851768+00:00

**Description:** Executable contract [tests.test_nlu.OllamaProtocolIntegrationTests.test_embedding_http_shape_and_generation_are_checked](../tests/test_nlu.py#L277), lines 277–287.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.server.result = {'embeddings': [[3, 4]]}; spec = EncoderSpec('fixture-model', 'a' * 64, 2); encoder = OllamaEncoder(self.client, spec)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.OllamaProtocolIntegrationTests.test_embedding_http_shape_and_generation_are_checked` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(encoder.encode(['college backpack']), [(0.6, 0.8)]); self.assertFalse(self.server.payload['truncate']); self.assertRaises(LocalServiceError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0016 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-755057D9 — explicit metadata encoder prefix preserves small token budget

**Test Case ID:** VC-755057D9

**Test Case Name:** OllamaProtocolIntegrationTests.test_explicit_metadata_encoder_prefix_preserves_small_token_budget

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.853411+00:00

**Description:** Executable contract [tests.test_nlu.OllamaProtocolIntegrationTests.test_explicit_metadata_encoder_prefix_preserves_small_token_budget](../tests/test_nlu.py#L289), lines 289–304.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `self.server.result = {'embeddings': [[3, 4]]}; encoder = OllamaEncoder(self.client, EncoderSpec('fixture-model', 'a' * 64, 2, serializer='metadata-prefix-256utf8bytes-v1'))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.OllamaProtocolIntegrationTests.test_explicit_metadata_encoder_prefix_preserves_small_token_budget` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertLessEqual(len(self.server.payload['input'][0].encode()), 256); self.assertFalse(self.server.payload['truncate'])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0007 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-B9094970 — malformed model json and extra fields never returns plan

**Test Case ID:** VC-B9094970

**Test Case Name:** OllamaProtocolIntegrationTests.test_malformed_model_json_and_extra_fields_never_returns_plan

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.854095+00:00

**Description:** Executable contract [tests.test_nlu.OllamaProtocolIntegrationTests.test_malformed_model_json_and_extra_fields_never_returns_plan](../tests/test_nlu.py#L321), lines 321–331.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.OllamaProtocolIntegrationTests.test_malformed_model_json_and_extra_fields_never_returns_plan` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0033 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C6424352 — wrong digest or truncated generation never returns plan

**Test Case ID:** VC-C6424352

**Test Case Name:** OllamaProtocolIntegrationTests.test_wrong_digest_or_truncated_generation_never_returns_plan

**System/Sub-system:** tests.test_nlu

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:17.857443+00:00

**Description:** Executable contract [tests.test_nlu.OllamaProtocolIntegrationTests.test_wrong_digest_or_truncated_generation_never_returns_plan](../tests/test_nlu.py#L306), lines 306–319.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu.OllamaProtocolIntegrationTests.test_wrong_digest_or_truncated_generation_never_returns_plan` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(LocalServiceError); self.assertRaises(LocalServiceError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0024 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-3CEA6B1E — false action proposal is counted without dispatch

**Test Case ID:** VC-3CEA6B1E

**Test Case Name:** EvaluationIntegrityTests.test_false_action_proposal_is_counted_without_dispatch

**System/Sub-system:** tests.test_nlu_evaluation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.361006+00:00

**Description:** Executable contract [tests.test_nlu_evaluation.EvaluationIntegrityTests.test_false_action_proposal_is_counted_without_dispatch](../tests/test_nlu_evaluation.py#L33), lines 33–48.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `interpreter = Mock(); interpreter.interpret.return_value = Intent('add', explicit_add=True); row = evaluate({'id': 'TEST-ACTION', 'text': 'find only', 'expected': {'kind': 'search'}, 'action_allowed': False}, interpreter)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu_evaluation.EvaluationIntegrityTests.test_false_action_proposal_is_counted_without_dispatch` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(metrics['false_action_authorization_count'], 1); self.assertEqual(metrics['false_action_authorization_rate'], 1); self.assertEqual(metrics['exact_expectation_matches'], 0)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0005 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-71839C2B — frozen bank ids unique and explicit action labels

**Test Case ID:** VC-71839C2B

**Test Case Name:** EvaluationIntegrityTests.test_frozen_bank_ids_unique_and_explicit_action_labels

**System/Sub-system:** tests.test_nlu_evaluation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.361517+00:00

**Description:** Executable contract [tests.test_nlu_evaluation.EvaluationIntegrityTests.test_frozen_bank_ids_unique_and_explicit_action_labels](../tests/test_nlu_evaluation.py#L91), lines 91–101.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `bank = json.loads(Path(__file__).with_name('nlu_eval_v2.json').read_text())['cases']`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu_evaluation.EvaluationIntegrityTests.test_frozen_bank_ids_unique_and_explicit_action_labels` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(len({r['id'] for r in bank}), len(bank)); self.assertTrue(all((type(r['action_allowed']) is bool and r['expected'] for r in bank)))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0005 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-486B3A35 — malformed shape and unsafe action outputs are independently rejected

**Test Case ID:** VC-486B3A35

**Test Case Name:** EvaluationIntegrityTests.test_malformed_shape_and_unsafe_action_outputs_are_independently_rejected

**System/Sub-system:** tests.test_nlu_evaluation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.362075+00:00

**Description:** Executable contract [tests.test_nlu_evaluation.EvaluationIntegrityTests.test_malformed_shape_and_unsafe_action_outputs_are_independently_rejected](../tests/test_nlu_evaluation.py#L81), lines 81–89.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu_evaluation.EvaluationIntegrityTests.test_malformed_shape_and_unsafe_action_outputs_are_independently_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0004 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-E2FB2BD4 — reject label distinguishes validation service and unknown errors

**Test Case ID:** VC-E2FB2BD4

**Test Case Name:** EvaluationIntegrityTests.test_reject_label_distinguishes_validation_service_and_unknown_errors

**System/Sub-system:** tests.test_nlu_evaluation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.362459+00:00

**Description:** Executable contract [tests.test_nlu_evaluation.EvaluationIntegrityTests.test_reject_label_distinguishes_validation_service_and_unknown_errors](../tests/test_nlu_evaluation.py#L13), lines 13–31.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `case = {'id': 'TEST-EVAL', 'text': 'unsupported', 'expected': {'reject': True}, 'action_allowed': False}`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu_evaluation.EvaluationIntegrityTests.test_reject_label_distinguishes_validation_service_and_unknown_errors` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(row['correct'], correct); self.assertEqual(row['outcome'], outcome)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0007 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-78ECE943 — slot micro counts missing wrong extra and correct

**Test Case ID:** VC-78ECE943

**Test Case Name:** EvaluationIntegrityTests.test_slot_micro_counts_missing_wrong_extra_and_correct

**System/Sub-system:** tests.test_nlu_evaluation

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.363193+00:00

**Description:** Executable contract [tests.test_nlu_evaluation.EvaluationIntegrityTests.test_slot_micro_counts_missing_wrong_extra_and_correct](../tests/test_nlu_evaluation.py#L50), lines 50–79.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `metrics = summarize([{'expected': {'kind': 'search', 'category': 'backpack', 'colour': 'blue', 'size': 'medium', 'ordinal': None}, 'observed': {'kind': 'search', 'category': 'backpack', 'colour': 'black', 'ordinal': 2}, 'outcome': 'accepted', 'correct': False, 'action_allowed': False, 'false_action_authorization': False, 'seconds': 1}])`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_nlu_evaluation.EvaluationIntegrityTests.test_slot_micro_counts_missing_wrong_extra_and_correct` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual((metrics['slot_tp'], metrics['slot_fp'], metrics['slot_fn']), (1, 2, 2)); self.assertAlmostEqual(metrics['slot_micro_f1'], 1 / 3); self.assertIsNone(metrics['p95_seconds'])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-135B5AE4 — complete valid fixture and unknown values remain explicit

**Test Case ID:** VC-135B5AE4

**Test Case Name:** ImportValidationTests.test_complete_valid_fixture_and_unknown_values_remain_explicit

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.363420+00:00

**Description:** Executable contract [tests.test_persistence.ImportValidationTests.test_complete_valid_fixture_and_unknown_values_remain_explicit](../tests/test_persistence.py#L24), lines 24–30.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = fabricated_document(); raw['variants'][0]['price'] = None; raw['variants'][0]['available'] = None`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.ImportValidationTests.test_complete_valid_fixture_and_unknown_values_remain_explicit` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIsNone(bundle.variants[0].price); self.assertIsNone(bundle.variants[0].available)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0003 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-346DABC1 — database config cannot redirect to remote hosts

**Test Case ID:** VC-346DABC1

**Test Case Name:** ImportValidationTests.test_database_config_cannot_redirect_to_remote_hosts

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.363762+00:00

**Description:** Executable contract [tests.test_persistence.ImportValidationTests.test_database_config_cannot_redirect_to_remote_hosts](../tests/test_persistence.py#L53), lines 53–60.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.ImportValidationTests.test_database_config_cannot_redirect_to_remote_hosts` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0004 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-57F641AC — reject duplicate ids skus bad prices orphans and unknown fields

**Test Case ID:** VC-57F641AC

**Test Case Name:** ImportValidationTests.test_reject_duplicate_ids_skus_bad_prices_orphans_and_unknown_fields

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.364218+00:00

**Description:** Executable contract [tests.test_persistence.ImportValidationTests.test_reject_duplicate_ids_skus_bad_prices_orphans_and_unknown_fields](../tests/test_persistence.py#L32), lines 32–45.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `changes = (lambda d: d['products'].append(d['products'][0]), lambda d: d['variants'][1].update(sku='SKU-BEST'), lambda d: d['variants'][0]['price'].update(minor_units=True), lambda d: d['variants'][0].update(product_id='missing'), lambda d: d.update(sample_data=True), lambda d: d.update(valid_until='2000-01-01T00:00:00Z'))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.ImportValidationTests.test_reject_duplicate_ids_skus_bad_prices_orphans_and_unknown_fields` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(ImportValidationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0006 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-B76A2858 — vector dimension nonfinite zero and mixed types rejected

**Test Case ID:** VC-B76A2858

**Test Case Name:** ImportValidationTests.test_vector_dimension_nonfinite_zero_and_mixed_types_rejected

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.364828+00:00

**Description:** Executable contract [tests.test_persistence.ImportValidationTests.test_vector_dimension_nonfinite_zero_and_mixed_types_rejected](../tests/test_persistence.py#L47), lines 47–51.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.ImportValidationTests.test_vector_dimension_nonfinite_zero_and_mixed_types_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(validate_vector([3, 4], 2), (0.6, 0.8)); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-1874CEEA — empty import can only assert its declared source

**Test Case ID:** VC-1874CEEA

**Test Case Name:** PostgreSQLIntegrationTests.test_empty_import_can_only_assert_its_declared_source

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.370427+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_empty_import_can_only_assert_its_declared_source](../tests/test_persistence.py#L308), lines 308–319.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = fabricated_document(); raw['products'], raw['variants'] = ([], []); state = self.database.inspect()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_empty_import_can_only_assert_its_declared_source` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(state['populated']); self.assertEqual(state['product_count'], 0); self.assertTrue(result.can_claim_no_match); self.assertEqual(self.database.snapshot().catalogue.coverage, Coverage.COMPLETE)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0300 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-65F9C232 — expired source and unknown prices block action claims

**Test Case ID:** VC-65F9C232

**Test Case Name:** PostgreSQLIntegrationTests.test_expired_source_and_unknown_prices_block_action_claims

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.400411+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_expired_source_and_unknown_prices_block_action_claims](../tests/test_persistence.py#L208), lines 208–217.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = PostgresCatalogue(self.database).search(SearchRequest(HardConstraints('INR', category='backpack')))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_expired_source_and_unknown_prices_block_action_claims` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.matches, ()); self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertFalse(result.can_claim_catalogue_minimum)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0212 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C52F5CA6 — failed publication rolls back every branch

**Test Case ID:** VC-C52F5CA6

**Test Case Name:** PostgreSQLIntegrationTests.test_failed_publication_rolls_back_every_branch

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.421647+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_failed_publication_rolls_back_every_branch](../tests/test_persistence.py#L175), lines 175–184.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `bundle = parse_import(fabricated_document('fixture-2', 'fixture-1')); broken = replace(bundle, aliases={'invalid': object()}); state = self.database.inspect()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_failed_publication_rolls_back_every_branch` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(state['revision'], 'fixture-1'); self.assertEqual(state['product_count'], 3); self.assertEqual(state['search_count'], 3); self.assertRaises(TypeError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0246 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-BD29F7DF — full replace and stale job compare and set

**Test Case ID:** VC-BD29F7DF

**Test Case Name:** PostgreSQLIntegrationTests.test_full_replace_and_stale_job_compare_and_set

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.446263+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_full_replace_and_stale_job_compare_and_set](../tests/test_persistence.py#L162), lines 162–173.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = fabricated_document('fixture-2', 'fixture-1'); raw['variants'] = raw['variants'][:1]; raw['products'] = raw['products'][:1]`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_full_replace_and_stale_job_compare_and_set` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(state['variant_count'], 1); self.assertEqual(state['search_count'], 1); self.assertEqual(state['revision'], 'fixture-2'); self.assertRaises(PublicationConflict)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0222 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-6479306E — migrations idempotent empty and startup inserts no products

**Test Case ID:** VC-6479306E

**Test Case Name:** PostgreSQLIntegrationTests.test_migrations_idempotent_empty_and_startup_inserts_no_products

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.468468+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_migrations_idempotent_empty_and_startup_inserts_no_products](../tests/test_persistence.py#L95), lines 95–107.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `state = self.database.inspect(); result = PostgresCatalogue(self.database).search(SearchRequest(HardConstraints('INR')))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_migrations_idempotent_empty_and_startup_inserts_no_products` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.database.migrate(), []); self.assertEqual(state['product_count'], 0); self.assertEqual(state['variant_count'], 0); self.assertFalse(state['populated']); self.assertEqual(result.status, SearchStatus.INCOMPLETE); self.assertFalse(result.can_claim_no_match); self.assertEqual(self.database.inspect()['product_count'], 0)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0201 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-D62A807E — parallel publishers cannot overwrite each other

**Test Case ID:** VC-D62A807E

**Test Case Name:** PostgreSQLIntegrationTests.test_parallel_publishers_cannot_overwrite_each_other

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.488561+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_parallel_publishers_cannot_overwrite_each_other](../tests/test_persistence.py#L196), lines 196–206.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_parallel_publishers_cannot_overwrite_each_other` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(results.count('conflict'), 1); self.assertIn(self.database.inspect()['revision'], ('writer-a', 'writer-b'))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0151 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-0ED86245 — price aware winner outside text top k gets its real dense feature

**Test Case ID:** VC-0ED86245

**Test Case Name:** PostgreSQLIntegrationTests.test_price_aware_winner_outside_text_top_k_gets_its_real_dense_feature

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.503707+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_price_aware_winner_outside_text_top_k_gets_its_real_dense_feature](../tests/test_persistence.py#L236), lines 236–295.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `raw = fabricated_document(); raw['products'], raw['variants'] = ([], []); encoder = ExhaustiveFixtureEncoder()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_price_aware_winner_outside_text_top_k_gets_its_real_dense_feature` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.overall_match.variant.variant_id, 'fixture-60'); self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, 'fixture-61'); self.assertFalse(result.can_claim_catalogue_minimum)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0231 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-7C222392 — readiness rejects missing current migration marker

**Test Case ID:** VC-7C222392

**Test Case Name:** PostgreSQLIntegrationTests.test_readiness_rejects_missing_current_migration_marker

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.526797+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_readiness_rejects_missing_current_migration_marker](../tests/test_persistence.py#L144), lines 144–160.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_readiness_rejects_missing_current_migration_marker` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(DatabaseUnavailable)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0152 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-4E02E228 — real pgvector lexical price roles and hard constraints

**Test Case ID:** VC-4E02E228

**Test Case Name:** PostgreSQLIntegrationTests.test_real_pgvector_lexical_price_roles_and_hard_constraints

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.542031+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_real_pgvector_lexical_price_roles_and_hard_constraints](../tests/test_persistence.py#L219), lines 219–234.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `catalogue = PostgresCatalogue(self.database, FixtureEncoder()); request = SearchRequest(HardConstraints('INR', category='backpack', colour='black'), RetrievalRoute.DISCOVERY, semantic_query='college backpack'); result = catalogue.search(request)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_real_pgvector_lexical_price_roles_and_hard_constraints` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.overall_match.variant.variant_id, 'v-best'); self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, 'v-cheap'); self.assertNotIn('v-accessory', {item.variant.variant_id for item in result.matches}); self.assertFalse(result.can_claim_catalogue_minimum); self.assertEqual(result.status, SearchStatus.INCOMPLETE)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0152 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-3D76F469 — real publication exact structured and cheapest oracle

**Test Case ID:** VC-3D76F469

**Test Case Name:** PostgreSQLIntegrationTests.test_real_publication_exact_structured_and_cheapest_oracle

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.557280+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_real_publication_exact_structured_and_cheapest_oracle](../tests/test_persistence.py#L109), lines 109–132.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `catalogue = PostgresCatalogue(self.database); request = SearchRequest(HardConstraints('INR', category='backpack', colour='black')); result = catalogue.search(request)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_real_publication_exact_structured_and_cheapest_oracle` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual({item.variant.variant_id for item in result.matches}, {'v-best', 'v-cheap'}); self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, 'v-cheap'); self.assertTrue(result.can_claim_catalogue_minimum); self.assertEqual(catalogue.lookup(ExactIdentifier(IdentifierKind.SKU, 'SKU-BEST'))[0].variant.variant_id, 'v-best'); self.assertEqual(catalogue.lookup(ExactIdentifier(IdentifierKind.SKU, 'sku-best')), ()); self.assertEqual(self.database.vocabulary()['category']['backpacks'], 'backpack')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0218 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-46C60290 — repeatable read does not mix old and new publication

**Test Case ID:** VC-46C60290

**Test Case Name:** PostgreSQLIntegrationTests.test_repeatable_read_does_not_mix_old_and_new_publication

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.579056+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_repeatable_read_does_not_mix_old_and_new_publication](../tests/test_persistence.py#L186), lines 186–194.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_repeatable_read_does_not_mix_old_and_new_publication` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.database.snapshot().state['revision'], 'fixture-2'); self.assertEqual(old.state['revision'], after.state['revision'])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0215 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-B0D6D8C8 — unconfigured or mismatched semantics is not silent no match

**Test Case ID:** VC-B0D6D8C8

**Test Case Name:** PostgreSQLIntegrationTests.test_unconfigured_or_mismatched_semantics_is_not_silent_no_match

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.600595+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_unconfigured_or_mismatched_semantics_is_not_silent_no_match](../tests/test_persistence.py#L297), lines 297–306.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `request = SearchRequest(HardConstraints('INR', category='backpack'), RetrievalRoute.DISCOVERY, semantic_query='college backpack'); result = PostgresCatalogue(self.database, FixtureEncoder()).search(request)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_unconfigured_or_mismatched_semantics_is_not_silent_no_match` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(result.can_claim_no_match); self.assertTrue(any(('generation' in issue.detail for issue in result.issues)))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0190 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-E4D3870A — vocabulary cache copies and publication invalidation

**Test Case ID:** VC-E4D3870A

**Test Case Name:** PostgreSQLIntegrationTests.test_vocabulary_cache_copies_and_publication_invalidation

**System/Sub-system:** tests.test_persistence

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.619576+00:00

**Description:** Executable contract [tests.test_persistence.PostgreSQLIntegrationTests.test_vocabulary_cache_copies_and_publication_invalidation](../tests/test_persistence.py#L134), lines 134–142.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `first = self.database.vocabulary(); first['category']['injected'] = 'wrong'; raw = fabricated_document('fixture-2', 'fixture-1')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_persistence.PostgreSQLIntegrationTests.test_vocabulary_cache_copies_and_publication_invalidation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertNotIn('injected', self.database.vocabulary()['category']); self.assertIn('new-category', self.database.vocabulary()['category'])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0230 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-EF8796DC — amount parser and number loop feasible inputs

**Test Case ID:** VC-EF8796DC

**Test Case Name:** PracticalContracts.test_amount_parser_and_number_loop_feasible_inputs

**System/Sub-system:** tests.test_practical_contracts

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.642553+00:00

**Description:** Executable contract [tests.test_practical_contracts.PracticalContracts.test_amount_parser_and_number_loop_feasible_inputs](../tests/test_practical_contracts.py#L75), lines 75–101.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_practical_contracts.PracticalContracts.test_amount_parser_and_number_loop_feasible_inputs` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(whole_number(text), expected); self.assertEqual(rupees_to_minor(text), expected); self.assertRaises((InterpretationError, ValueError)); self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-42F571AF — eligibility decision table rejected dominates unknown

**Test Case ID:** VC-42F571AF

**Test Case Name:** PracticalContracts.test_eligibility_decision_table_rejected_dominates_unknown

**System/Sub-system:** tests.test_practical_contracts

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.642734+00:00

**Description:** Executable contract [tests.test_practical_contracts.PracticalContracts.test_eligibility_decision_table_rejected_dominates_unknown](../tests/test_practical_contracts.py#L39), lines 39–68.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `rows = [({}, {}, Eligibility.QUALIFIED), ({'active': False}, {}, Eligibility.REJECTED), ({}, {'colour': 'blue'}, Eligibility.REJECTED), ({}, {'price': 10001}, Eligibility.REJECTED), ({}, {'available': False}, Eligibility.REJECTED), ({}, {'available': None}, Eligibility.UNKNOWN), ({}, {'price': None}, Eligibility.UNKNOWN), ({'active': False}, {'price': None}, Eligibility.REJECTED)]; constraint = HardConstraints('INR', colour='black', price_limit=PriceLimit(Money(10000, 'INR'), PriceOperator.LTE))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_practical_contracts.PracticalContracts.test_eligibility_decision_table_rejected_dominates_unknown` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIs(qualify(CatalogueItem(product(), replace(variant(price=None), colour='blue')), constraint).state, Eligibility.REJECTED); self.assertIs(qualify(item, constraint).state, state)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-42772094 — money text three feasible return paths

**Test Case ID:** VC-42772094

**Test Case Name:** PracticalContracts.test_money_text_three_feasible_return_paths

**System/Sub-system:** tests.test_practical_contracts

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.642879+00:00

**Description:** Executable contract [tests.test_practical_contracts.PracticalContracts.test_money_text_three_feasible_return_paths](../tests/test_practical_contracts.py#L70), lines 70–73.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_practical_contracts.PracticalContracts.test_money_text_three_feasible_return_paths` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(money_text(100, 'INR'), '1 rupees'); self.assertEqual(money_text(101, 'INR'), '1 rupees and 1 paise'); self.assertEqual(money_text(100, 'USD'), '100 minor units USD')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-13F123AA — price equivalence partitions and strict inclusive boundaries

**Test Case ID:** VC-13F123AA

**Test Case Name:** PracticalContracts.test_price_equivalence_partitions_and_strict_inclusive_boundaries

**System/Sub-system:** tests.test_practical_contracts

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.642903+00:00

**Description:** Executable contract [tests.test_practical_contracts.PracticalContracts.test_price_equivalence_partitions_and_strict_inclusive_boundaries](../tests/test_practical_contracts.py#L21), lines 21–37.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `item = CatalogueItem(product(), variant(price=None))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_practical_contracts.PracticalContracts.test_price_equivalence_partitions_and_strict_inclusive_boundaries` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIs(qualify(item, HardConstraints('INR')).state, Eligibility.UNKNOWN); self.assertRaises((ValueError, TypeError)); self.assertEqual(limit.permits(Money(price, 'INR')), accepted)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-6EC43B06 — absent ranking policy does not invent overall relevance

**Test Case ID:** VC-6EC43B06

**Test Case Name:** RankingBoundaryTests.test_absent_ranking_policy_does_not_invent_overall_relevance

**System/Sub-system:** tests.test_ranking

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.642996+00:00

**Description:** Executable contract [tests.test_ranking.RankingBoundaryTests.test_absent_ranking_policy_does_not_invent_overall_relevance](../tests/test_ranking.py#L52), lines 52–57.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = self.db.search(request())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_ranking.RankingBoundaryTests.test_absent_ranking_policy_does_not_invent_overall_relevance` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIsNone(result.overall_match); self.assertIsNone(result.ranking_policy_version); self.assertEqual(result.ranked_matches, ()); self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, 'cheap')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-A8CA8105 — only hard qualified records reach ranking

**Test Case ID:** VC-A8CA8105

**Test Case Name:** RankingBoundaryTests.test_only_hard_qualified_records_reach_ranking

**System/Sub-system:** tests.test_ranking

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.643073+00:00

**Description:** Executable contract [tests.test_ranking.RankingBoundaryTests.test_only_hard_qualified_records_reach_ranking](../tests/test_ranking.py#L47), lines 47–50.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `policy = FixtureOrder(('better-fit', 'cheap'))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_ranking.RankingBoundaryTests.test_only_hard_qualified_records_reach_ranking` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(set(policy.seen), {'cheap', 'better-fit'})
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-EAB3CE3A — overall ranked match is distinct from cheapest match

**Test Case ID:** VC-EAB3CE3A

**Test Case Name:** RankingBoundaryTests.test_overall_ranked_match_is_distinct_from_cheapest_match

**System/Sub-system:** tests.test_ranking

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.643141+00:00

**Description:** Executable contract [tests.test_ranking.RankingBoundaryTests.test_overall_ranked_match_is_distinct_from_cheapest_match](../tests/test_ranking.py#L37), lines 37–45.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `policy = FixtureOrder(('better-fit', 'cheap')); result = self.db.search(request(), ranking_policy=policy)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_ranking.RankingBoundaryTests.test_overall_ranked_match_is_distinct_from_cheapest_match` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.overall_match.variant.variant_id, 'better-fit'); self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, 'cheap'); self.assertEqual(result.ranking_policy_version, 'fixture-judgments-v1'); self.assertFalse(result.can_claim_catalogue_minimum)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-FF24368E — policy cannot inject unqualified ids drop or duplicate matches

**Test Case ID:** VC-FF24368E

**Test Case Name:** RankingBoundaryTests.test_policy_cannot_inject_unqualified_ids_drop_or_duplicate_matches

**System/Sub-system:** tests.test_ranking

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.643198+00:00

**Description:** Executable contract [tests.test_ranking.RankingBoundaryTests.test_policy_cannot_inject_unqualified_ids_drop_or_duplicate_matches](../tests/test_ranking.py#L71), lines 71–81.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_ranking.RankingBoundaryTests.test_policy_cannot_inject_unqualified_ids_drop_or_duplicate_matches` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(RankingContractError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-9F4572F7 — policy version change cannot mislabel a result

**Test Case ID:** VC-9F4572F7

**Test Case Name:** RankingBoundaryTests.test_policy_version_change_cannot_mislabel_a_result

**System/Sub-system:** tests.test_ranking

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.643346+00:00

**Description:** Executable contract [tests.test_ranking.RankingBoundaryTests.test_policy_version_change_cannot_mislabel_a_result](../tests/test_ranking.py#L93), lines 93–102.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `policy = ChangingVersion(('better-fit', 'cheap'))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_ranking.RankingBoundaryTests.test_policy_version_change_cannot_mislabel_a_result` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaisesRegex(RankingContractError, 'version changed')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-90C116FF — ranking order cannot change the price minimum

**Test Case ID:** VC-90C116FF

**Test Case Name:** RankingBoundaryTests.test_ranking_order_cannot_change_the_price_minimum

**System/Sub-system:** tests.test_ranking

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.643462+00:00

**Description:** Executable contract [tests.test_ranking.RankingBoundaryTests.test_ranking_order_cannot_change_the_price_minimum](../tests/test_ranking.py#L59), lines 59–69.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `first = self.db.search(request(), ranking_policy=FixtureOrder(('better-fit', 'cheap'))); second = self.db.search(request(), ranking_policy=FixtureOrder(('cheap', 'better-fit'), 'v2'))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_ranking.RankingBoundaryTests.test_ranking_order_cannot_change_the_price_minimum` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(first.cheapest_qualifying_match, second.cheapest_qualifying_match); self.assertNotEqual(first.overall_match, second.overall_match)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-8FC98B19 — unversioned and untyped policy outputs are rejected

**Test Case ID:** VC-8FC98B19

**Test Case Name:** RankingBoundaryTests.test_unversioned_and_untyped_policy_outputs_are_rejected

**System/Sub-system:** tests.test_ranking

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.643545+00:00

**Description:** Executable contract [tests.test_ranking.RankingBoundaryTests.test_unversioned_and_untyped_policy_outputs_are_rejected](../tests/test_ranking.py#L83), lines 83–91.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_ranking.RankingBoundaryTests.test_unversioned_and_untyped_policy_outputs_are_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertRaises(RankingContractError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-8E2A66E9 — real dump restores schema catalogue and metadata

**Test Case ID:** VC-8E2A66E9

**Test Case Name:** RestoreTests.test_real_dump_restores_schema_catalogue_and_metadata

**System/Sub-system:** tests.test_restore

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.643668+00:00

**Description:** Executable contract [tests.test_restore.RestoreTests.test_real_dump_restores_schema_catalogue_and_metadata](../tests/test_restore.py#L20), lines 20–74.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `database = isolated_database(); original = os.environ['VOICECART_TEST_DSN']; config = conninfo_to_dict(original)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_restore.RestoreTests.test_real_dump_restores_schema_catalogue_and_metadata` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(restored.inspect(), database.inspect()); self.assertEqual(config['host'], conninfo_to_dict(target)['host'])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.1797 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-18058474 — body limits duplicate json and framing rejected

**Test Case ID:** VC-18058474

**Test Case Name:** ExtendedSecurityTests.test_body_limits_duplicate_json_and_framing_rejected

**System/Sub-system:** tests.test_security_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:18.826539+00:00

**Description:** Executable contract [tests.test_security_extended.ExtendedSecurityTests.test_body_limits_duplicate_json_and_framing_rejected](../tests/test_security_extended.py#L134), lines 134–146.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_security_extended.ExtendedSecurityTests.test_body_limits_duplicate_json_and_framing_rejected` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.raw('/api/local/search', body=body, headers=headers)[0], 400)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5515 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-8D856E72 — compose probe matches strict host policy

**Test Case ID:** VC-8D856E72

**Test Case Name:** ExtendedSecurityTests.test_compose_probe_matches_strict_host_policy

**System/Sub-system:** tests.test_security_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:19.378090+00:00

**Description:** Executable contract [tests.test_security_extended.ExtendedSecurityTests.test_compose_probe_matches_strict_host_policy](../tests/test_security_extended.py#L122), lines 122–132.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `compose = (Path(__file__).resolve().parents[1] / 'compose.yaml').read_text(); port = self.server.server_address[1]`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_security_extended.ExtendedSecurityTests.test_compose_probe_matches_strict_host_policy` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIn('VOICECART_PUBLIC_ORIGIN: http://localhost:8080', compose); self.assertIn("urlopen('http://localhost:8080/health'", compose); self.assertEqual(self.raw('/health', 'GET')[0], 403); self.assertEqual(self.raw('/health', 'GET', headers={'Host': f'localhost:{port}'})[0], 200)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5548 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-44973919 — cookie scope https flag origin cors and expiry

**Test Case ID:** VC-44973919

**Test Case Name:** ExtendedSecurityTests.test_cookie_scope_https_flag_origin_cors_and_expiry

**System/Sub-system:** tests.test_security_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:19.932946+00:00

**Description:** Executable contract [tests.test_security_extended.ExtendedSecurityTests.test_cookie_scope_https_flag_origin_cors_and_expiry](../tests/test_security_extended.py#L87), lines 87–120.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `port = self.server.server_address[1]; origin = f'https://localhost:{port}'; identity = self.server.application.auth.from_cookie(self.cookie, 'local', 'customer')`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_security_extended.ExtendedSecurityTests.test_cookie_scope_https_flag_origin_cors_and_expiry` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.request('cart')[0], 403); self.assertEqual(status, 201); self.assertIn('Secure', headers['Set-Cookie']); self.assertIn('HttpOnly', headers['Set-Cookie']); self.assertIn('SameSite=Strict', headers['Set-Cookie']); self.assertNotIn('Access-Control-Allow-Origin', headers); self.assertEqual(self.raw('/api/local/sessions', headers={'Host': f'localhost:{port}', 'Origin': 'null'})[0], 403); self.assertRaises(AccessDenied)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5678 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-6C32FC3F — every protected route requires correct role

**Test Case ID:** VC-6C32FC3F

**Test Case Name:** ExtendedSecurityTests.test_every_protected_route_requires_correct_role

**System/Sub-system:** tests.test_security_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:20.500863+00:00

**Description:** Executable contract [tests.test_security_extended.ExtendedSecurityTests.test_every_protected_route_requires_correct_role](../tests/test_security_extended.py#L40), lines 40–85.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `customers = {'POST': ['turns', 'search', 'query', 'ack', 'cancel', 'repeat', 'transcribe', 'speak', 'cart/add', 'cart/quantity', 'cart/retry'], 'GET': ['cart', 'operations']}; admins = {'POST': ['catalogue', 'import'], 'GET': ['export', 'imports', 'analytics', 'health']}; merchants = ['sessions', 'search', 'lookup', 'refresh', 'cart', 'add', 'quantity', 'operation']`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_security_extended.ExtendedSecurityTests.test_every_protected_route_requires_correct_role` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.raw('/api/local/admin/export', 'GET')[0], 403); self.assertEqual(self.raw('/api/local/merchant/' + name)[0], 403); self.assertEqual(self.raw('/api/local/' + name, method)[0], 403); self.assertEqual(self.raw('/api/local/admin/' + name, method)[0], 403)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5744 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-F7AD0E5C — health outage sanitized and missing secrets fail startup

**Test Case ID:** VC-F7AD0E5C

**Test Case Name:** ExtendedSecurityTests.test_health_outage_sanitized_and_missing_secrets_fail_startup

**System/Sub-system:** tests.test_security_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:21.075356+00:00

**Description:** Executable contract [tests.test_security_extended.ExtendedSecurityTests.test_health_outage_sanitized_and_missing_secrets_fail_startup](../tests/test_security_extended.py#L160), lines 160–174.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `app = self.server.application.apps['local']`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_security_extended.ExtendedSecurityTests.test_health_outage_sanitized_and_missing_secrets_fail_startup` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(status, 503); self.assertNotIn('PRIVATE TEST SQL DETAIL', str(payload)); self.assertRaises((ValueError, KeyError))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5559 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-F5CCEA95 — malformed nested admin import is 400 without publication

**Test Case ID:** VC-F5CCEA95

**Test Case Name:** ExtendedSecurityTests.test_malformed_nested_admin_import_is_400_without_publication

**System/Sub-system:** tests.test_security_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:21.631337+00:00

**Description:** Executable contract [tests.test_security_extended.ExtendedSecurityTests.test_malformed_nested_admin_import_is_400_without_publication](../tests/test_security_extended.py#L148), lines 148–158.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `before = self.database.inspect()['revision']`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_security_extended.ExtendedSecurityTests.test_malformed_nested_admin_import_is_400_without_publication` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(status, 400); self.assertEqual(self.database.inspect()['revision'], before)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5773 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C9F80A53 — artifact hash zero one two chunks and failure

**Test Case ID:** VC-C9F80A53

**Test Case Name:** SyllabusPartitions.test_artifact_hash_zero_one_two_chunks_and_failure

**System/Sub-system:** tests.test_syllabus

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.208917+00:00

**Description:** Executable contract [tests.test_syllabus.SyllabusPartitions.test_artifact_hash_zero_one_two_chunks_and_failure](../tests/test_syllabus.py#L108), lines 108–120.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_syllabus.SyllabusPartitions.test_artifact_hash_zero_one_two_chunks_and_failure` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(FileArtifact(path, hashlib.sha256(data).hexdigest()).verify(), path); self.assertRaises(VoiceError); self.assertRaises(VoiceError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0133 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-31BFFF6A — import file boundary and oversized manifest without huge allocation

**Test Case ID:** VC-31BFFF6A

**Test Case Name:** SyllabusPartitions.test_import_file_boundary_and_oversized_manifest_without_huge_allocation

**System/Sub-system:** tests.test_syllabus

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.222234+00:00

**Description:** Executable contract [tests.test_syllabus.SyllabusPartitions.test_import_file_boundary_and_oversized_manifest_without_huge_allocation](../tests/test_syllabus.py#L61), lines 61–79.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `source = Mock(); source.stat.return_value.st_size = 128 * 1024 * 1024; source.read_text.return_value = __import__('json').dumps(fabricated_document())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_syllabus.SyllabusPartitions.test_import_file_boundary_and_oversized_manifest_without_huge_allocation` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(load_import(source).revision, 'fixture-1'); source.read_text.assert_not_called(); self.assertRaises(ImportValidationError); self.assertRaises(ImportValidationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0009 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-849C95CC — money min max bool float and lt lte decision table

**Test Case ID:** VC-849C95CC

**Test Case Name:** SyllabusPartitions.test_money_min_max_bool_float_and_lt_lte_decision_table

**System/Sub-system:** tests.test_syllabus

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.223163+00:00

**Description:** Executable contract [tests.test_syllabus.SyllabusPartitions.test_money_min_max_bool_float_and_lt_lte_decision_table](../tests/test_syllabus.py#L20), lines 20–37.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_syllabus.SyllabusPartitions.test_money_min_max_bool_float_and_lt_lte_decision_table` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(Money(price, 'INR').minor_units, price); self.assertEqual(PriceLimit(Money(100, 'INR'), operator).permits(Money(price, 'INR')), expected); self.assertRaises((TypeError, ValueError))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-38AE0858 — number loop zero one two typical scales and early failure

**Test Case ID:** VC-38AE0858

**Test Case Name:** SyllabusPartitions.test_number_loop_zero_one_two_typical_scales_and_early_failure

**System/Sub-system:** tests.test_syllabus

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.223387+00:00

**Description:** Executable contract [tests.test_syllabus.SyllabusPartitions.test_number_loop_zero_one_two_typical_scales_and_early_failure](../tests/test_syllabus.py#L39), lines 39–59.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_syllabus.SyllabusPartitions.test_number_loop_zero_one_two_typical_scales_and_early_failure` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(whole_number(text), expected); self.assertRaises(InterpretationError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0002 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-7CB0A8CC — secret provisioning private parent and container readable files

**Test Case ID:** VC-7CB0A8CC

**Test Case Name:** SyllabusPartitions.test_secret_provisioning_private_parent_and_container_readable_files

**System/Sub-system:** tests.test_syllabus

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.223608+00:00

**Description:** Executable contract [tests.test_syllabus.SyllabusPartitions.test_secret_provisioning_private_parent_and_container_readable_files](../tests/test_syllabus.py#L81), lines 81–106.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `script = Path(__file__).resolve().parents[1] / 'scripts/init_secrets.py'`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_syllabus.SyllabusPartitions.test_secret_provisioning_private_parent_and_container_readable_files` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(stat.S_IMODE(parent.stat().st_mode), 448); self.assertNotEqual(again.returncode, 0); self.assertEqual(stat.S_IMODE(path.stat().st_mode), 292); self.assertNotIn(path.read_text().strip(), result.stdout)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0777 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-2D0D21E6 — publication batch zero one two 32 33 and early encoder failure

**Test Case ID:** VC-2D0D21E6

**Test Case Name:** SyllabusSQLLoops.test_publication_batch_zero_one_two_32_33_and_early_encoder_failure

**System/Sub-system:** tests.test_syllabus

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.304820+00:00

**Description:** Executable contract [tests.test_syllabus.SyllabusSQLLoops.test_publication_batch_zero_one_two_32_33_and_early_encoder_failure](../tests/test_syllabus.py#L162), lines 162–196.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `before = self.database.inspect()['revision']; raw = fabricated_document('batch-failure', before); raw['variants'] = [{**raw['variants'][0], 'variant_id': f'TEST-FAIL-{i}', 'sku': None} for i in range(33)]`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_syllabus.SyllabusSQLLoops.test_publication_batch_zero_one_two_32_33_and_early_encoder_failure` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.database.inspect()['revision'], before); self.assertRaises(RuntimeError); self.assertEqual(self.database.inspect()['variant_count'], count)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0583 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-7482DA5E — session min max and exact expiry boundary

**Test Case ID:** VC-7482DA5E

**Test Case Name:** SyllabusSQLLoops.test_session_min_max_and_exact_expiry_boundary

**System/Sub-system:** tests.test_syllabus

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.363096+00:00

**Description:** Executable contract [tests.test_syllabus.SyllabusSQLLoops.test_session_min_max_and_exact_expiry_boundary](../tests/test_syllabus.py#L138), lines 138–160.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `store = SessionStore(self.database); session = store.create(); fixed = datetime(2030, 1, 1, tzinfo=UTC)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_syllabus.SyllabusSQLLoops.test_session_min_max_and_exact_expiry_boundary` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIsInstance(store.create(ttl_seconds=ttl), str); self.assertRaises((ValueError, SessionError)); self.assertEqual(str(store.require(connection, session)['session_id']), session); self.assertRaises(SessionError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0172 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-7B9C78AA — concurrent traces do not mix

**Test Case ID:** VC-7B9C78AA

**Test Case Name:** TelemetryTests.test_concurrent_traces_do_not_mix

**System/Sub-system:** tests.test_telemetry

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.380329+00:00

**Description:** Executable contract [tests.test_telemetry.TelemetryTests.test_concurrent_traces_do_not_mix](../tests/test_telemetry.py#L26), lines 26–36.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_telemetry.TelemetryTests.test_concurrent_traces_do_not_mix` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(list(pool.map(record, range(20))), list(map(str, range(20))))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0005 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-662546DC — nested failure numeric metrics and context cleanup

**Test Case ID:** VC-662546DC

**Test Case Name:** TelemetryTests.test_nested_failure_numeric_metrics_and_context_cleanup

**System/Sub-system:** tests.test_telemetry

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.380883+00:00

**Description:** Executable contract [tests.test_telemetry.TelemetryTests.test_nested_failure_numeric_metrics_and_context_cleanup](../tests/test_telemetry.py#L10), lines 10–24.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_telemetry.TelemetryTests.test_nested_failure_numeric_metrics_and_context_cleanup` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(trace.spans[0]['outcome'], 'error'); self.assertEqual(trace.spans[1]['seconds'], 2); self.assertNotIn('PRIVATE', str(trace.spans)); self.assertEqual(len(trace.spans), 2); self.assertRaises(ValueError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0001 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-651890F3 — failure before commit rolls back and original id recovers

**Test Case ID:** VC-651890F3

**Test Case Name:** ExtendedTransactionTests.test_failure_before_commit_rolls_back_and_original_id_recovers

**System/Sub-system:** tests.test_transaction_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.383262+00:00

**Description:** Executable contract [tests.test_transaction_extended.ExtendedTransactionTests.test_failure_before_commit_rolls_back_and_original_id_recovers](../tests/test_transaction_extended.py#L58), lines 58–81.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `management = self.seed_line(); operation = str(uuid.uuid4()); connect = self.database.connect`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_transaction_extended.ExtendedTransactionTests.test_failure_before_commit_rolls_back_and_original_id_recovers` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(management.overview(self.session)['items'][0]['quantity'], 1); self.assertIsNone(management.receipt(self.session, operation)); self.assertEqual(management.overview(self.session)['items'][0]['quantity'], 2); self.assertRaises(OutcomeUnknown)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0419 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-C301E793 — loss after commit reconciles authoritative adjustment

**Test Case ID:** VC-C301E793

**Test Case Name:** ExtendedTransactionTests.test_loss_after_commit_reconciles_authoritative_adjustment

**System/Sub-system:** tests.test_transaction_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.425205+00:00

**Description:** Executable contract [tests.test_transaction_extended.ExtendedTransactionTests.test_loss_after_commit_reconciles_authoritative_adjustment](../tests/test_transaction_extended.py#L83), lines 83–103.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `management = self.seed_line(); operation = str(uuid.uuid4()); connect = self.database.connect`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_transaction_extended.ExtendedTransactionTests.test_loss_after_commit_reconciles_authoritative_adjustment` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(receipt['status'], 'committed'); self.assertEqual(management.overview(self.session)['items'][0]['quantity'], 2)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0336 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-4D2E7689 — parallel target updates duplicate payload and immutable replay

**Test Case ID:** VC-4D2E7689

**Test Case Name:** ExtendedTransactionTests.test_parallel_target_updates_duplicate_payload_and_immutable_replay

**System/Sub-system:** tests.test_transaction_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.458828+00:00

**Description:** Executable contract [tests.test_transaction_extended.ExtendedTransactionTests.test_parallel_target_updates_duplicate_payload_and_immutable_replay](../tests/test_transaction_extended.py#L30), lines 30–56.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `management = self.seed_line(); operations = [str(uuid.uuid4()), str(uuid.uuid4())]; final = management.overview(self.session)['items'][0]['quantity']`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_transaction_extended.ExtendedTransactionTests.test_parallel_target_updates_duplicate_payload_and_immutable_replay` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIn(final, (2, 3)); self.assertEqual(management.overview(self.session)['items'][0]['quantity'], final); self.assertEqual(receipt['quantity'], quantity); self.assertEqual(management.set_quantity(self.session, receipt['operation_id'], 'v-cheap', quantity, 'INR'), receipt); self.assertRaises(CartError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0416 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-531EFE89 — postcommit receipt outage is unknown then same id replays

**Test Case ID:** VC-531EFE89

**Test Case Name:** ExtendedTransactionTests.test_postcommit_receipt_outage_is_unknown_then_same_id_replays

**System/Sub-system:** tests.test_transaction_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.500396+00:00

**Description:** Executable contract [tests.test_transaction_extended.ExtendedTransactionTests.test_postcommit_receipt_outage_is_unknown_then_same_id_replays](../tests/test_transaction_extended.py#L105), lines 105–123.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `management = self.seed_line(); operation = str(uuid.uuid4()); recovered = CartManagement(self.database).receipt(self.session, operation)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_transaction_extended.ExtendedTransactionTests.test_postcommit_receipt_outage_is_unknown_then_same_id_replays` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(recovered['status'], 'committed'); self.assertEqual(management.set_quantity(self.session, operation, 'v-cheap', 2, 'INR'), recovered); self.assertEqual(management.overview(self.session)['items'][0]['quantity'], 2); self.assertRaises(OutcomeUnknown)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0343 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-3A859246 — product deactivation after search prevents add

**Test Case ID:** VC-3A859246

**Test Case Name:** ExtendedTransactionTests.test_product_deactivation_after_search_prevents_add

**System/Sub-system:** tests.test_transaction_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.534713+00:00

**Description:** Executable contract [tests.test_transaction_extended.ExtendedTransactionTests.test_product_deactivation_after_search_prevents_add](../tests/test_transaction_extended.py#L165), lines 165–178.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `command = self.command(); raw = fabricated_document('fixture-deactivated', 'fixture-1'); parent = next((v['product_id'] for v in raw['variants'] if v['variant_id'] == 'v-cheap'))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_transaction_extended.ExtendedTransactionTests.test_product_deactivation_after_search_prevents_add` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.items(self.session), {}); self.assertRaises(CartError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0303 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-CE1AD344 — session expiry during quantity eligibility blocks write

**Test Case ID:** VC-CE1AD344

**Test Case Name:** ExtendedTransactionTests.test_session_expiry_during_quantity_eligibility_blocks_write

**System/Sub-system:** tests.test_transaction_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.564999+00:00

**Description:** Executable contract [tests.test_transaction_extended.ExtendedTransactionTests.test_session_expiry_during_quantity_eligibility_blocks_write](../tests/test_transaction_extended.py#L144), lines 144–163.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `management = self.seed_line(); snapshot = self.database.snapshot_in; now = datetime.now(UTC)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_transaction_extended.ExtendedTransactionTests.test_session_expiry_during_quantity_eligibility_blocks_write` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(management.overview(self.session)['items'][0]['quantity'], 1); self.assertIsNone(management.receipt(self.session, operation)); self.assertRaises(SessionError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0318 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-29B52894 — session expiry during snapshot blocks add before write

**Test Case ID:** VC-29B52894

**Test Case Name:** ExtendedTransactionTests.test_session_expiry_during_snapshot_blocks_add_before_write

**System/Sub-system:** tests.test_transaction_extended

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.596816+00:00

**Description:** Executable contract [tests.test_transaction_extended.ExtendedTransactionTests.test_session_expiry_during_snapshot_blocks_add_before_write](../tests/test_transaction_extended.py#L125), lines 125–142.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `snapshot = self.database.snapshot_in; now = datetime.now(UTC)`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_transaction_extended.ExtendedTransactionTests.test_session_expiry_during_snapshot_blocks_add_before_write` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.cart.items(self.session), {}); self.assertEqual(expired.exception.code, 'invalid_or_expired_operation'); self.assertRaises(CartError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0271 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-7C98A10E — all response codes share verified output path

**Test Case ID:** VC-7C98A10E

**Test Case Name:** DeliveryTests.test_all_response_codes_share_verified_output_path

**System/Sub-system:** tests.test_voice_delivery

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.623950+00:00

**Description:** Executable contract [tests.test_voice_delivery.DeliveryTests.test_all_response_codes_share_verified_output_path](../tests/test_voice_delivery.py#L21), lines 21–54.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_voice_delivery.DeliveryTests.test_all_response_codes_share_verified_output_path` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.kind, 'response_completed'); self.assertGreater(len(output.played_chunks), 0); self.assertFalse(controller.is_capture_gated); self.assertFalse(controller.process_transcript(Transcript(TranscriptKind.FINAL, 'add', controller.current_turn_id or 'expired')))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0003 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-51DFAA92 — artifact integrity and resource cleanup without fake onset

**Test Case ID:** VC-51DFAA92

**Test Case Name:** DeliveryTests.test_artifact_integrity_and_resource_cleanup_without_fake_onset

**System/Sub-system:** tests.test_voice_delivery

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.624229+00:00

**Description:** Executable contract [tests.test_voice_delivery.DeliveryTests.test_artifact_integrity_and_resource_cleanup_without_fake_onset](../tests/test_voice_delivery.py#L97), lines 97–135.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `output = SoundDeviceOutput(driver=Driver())`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_voice_delivery.DeliveryTests.test_artifact_integrity_and_resource_cleanup_without_fake_onset` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertIsNone(output.drain('t')); self.assertTrue(Stream.closed); self.assertFalse(output.is_playing()); self.assertEqual(artifact.verify(), path); self.assertRaises(VoiceError)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0007 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-94AC0591 — playback failure uses assistive channel and never claims audible delivery

**Test Case ID:** VC-94AC0591

**Test Case Name:** DeliveryTests.test_playback_failure_uses_assistive_channel_and_never_claims_audible_delivery

**System/Sub-system:** tests.test_voice_delivery

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.624958+00:00

**Description:** Executable contract [tests.test_voice_delivery.DeliveryTests.test_playback_failure_uses_assistive_channel_and_never_claims_audible_delivery](../tests/test_voice_delivery.py#L74), lines 74–95.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `output = MockAudioOutput(); output.play_chunk = broken; controller = HalfDuplexTurnController()`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_voice_delivery.DeliveryTests.test_playback_failure_uses_assistive_channel_and_never_claims_audible_delivery` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(delivery.kind, 'assistive_only'); self.assertIsNone(delivery.audible_onset); self.assertTrue(any(('Speech unavailable' in status.text for status in controller.status_messages)))
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-B7231EE2 — tts fallback is not a completed product list

**Test Case ID:** VC-B7231EE2

**Test Case Name:** DeliveryTests.test_tts_fallback_is_not_a_completed_product_list

**System/Sub-system:** tests.test_voice_delivery

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.625008+00:00

**Description:** Executable contract [tests.test_voice_delivery.DeliveryTests.test_tts_fallback_is_not_a_completed_product_list](../tests/test_voice_delivery.py#L56), lines 56–72.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `controller = HalfDuplexTurnController(); output = MockAudioOutput(); fallback = CachedSpeechPrompt('Please use text or retry.', AudioChunk(b'\x00\x00' * 100, 16000))`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_voice_delivery.DeliveryTests.test_tts_fallback_is_not_a_completed_product_list` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(result.kind, 'fallback_completed'); self.assertEqual(output.played_chunks, [fallback.chunk])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.0000 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-669D5BDD — cancelled asr final cannot reappear or mutate

**Test Case ID:** VC-669D5BDD

**Test Case Name:** CustomerHTTPTests.test_cancelled_asr_final_cannot_reappear_or_mutate

**System/Sub-system:** tests.test_web_customer

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:22.627530+00:00

**Description:** Executable contract [tests.test_web_customer.CustomerHTTPTests.test_cancelled_asr_final_cannot_reappear_or_mutate](../tests/test_web_customer.py#L168), lines 168–217.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `entered = threading.Event(); cancelled_seen = threading.Event(); web = self.server.application`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_web_customer.CustomerHTTPTests.test_cancelled_asr_final_cannot_reappear_or_mutate` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertTrue(entered.wait(2)); self.assertEqual(self.request('cancel', {})[0], 200); self.assertTrue(cancelled_seen.is_set()); self.assertEqual(result[0][0], 409); self.assertNotIn('STALE TEST TRANSCRIPT', str(result)); self.assertEqual(self.request('cart')[1]['items'], [])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5380 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-743C910F — discovery cannot silently drop a text price boundary

**Test Case ID:** VC-743C910F

**Test Case Name:** CustomerHTTPTests.test_discovery_cannot_silently_drop_a_text_price_boundary

**System/Sub-system:** tests.test_web_customer

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:23.165628+00:00

**Description:** Executable contract [tests.test_web_customer.CustomerHTTPTests.test_discovery_cannot_silently_drop_a_text_price_boundary](../tests/test_web_customer.py#L153), lines 153–166.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `body = {'query': 'backpack under 20 rupees', 'currency': 'INR'}`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_web_customer.CustomerHTTPTests.test_discovery_cannot_silently_drop_a_text_price_boundary` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.request('search', body)[0], 400); self.assertEqual(self.request('search', {**body, 'under_minor': 2000, 'inclusive': True})[0], 400); self.assertEqual(self.request('search', {**body, 'under_minor': '2000', 'inclusive': False})[0], 200)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5724 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-D7495CCB — registered final cancelled before arrival cannot execute

**Test Case ID:** VC-D7495CCB

**Test Case Name:** CustomerHTTPTests.test_registered_final_cancelled_before_arrival_cannot_execute

**System/Sub-system:** tests.test_web_customer

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:23.738138+00:00

**Description:** Executable contract [tests.test_web_customer.CustomerHTTPTests.test_registered_final_cancelled_before_arrival_cannot_execute](../tests/test_web_customer.py#L140), lines 140–151.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `status, registration = self.request('turns', {}); status, result = self.request('query', {'turn_id': registration['turn_id'], 'text': 'add a black backpack'})`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_web_customer.CustomerHTTPTests.test_registered_final_cancelled_before_arrival_cannot_execute` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(status, 201); self.assertEqual(status, 200); self.assertEqual(result['code'], 'cancelled'); self.assertEqual(self.request('cart')[1]['items'], [])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5818 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-9AFE1AE2 — search add replay quantity remove and resume

**Test Case ID:** VC-9AFE1AE2

**Test Case Name:** CustomerHTTPTests.test_search_add_replay_quantity_remove_and_resume

**System/Sub-system:** tests.test_web_customer

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:24.320050+00:00

**Description:** Executable contract [tests.test_web_customer.CustomerHTTPTests.test_search_add_replay_quantity_remove_and_resume](../tests/test_web_customer.py#L67), lines 67–120.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `status, session = self.request('sessions', {}); status, result = self.request('search', {'query': 'backpack', 'category': 'backpack', 'currency': 'INR'}); item = result['items'][0]`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_web_customer.CustomerHTTPTests.test_search_add_replay_quantity_remove_and_resume` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(status, 201); self.assertEqual(self.request('sessions', {})[1]['session_id'], session['session_id']); self.assertEqual(status, 200); self.assertEqual(self.request('cart/add', body)[1]['code'], 'added'); self.assertEqual(self.request('cart/add', body)[1]['code'], 'added'); self.assertEqual(self.request('cart')[1]['items'][0]['quantity'], 1); self.assertEqual(self.request('cart/add', changed)[0], 409); self.assertEqual(self.request('cart/quantity', {'operation_id': body['operation_id'], 'variant_id': item['variant_id'], 'quantity': 0, 'currency': 'INR'})[0], 409); self.assertEqual(self.request('cart/quantity', update)[1]['quantity'], 2); self.assertEqual(self.request('cart/quantity', update)[1]['quantity'], 2); self.assertEqual(self.request('cart/quantity', update)[1]['quantity'], 0); self.assertEqual(self.request('cart')[1]['items'], []); self.assertGreaterEqual(len(self.request('operations')[1]['operations']), 3); self.assertEqual(CartManagement(self.database).receipt(session['session_id'], update['operation_id'])['status'], 'committed')
```

**Actual Result:** All method assertions completed without a failure. Duration 0.6453 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-800A6D3A — unauthenticated invalid quantity and unknown voice

**Test Case ID:** VC-800A6D3A

**Test Case Name:** CustomerHTTPTests.test_unauthenticated_invalid_quantity_and_unknown_voice

**System/Sub-system:** tests.test_web_customer

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:24.965451+00:00

**Description:** Executable contract [tests.test_web_customer.CustomerHTTPTests.test_unauthenticated_invalid_quantity_and_unknown_voice](../tests/test_web_customer.py#L122), lines 122–138.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `See the source method and class setUp fixture.`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_web_customer.CustomerHTTPTests.test_unauthenticated_invalid_quantity_and_unknown_voice` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertEqual(self.request('cart')[0], 403); self.assertEqual(self.request('cart/quantity', {'operation_id': str(uuid.uuid4()), 'variant_id': 'v-best', 'quantity': True, 'currency': 'INR'})[0], 400); self.assertEqual(self.request('transcribe', {'pcm_base64': 'AAAAAA=='})[0], 503); self.assertEqual(self.request('search', {'query': 'x', 'limit': 101})[0], 400)
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5680 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


## VC-84723B96 — unknown historical inventory never enables add

**Test Case ID:** VC-84723B96

**Test Case Name:** CustomerHTTPTests.test_unknown_historical_inventory_never_enables_add

**System/Sub-system:** tests.test_web_customer

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-03 (current mapping review; see Git source history for original design)

**Executed By:** Python unittest runner

**Execution Date:** 2026-11-03T04:03:25.533487+00:00

**Description:** Executable contract [tests.test_web_customer.CustomerHTTPTests.test_unknown_historical_inventory_never_enables_add](../tests/test_web_customer.py#L219), lines 219–237.

**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.

**Concrete input arrangement:** `result = self.request('search', {'query': 'backpack', 'currency': 'INR'})[1]; row = result['items'][0]; body = {'operation_id': str(uuid.uuid4()), 'variant_id': row['variant_id'], 'quantity': 1, 'currency': 'INR', 'revision': row['revision'], 'unit_price_minor': row['price_minor']}`

**Test Steps / Step Number / Action:**

1. Arrange the exact source fixture and input cases linked above.
2. Execute `python -m scripts.run_tests tests.test_web_customer.CustomerHTTPTests.test_unknown_historical_inventory_never_enables_add` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).
3. Evaluate the following exact source assertions and restore owned temporary state.

**Expected Result:**

```python
self.assertFalse(any((row['can_add'] for row in result['items']))); self.assertEqual(self.request('cart/add', body)[0], 409); self.assertEqual(self.request('cart')[1]['items'], [])
```

**Actual Result:** All method assertions completed without a failure. Duration 0.5954 seconds.

**Pass/Fail/Not Run:** Pass

**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.

**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.

**Defect Reference:** None observed in this execution.


# Manual and external acceptance records


## VC-MAN-DEVICE — Physical microphone/speaker and noise/pauses/interruptions

**Test Case ID:** VC-MAN-DEVICE

**Test Case Name:** Physical microphone/speaker and noise/pauses/interruptions

**System/Sub-system:** Release acceptance

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-02

**Executed By:** Not Run

**Execution Date:** Not Run

**Description:** Required acceptance beyond automated source/browser contracts.

**Preconditions:** Owner-approved real environment/users/rights and isolated recovery plan.

**Test Steps / Step Number / Action:** 1. Provision exact English voice models and consented physical devices; record several prices/SKUs with silence/noise and stop/repeat. 2. Record observations, failures and evidence. 3. Restore/stop the test resources.

**Expected Result:** Correct reviewed transcripts/negation, no partial mutation, stopped audio, understood prices and recovery.

**Actual Result:** Headless host capture returned NotSupportedError; browser capture/ASR fault tests are explicitly scripted. Physical device/user test Not Run.

**Pass/Fail/Not Run:** Not Run

**Comments:** No automated fixture/model/protocol result is substituted for this acceptance.

**Postconditions:** Protect owner data; stop capture and remove unnecessary diagnostics.

**Defect Reference:** OPEN-DEVICE.


## VC-MAN-A11Y — Representative blind/low-vision screen-reader acceptance

**Test Case ID:** VC-MAN-A11Y

**Test Case Name:** Representative blind/low-vision screen-reader acceptance

**System/Sub-system:** Release acceptance

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-02

**Executed By:** Not Run

**Execution Date:** Not Run

**Description:** Required acceptance beyond automated source/browser contracts.

**Preconditions:** Owner-approved real environment/users/rights and isolated recovery plan.

**Test Steps / Step Number / Action:** 1. Use actual VoiceOver/screen reader and keyboard on desktop/mobile; search, review, select, change cart and recover from error. 2. Record observations, failures and evidence. 3. Restore/stop the test resources.

**Expected Result:** Correct focus/order/status announcements, intelligible amounts/SKUs and independent completion without a mouse.

**Actual Result:** Automated keyboard/axe checks passed checked states; representative-user/screen-reader speech acceptance Not Run.

**Pass/Fail/Not Run:** Not Run

**Comments:** No automated fixture/model/protocol result is substituted for this acceptance.

**Postconditions:** Protect owner data; stop capture and remove unnecessary diagnostics.

**Defect Reference:** OPEN-A11Y.


## VC-MAN-DOCKER — Clean container installation and persistent restart

**Test Case ID:** VC-MAN-DOCKER

**Test Case Name:** Clean container installation and persistent restart

**System/Sub-system:** Release acceptance

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-02

**Executed By:** Not Run

**Execution Date:** Not Run

**Description:** Required acceptance beyond automated source/browser contracts.

**Preconditions:** Owner-approved real environment/users/rights and isolated recovery plan.

**Test Steps / Step Number / Action:** 1. Install Docker; provision private secrets; compose config/up; migrate/import; stop/start and restore into a separate destination. 2. Record observations, failures and evidence. 3. Restore/stop the test resources.

**Expected Result:** Healthy actual services, readable scoped secrets, persisted revision/cart/receipts, correct migration/recovery and no seed fixtures.

**Actual Result:** Docker is unavailable; static configuration only. Clean container/restart acceptance Not Run.

**Pass/Fail/Not Run:** Not Run

**Comments:** No automated fixture/model/protocol result is substituted for this acceptance.

**Postconditions:** Protect owner data; stop capture and remove unnecessary diagnostics.

**Defect Reference:** OPEN-DOCKER.


## VC-MAN-MERCHANT — External merchant platform conformance

**Test Case ID:** VC-MAN-MERCHANT

**Test Case Name:** External merchant platform conformance

**System/Sub-system:** Release acceptance

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-02

**Executed By:** Not Run

**Execution Date:** Not Run

**Description:** Required acceptance beyond automated source/browser contracts.

**Preconditions:** Owner-approved real environment/users/rights and isolated recovery plan.

**Test Steps / Step Number / Action:** 1. Implement an approved adapter with real merchant credentials/current source and authoritative idempotency/outcome lookup. 2. Record observations, failures and evidence. 3. Restore/stop the test resources.

**Expected Result:** Fresh merchant facts and platform receipt own every confirmed mutation; tenant/auth/retry/failure contracts hold.

**Actual Result:** Only the actual local adapter is implemented; external Shopify/WooCommerce/Magento integration Not Run/unsupported.

**Pass/Fail/Not Run:** Not Run

**Comments:** No automated fixture/model/protocol result is substituted for this acceptance.

**Postconditions:** Protect owner data; stop capture and remove unnecessary diagnostics.

**Defect Reference:** OPEN-MERCHANT.


## VC-MAN-RIGHTS — Distribution and data/voice rights review

**Test Case ID:** VC-MAN-RIGHTS

**Test Case Name:** Distribution and data/voice rights review

**System/Sub-system:** Release acceptance

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-02

**Executed By:** Not Run

**Execution Date:** Not Run

**Description:** Required acceptance beyond automated source/browser contracts.

**Preconditions:** Owner-approved real environment/users/rights and isolated recovery plan.

**Test Steps / Step Number / Action:** 1. Owner specifies project/license/deployment intent and obtains dataset/voice/dependency distribution clearance. 2. Record observations, failures and evidence. 3. Restore/stop the test resources.

**Expected Result:** Exact notices, source obligations and permitted data/voice use documented for the actual shipped artifacts.

**Actual Result:** Inventory/declared terms inspected; no dataset-wide redistribution grant or owner project license selected. Commercial redistribution acceptance Not Run.

**Pass/Fail/Not Run:** Not Run

**Comments:** No automated fixture/model/protocol result is substituted for this acceptance.

**Postconditions:** Protect owner data; stop capture and remove unnecessary diagnostics.

**Defect Reference:** OPEN-RIGHTS.


## VC-MAN-AUDIBLE — Calibrated full audible latency acceptance

**Test Case ID:** VC-MAN-AUDIBLE

**Test Case Name:** Calibrated full audible latency acceptance

**System/Sub-system:** Release acceptance

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-02

**Executed By:** Not Run

**Execution Date:** Not Run

**Description:** Required acceptance beyond automated source/browser contracts.

**Preconditions:** Owner-approved real environment/users/rights and isolated recovery plan.

**Test Steps / Step Number / Action:** 1. Measure actual end of user speech to meaningful verified audible response, cold/warm, failures and sufficient samples on approved hardware/language. 2. Record observations, failures and evidence. 3. Restore/stop the test resources.

**Expected Result:** Report sample sizes/percentiles/timeouts and compare the unchanged 1.5s goal without substituting enqueue or synthesis time.

**Actual Result:** Stage/file timings exist; calibrated acoustic/human full-turn acceptance Not Run.

**Pass/Fail/Not Run:** Not Run

**Comments:** No automated fixture/model/protocol result is substituted for this acceptance.

**Postconditions:** Protect owner data; stop capture and remove unnecessary diagnostics.

**Defect Reference:** OPEN-AUDIBLE.


## VC-MAN-PLATFORM — Windows/Linux/GPU/mobile hardware acceptance

**Test Case ID:** VC-MAN-PLATFORM

**Test Case Name:** Windows/Linux/GPU/mobile hardware acceptance

**System/Sub-system:** Release acceptance

**Designed By:** VoiceCart engineering test automation

**Design Date:** 2026-11-02

**Executed By:** Not Run

**Execution Date:** Not Run

**Description:** Required acceptance beyond automated source/browser contracts.

**Preconditions:** Owner-approved real environment/users/rights and isolated recovery plan.

**Test Steps / Step Number / Action:** 1. Run documented clean setup and real devices on each supported candidate platform, including network/permissions and model resources. 2. Record observations, failures and evidence. 3. Restore/stop the test resources.

**Expected Result:** Platform-specific setup, recovery, input/output and resource observations recorded without assuming parity.

**Actual Result:** Native macOS source/wheel/Chromium checks completed; other physical platform/GPU acceptance Not Run.

**Pass/Fail/Not Run:** Not Run

**Comments:** No automated fixture/model/protocol result is substituted for this acceptance.

**Postconditions:** Protect owner data; stop capture and remove unnecessary diagnostics.

**Defect Reference:** OPEN-PLATFORM.


## VC-ML-H05 — held-out quantity interpretation

**Test Case ID:** VC-ML-H05

**Test Case Name:** Two-item explicit search-and-add

**System/Sub-system:** Actual pinned local NLU

**Designed By:** VoiceCart frozen holdout design

**Design Date:** 2026-11-02

**Executed By:** scripts/benchmark_nlu.py against actual Qwen

**Execution Date:** 2026-11-02

**Description:** H05 in tests/nlu_holdout.json; no prompt tuning on this evaluation.

**Preconditions:** Pinned local Qwen model and canonical fixture vocabulary, no writes.

**Test Steps / Step Number / Action:** 1. Submit the exact H05 text. 2. Apply strict independent validation. 3. Compare against search_and_add quantity 2 expectation.

**Expected Result:** Valid explicit intent with quantity 2.

**Actual Result:** InterpretationError (safe rejection), recorded 21.882 seconds; no commerce dispatch.

**Pass/Fail/Not Run:** Fail (quality expectation; safety preserved).

**Comments:** Eleven other declared holdout expectations passed; this is not population accuracy.

**Postconditions:** No cart/database mutation.

**Defect Reference:** OPEN-NLU-H05; improve on development data and reevaluate on a new frozen holdout.
