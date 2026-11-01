# Source-level control-flow analysis

Generated from actual current source. Nodes include explicit decisions, short-circuit Boolean tests, loops, returns/raises and context cleanup. Nested callable/comprehension frames and arbitrary implicit faults inside external calls are outside this intraprocedural convention. Declared try handlers are represented; this is not a claim of exhaustive exception/path coverage.

Each listed basis is a structural GF(2) edge-independent entry/exit path set. Logical feasibility and concrete input execution are separate: refer to the input bank and measured branch report. Unexecuted/infeasible candidate paths are **Not Run**, never presented as achieved path coverage. Regions are actual faces enumerated from a planar embedding when available, including the exterior. Predicate equivalents sum outdegree−1 for multiway nodes.


## application.py: money_text

Source: [voicecart/application.py:39](../voicecart/application.py#L39), through line 43.

N=9, E=10, P=1. **E−N+2P = 10−9+2 = 3**. Predicate equivalents 2; **predicates+1 = 3**. Planar embedding has **3 regions** including the exterior.

Input/design bank: INR 100, INR 101, USD 100; tests/test_application.py confirmation/system assertions.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L43: return f'{amount} minor units {currency}'"]

 n3["L42: return f'{rupees} rupees' + (f' and {paise} paise' if paise else '')"]

 n4["L42: evaluate f' and {paise} paise'"]

 n5["L42: evaluate ''"]

 n6["L42: test paise"]

 n7["L41: rupees, paise = divmod(amount, 100)"]

 n8["L40: test currency == 'INR'"]

 n1 -->|next| n8

 n2 -->|next| n0

 n3 -->|next| n0

 n4 -->|next| n3

 n5 -->|next| n3

 n6 -->|T| n4

 n6 -->|F| n5

 n7 -->|next| n6

 n8 -->|T| n7

 n8 -->|F| n2

```

Structural independent basis (execution status as above):

- B1: n1 → n8 → n2 → n0

- B2: n1 → n8 → n7 → n6 → n4 → n3 → n0

- B3: n1 → n8 → n7 → n6 → n5 → n3 → n0


## nlu.py: rupees_to_minor

Source: [voicecart/nlu.py:118](../voicecart/nlu.py#L118), through line 132.

N=14, E=18, P=1. **E−N+2P = 18−14+2 = 6**. Predicate equivalents 5; **predicates+1 = 6**. Planar embedding has **6 regions** including the exterior.

Input/design bank: 0, 0.01, 1,000, 1,00,000.50, two thousand, malformed punctuation, negative/nonfinite and input longer than 100 characters; tests/test_nlu.py and tests/test_syllabus.py. Parser normal/handled failure paths are explicit; nested whole_number loop tests are separately documented.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L132: return result"]

 n3["L131: require_integer(result, 'amount_minor')"]

 n4["L128: raise InterpretationError('Invalid amount') from exc"]

 n5["L126: result = int(Decimal(cleaned.replace(',', '')) * 100)"]

 n6["L125: try: normal or declared handled exception"]

 n7["L130: result = whole_number(cleaned) * 100"]

 n8["L122: test re.fullmatch('(?:\\d{1,3}(?:,\\d{3})+|\\d{1,2}(?:,\\d{2})*,\\d{3})(?:\\.\\d{1,2})?', cleaned)"]

 n9["L122: test re.fullmatch('\\d+(?:\\.\\d{1,2})?', cleaned)"]

 n10["L121: cleaned = text.strip()"]

 n11["L120: raise InterpretationError('Invalid amount')"]

 n12["L119: test len(text) &gt; 100"]

 n13["L119: test isinstance(text, str)"]

 n1 -->|next| n13

 n2 -->|next| n0

 n3 -->|next| n2

 n4 -->|next| n0

 n5 -->|next| n3

 n6 -->|normal| n5

 n6 -->|handler 0| n4

 n7 -->|next| n3

 n8 -->|T| n6

 n8 -->|F| n7

 n9 -->|T| n6

 n9 -->|F| n8

 n10 -->|next| n9

 n11 -->|next| n0

 n12 -->|T| n11

 n12 -->|F| n10

 n13 -->|T| n12

 n13 -->|F| n11

```

Structural independent basis (execution status as above):

- B1: n1 → n13 → n11 → n0

- B2: n1 → n13 → n12 → n10 → n9 → n6 → n5 → n3 → n2 → n0

- B3: n1 → n13 → n12 → n10 → n9 → n6 → n4 → n0

- B4: n1 → n13 → n12 → n10 → n9 → n8 → n7 → n3 → n2 → n0

- B5: n1 → n13 → n12 → n10 → n9 → n8 → n6 → n4 → n0

- B6: n1 → n13 → n12 → n11 → n0


## search.py: item_price

Source: [voicecart/search.py:41](../voicecart/search.py#L41), through line 44.

N=5, E=5, P=1. **E−N+2P = 5−5+2 = 2**. Predicate equivalents 1; **predicates+1 = 2**. Planar embedding has **2 regions** including the exterior.

Input/design bank: Qualified priced fixture versus price=None; tests/test_persistence.py and tests/test_catalogue.py.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L44: return item.variant.price.minor_units"]

 n3["L43: raise ValueError('Qualified candidate lacks price')"]

 n4["L42: test item.variant.price is None"]

 n1 -->|next| n4

 n2 -->|next| n0

 n3 -->|next| n0

 n4 -->|T| n3

 n4 -->|F| n2

```

Structural independent basis (execution status as above):

- B1: n1 → n4 → n2 → n0

- B2: n1 → n4 → n3 → n0


## ranking.py: rank_qualified

Source: [voicecart/ranking.py:27](../voicecart/ranking.py#L27), through line 47.

N=17, E=22, P=1. **E−N+2P = 22−17+2 = 7**. Predicate equivalents 6; **predicates+1 = 7**. Planar embedding has **7 regions** including the exterior.

Input/design bank: Valid permutation, empty/non-string version, changed version, list output, non-string ID, duplicate/missing/injected IDs; tests/test_ranking.py.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L47: return (version, tuple((by_id[variant_id] for variant_id in ordered)))"]

 n3["L46: raise RankingContractError('policy must return every qualified ID exactly once')"]

 n4["L45: test set(ordered) != set(by_id)"]

 n5["L45: test len(ordered) != len(by_id)"]

 n6["L44: by_id = {item.variant.variant_id: item for item in qualified}"]

 n7["L41: raise RankingContractError('policy must return a tuple of qualified variant IDs')"]

 n8["L40: test any((not isinstance(x, str) for x in ordered))"]

 n9["L40: test isinstance(ordered, tuple)"]

 n10["L39: raise RankingContractError('policy version changed during ranking')"]

 n11["L38: test policy.version != version"]

 n12["L37: ordered = policy.rank(request, qualified)"]

 n13["L36: raise RankingContractError(str(error)) from error"]

 n14["L34: require_text(version, 'ranking policy version')"]

 n15["L33: try: normal or declared handled exception"]

 n16["L32: version = policy.version"]

 n1 -->|next| n16

 n2 -->|next| n0

 n3 -->|next| n0

 n4 -->|T| n3

 n4 -->|F| n2

 n5 -->|T| n3

 n5 -->|F| n4

 n6 -->|next| n5

 n7 -->|next| n0

 n8 -->|T| n7

 n8 -->|F| n6

 n9 -->|T| n8

 n9 -->|F| n7

 n10 -->|next| n0

 n11 -->|T| n10

 n11 -->|F| n9

 n12 -->|next| n11

 n13 -->|next| n0

 n14 -->|next| n12

 n15 -->|normal| n14

 n15 -->|handler 0| n13

 n16 -->|next| n15

```

Structural independent basis (execution status as above):

- B1: n1 → n16 → n15 → n13 → n0

- B2: n1 → n16 → n15 → n14 → n12 → n11 → n9 → n8 → n6 → n5 → n4 → n2 → n0

- B3: n1 → n16 → n15 → n14 → n12 → n11 → n9 → n8 → n6 → n5 → n3 → n0

- B4: n1 → n16 → n15 → n14 → n12 → n11 → n9 → n8 → n6 → n5 → n4 → n3 → n0

- B5: n1 → n16 → n15 → n14 → n12 → n11 → n9 → n7 → n0

- B6: n1 → n16 → n15 → n14 → n12 → n11 → n9 → n8 → n7 → n0

- B7: n1 → n16 → n15 → n14 → n12 → n11 → n10 → n0


## cart.py: CartService.prepare

Source: [voicecart/cart.py:146](../voicecart/cart.py#L146), through line 185.

N=22, E=27, P=1. **E−N+2P = 27−22+2 = 7**. Predicate equivalents 6; **predicates+1 = 7**. Planar embedding has **7 regions** including the exterior.

Input/design bank: New live command, same fingerprint replay, other session/fingerprint, superseded turn, another prepared operation, ID already used by adjustment; tests/test_cart.py, tests/test_web_customer.py. Structural path coverage beyond measured branches is Not Run.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L147: context exit: normal"]

 n3["L147: context exit: return"]

 n4["L147: context exit: explicit error"]

 n5["L176: connection.execute('INSERT INTO commands(operation_id,session_id,turn_id,fingerprint,payload,status) VALUES (%s,%s,%s,%s,%s,'prepared')', (command.operation_id, command.session_id,"]

 n6["L175: raise CartError('resolve_previous_operation_first')"]

 n7["L174: test pending"]

 n8["L170: pending = connection.execute('SELECT operation_id FROM commands WHERE session_id=%s AND status='prepared'', (command.session_id,)).fetchone()"]

 n9["L169: raise CartError('turn_cancelled_or_superseded')"]

 n10["L168: test str(session['active_turn']) != command.turn_id"]

 n11["L167: return"]

 n12["L166: raise CartError('operation_identity_conflict')"]

 n13["L164: test existing['fingerprint'] != command.fingerprint"]

 n14["L163: test str(existing['session_id']) != command.session_id"]

 n15["L161: test existing"]

 n16["L158: existing = connection.execute('SELECT * FROM commands WHERE operation_id=%s', (command.operation_id,)).fetchone()"]

 n17["L157: raise CartError('operation_identity_conflict')"]

 n18["L153: test connection.execute('SELECT 1 FROM cart_adjustments WHERE operation_id=%s', (command.operation_id,)).fetchone()"]

 n19["L149: connection.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))', (command.operation_id,))"]

 n20["L148: session = self.sessions.require(connection, command.session_id, lock=True)"]

 n21["L147: context enter self.database.connect()"]

 n1 -->|next| n21

 n2 -->|next| n0

 n3 -->|next| n0

 n4 -->|next| n0

 n5 -->|next| n2

 n6 -->|next| n4

 n7 -->|T| n6

 n7 -->|F| n5

 n8 -->|next| n7

 n9 -->|next| n4

 n10 -->|T| n9

 n10 -->|F| n8

 n11 -->|next| n3

 n12 -->|next| n4

 n13 -->|T| n12

 n13 -->|F| n11

 n14 -->|T| n12

 n14 -->|F| n13

 n15 -->|T| n14

 n15 -->|F| n10

 n16 -->|next| n15

 n17 -->|next| n4

 n18 -->|T| n17

 n18 -->|F| n16

 n19 -->|next| n18

 n20 -->|next| n19

 n21 -->|next| n20

```

Structural independent basis (execution status as above):

- B1: n1 → n21 → n20 → n19 → n18 → n17 → n4 → n0

- B2: n1 → n21 → n20 → n19 → n18 → n16 → n15 → n10 → n8 → n7 → n5 → n2 → n0

- B3: n1 → n21 → n20 → n19 → n18 → n16 → n15 → n14 → n13 → n11 → n3 → n0

- B4: n1 → n21 → n20 → n19 → n18 → n16 → n15 → n10 → n8 → n7 → n6 → n4 → n0

- B5: n1 → n21 → n20 → n19 → n18 → n16 → n15 → n10 → n9 → n4 → n0

- B6: n1 → n21 → n20 → n19 → n18 → n16 → n15 → n14 → n12 → n4 → n0

- B7: n1 → n21 → n20 → n19 → n18 → n16 → n15 → n14 → n13 → n12 → n4 → n0


## sessions.py: SessionStore.create

Source: [voicecart/sessions.py:51](../voicecart/sessions.py#L51), through line 61.

N=10, E=10, P=1. **E−N+2P = 10−10+2 = 2**. Predicate equivalents 1; **predicates+1 = 2**. Planar embedding has **2 regions** including the exterior.

Input/design bank: ttl 0/59/60/86400/86401; tests/test_syllabus.py. DB failures separately injected in transaction tests.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L61: return identifier"]

 n3["L56: context exit: normal"]

 n6["L57: connection.execute('INSERT INTO sessions(session_id,expires_at) VALUES (%s,%s)', (identifier, datetime.now(UTC) + timedelta(seconds=ttl_seconds)))"]

 n7["L56: context enter self.database.connect()"]

 n8["L55: identifier = str(uuid.uuid4())"]

 n9["L54: raise SessionError('Session lifetime is at most one day')"]

 n10["L53: test ttl_seconds &gt; 86400"]

 n11["L52: require_integer(ttl_seconds, 'ttl_seconds', 60)"]

 n1 -->|next| n11

 n2 -->|next| n0

 n3 -->|next| n2

 n6 -->|next| n3

 n7 -->|next| n6

 n8 -->|next| n7

 n9 -->|next| n0

 n10 -->|T| n9

 n10 -->|F| n8

 n11 -->|next| n10

```

Structural independent basis (execution status as above):

- B1: n1 → n11 → n10 → n9 → n0

- B2: n1 → n11 → n10 → n8 → n7 → n6 → n3 → n2 → n0


## audio.py: _interval

Source: [voicecart/audio.py:28](../voicecart/audio.py#L28), through line 31.

N=7, E=9, P=1. **E−N+2P = 9−7+2 = 4**. Predicate equivalents 3; **predicates+1 = 4**. Planar embedding has **4 regions** including the exterior.

Input/design bank: missing/bool/nonfinite/huge integer endpoints, reversed endpoints, equal timestamps, ordered timestamps; tests/test_audio.py.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L31: return end - start"]

 n3["L30: return None"]

 n4["L29: test end &lt; start"]

 n5["L29: test _finite_time(end)"]

 n6["L29: test _finite_time(start)"]

 n1 -->|next| n6

 n2 -->|next| n0

 n3 -->|next| n0

 n4 -->|T| n3

 n4 -->|F| n2

 n5 -->|T| n4

 n5 -->|F| n3

 n6 -->|T| n5

 n6 -->|F| n3

```

Structural independent basis (execution status as above):

- B1: n1 → n6 → n3 → n0

- B2: n1 → n6 → n5 → n4 → n2 → n0

- B3: n1 → n6 → n5 → n4 → n3 → n0

- B4: n1 → n6 → n5 → n3 → n0


## voice.py: FileArtifact.verify

Source: [voicecart/voice.py:38](../voicecart/voice.py#L38), through line 49.

N=13, E=16, P=1. **E−N+2P = 16−13+2 = 5**. Predicate equivalents 4; **predicates+1 = 5**. Planar embedding has **5 regions** including the exterior.

Input/design bank: invalid digest, missing file, empty file, one byte, exactly one read chunk, two read chunks, hash mismatch; tests/test_syllabus.py and tests/test_voice_delivery.py.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L49: return self.path"]

 n3["L48: raise VoiceError('Local artifact integrity check failed')"]

 n4["L47: test digest.hexdigest() != self.sha256"]

 n5["L44: context exit: normal"]

 n8["L45: loop (chunk := source.read(1024 * 1024))"]

 n9["L46: digest.update(chunk)"]

 n10["L44: context enter self.path.open('rb')"]

 n11["L43: digest = hashlib.sha256()"]

 n12["L42: raise VoiceError('A lowercase SHA-256 artifact digest is required')"]

 n13["L39: test any((character not in '0123456789abcdef' for character in self.sha256))"]

 n14["L39: test len(self.sha256) != 64"]

 n1 -->|next| n14

 n2 -->|next| n0

 n3 -->|next| n0

 n4 -->|T| n3

 n4 -->|F| n2

 n5 -->|next| n4

 n8 -->|iteration| n9

 n8 -->|done| n5

 n9 -->|next| n8

 n10 -->|next| n8

 n11 -->|next| n10

 n12 -->|next| n0

 n13 -->|T| n12

 n13 -->|F| n11

 n14 -->|T| n12

 n14 -->|F| n13

```

Structural independent basis (execution status as above):

- B1: n1 → n14 → n12 → n0

- B2: n1 → n14 → n13 → n11 → n10 → n8 → n5 → n4 → n2 → n0

- B3: n1 → n14 → n13 → n11 → n10 → n8 → n5 → n4 → n3 → n0

- B4: n1 → n14 → n13 → n11 → n10 → n8 → n9 → n8 → n5 → n4 → n2 → n0

- B5: n1 → n14 → n13 → n12 → n0


## catalogue.py: qualify

Source: [voicecart/catalogue.py:44](../voicecart/catalogue.py#L44), through line 99.

N=45, E=63, P=1. **E−N+2P = 63−45+2 = 20**. Predicate equivalents 19; **predicates+1 = 20**. Planar embedding has **20 regions** including the exterior.

Input/design bank: Active/inactive, each matching/mismatching/unknown attribute, available/false/unknown, stock below/equal/above quantity, missing/stale/current price, currency mismatch and LT/LTE boundary; tests/test_catalogue.py and tests/test_syllabus.py.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L99: return Qualification(Eligibility.QUALIFIED)"]

 n3["L98: return Qualification(Eligibility.UNKNOWN, tuple(unknown))"]

 n4["L97: test unknown"]

 n5["L96: return Qualification(Eligibility.REJECTED, tuple(rejected + unknown))"]

 n6["L95: test rejected"]

 n7["L81: unknown.append(issue(IssueCode.MISSING_PRICE, 'Price/currency is missing'))"]

 n8["L88: unknown.append(issue(code, 'A current price is not verified'))"]

 n9["L83: code = IssueCode.STALE_PRICE if variant.price_freshness is Freshness.STALE else IssueCode.UNKNOWN_PRICE_FRESHNESS"]

 n10["L83: evaluate IssueCode.STALE_PRICE"]

 n11["L83: evaluate IssueCode.UNKNOWN_PRICE_FRESHNESS"]

 n12["L85: test variant.price_freshness is Freshness.STALE"]

 n13["L90: rejected.append(issue(IssueCode.CURRENCY_MISMATCH, 'Different currency'))"]

 n14["L93: rejected.append(issue(IssueCode.OVER_BUDGET, 'Unit price fails budget'))"]

 n15["L92: test constraints.price_limit.permits(variant.price)"]

 n16["L91: test constraints.price_limit is not None"]

 n17["L89: test variant.price.currency != constraints.currency"]

 n18["L82: test variant.price_freshness is not Freshness.CURRENT"]

 n19["L80: test variant.price is None"]

 n20["L74: rejected.append(issue(IssueCode.INSUFFICIENT_STOCK, 'Insufficient quantity'))"]

 n21["L73: test variant.stock_quantity &lt; constraints.quantity"]

 n22["L78: unknown.append(issue(IssueCode.UNKNOWN_STOCK, 'Multi-unit stock is unknown'))"]

 n23["L77: test constraints.quantity &gt; 1"]

 n24["L72: test variant.stock_quantity is not None"]

 n25["L69: rejected.append(issue(IssueCode.UNAVAILABLE, 'Variant is not available'))"]

 n26["L71: unknown.append(issue(IssueCode.UNKNOWN_AVAILABILITY, 'Availability is unknown'))"]

 n27["L70: test variant.available is None"]

 n28["L68: test variant.available is False"]

 n29["L55: loop next (field, actual) from (('category', product.category), ('colour', variant.colour), ('size', variant.size))"]

 n30["L64: unknown.append(issue(IssueCode.UNKNOWN_ATTRIBUTE, f'Unknown {field}'))"]

 n31["L66: rejected.append(issue(IssueCode.ATTRIBUTE_MISMATCH, f'Different {field}'))"]

 n32["L65: test actual != expected"]

 n33["L63: test actual is None"]

 n34["L62: continue"]

 n35["L61: test expected is None"]

 n36["L60: expected = getattr(constraints, field)"]

 n37["L54: rejected.append(issue(IssueCode.INACTIVE, 'Product or variant is inactive'))"]

 n38["L53: test variant.active"]

 n39["L53: test product.active"]

 n40["L50: def issue(code: IssueCode, detail: str) -&gt; SearchIssue:"]

 n41["L48: unknown: list[SearchIssue] = []"]

 n42["L47: rejected: list[SearchIssue] = []"]

 n43["L46: product, variant = (item.product, item.variant)"]

 n44["L45: 'Combine predicates as three-valued AND: a known false dominates unknowns.'"]

 n1 -->|next| n44

 n2 -->|next| n0

 n3 -->|next| n0

 n4 -->|T| n3

 n4 -->|F| n2

 n5 -->|next| n0

 n6 -->|T| n5

 n6 -->|F| n4

 n7 -->|next| n6

 n8 -->|next| n6

 n9 -->|next| n8

 n10 -->|next| n9

 n11 -->|next| n9

 n12 -->|T| n10

 n12 -->|F| n11

 n13 -->|next| n6

 n14 -->|next| n6

 n15 -->|T| n6

 n15 -->|F| n14

 n16 -->|T| n15

 n16 -->|F| n6

 n17 -->|T| n13

 n17 -->|F| n16

 n18 -->|T| n12

 n18 -->|F| n17

 n19 -->|T| n7

 n19 -->|F| n18

 n20 -->|next| n19

 n21 -->|T| n20

 n21 -->|F| n19

 n22 -->|next| n19

 n23 -->|T| n22

 n23 -->|F| n19

 n24 -->|T| n21

 n24 -->|F| n23

 n25 -->|next| n24

 n26 -->|next| n24

 n27 -->|T| n26

 n27 -->|F| n24

 n28 -->|T| n25

 n28 -->|F| n27

 n29 -->|iteration| n36

 n29 -->|done| n28

 n30 -->|next| n29

 n31 -->|next| n29

 n32 -->|T| n31

 n32 -->|F| n29

 n33 -->|T| n30

 n33 -->|F| n32

 n34 -->|next| n29

 n35 -->|T| n34

 n35 -->|F| n33

 n36 -->|next| n35

 n37 -->|next| n29

 n38 -->|T| n29

 n38 -->|F| n37

 n39 -->|T| n38

 n39 -->|F| n37

 n40 -->|next| n39

 n41 -->|next| n40

 n42 -->|next| n41

 n43 -->|next| n42

 n44 -->|next| n43

```

Structural independent basis (execution status as above):

- B1: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n19 → n7 → n6 → n5 → n0

- B2: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n19 → n7 → n6 → n4 → n2 → n0

- B3: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n19 → n7 → n6 → n4 → n3 → n0

- B4: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n19 → n18 → n12 → n10 → n9 → n8 → n6 → n5 → n0

- B5: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n19 → n18 → n12 → n11 → n9 → n8 → n6 → n5 → n0

- B6: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n19 → n18 → n17 → n13 → n6 → n5 → n0

- B7: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n19 → n18 → n17 → n16 → n15 → n14 → n6 → n5 → n0

- B8: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n19 → n18 → n17 → n16 → n15 → n6 → n5 → n0

- B9: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n19 → n18 → n17 → n16 → n6 → n5 → n0

- B10: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n21 → n20 → n19 → n7 → n6 → n5 → n0

- B11: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n23 → n22 → n19 → n7 → n6 → n5 → n0

- B12: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n29 → n28 → n25 → n24 → n23 → n19 → n7 → n6 → n5 → n0

- B13: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n37 → n29 → n28 → n25 → n24 → n21 → n19 → n7 → n6 → n5 → n0

- B14: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n37 → n29 → n28 → n27 → n26 → n24 → n21 → n19 → n7 → n6 → n5 → n0

- B15: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n37 → n29 → n28 → n27 → n24 → n21 → n19 → n7 → n6 → n5 → n0

- B16: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n37 → n29 → n36 → n35 → n34 → n29 → n28 → n25 → n24 → n21 → n19 → n7 → n6 → n5 → n0

- B17: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n37 → n29 → n36 → n35 → n33 → n30 → n29 → n28 → n25 → n24 → n21 → n19 → n7 → n6 → n5 → n0

- B18: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n37 → n29 → n36 → n35 → n33 → n32 → n31 → n29 → n28 → n25 → n24 → n21 → n19 → n7 → n6 → n5 → n0

- B19: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n37 → n29 → n36 → n35 → n33 → n32 → n29 → n28 → n25 → n24 → n21 → n19 → n7 → n6 → n5 → n0

- B20: n1 → n44 → n43 → n42 → n41 → n40 → n39 → n38 → n37 → n29 → n28 → n25 → n24 → n21 → n19 → n7 → n6 → n5 → n0


## ingestion.py: exact_keys

Source: [voicecart/ingestion.py:44](../voicecart/ingestion.py#L44), through line 50.

N=6, E=8, P=1. **E−N+2P = 8−6+2 = 4**. Predicate equivalents 3; **predicates+1 = 4**. Planar embedding has **4 regions** including the exterior.

Input/design bank: Nonobject, missing required field, unsupported extra key, valid required-only, valid optional fields; tests/test_persistence.py and tests/test_dataset.py.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L50: raise ValueError('Missing or unsupported fields')"]

 n3["L48: test set(value) - required - optional"]

 n4["L47: test required &lt;= set(value)"]

 n5["L46: test isinstance(value, dict)"]

 n1 -->|next| n5

 n2 -->|next| n0

 n3 -->|T| n2

 n3 -->|F| n0

 n4 -->|T| n3

 n4 -->|F| n2

 n5 -->|T| n4

 n5 -->|F| n2

```

Structural independent basis (execution status as above):

- B1: n1 → n5 → n2 → n0

- B2: n1 → n5 → n4 → n3 → n2 → n0

- B3: n1 → n5 → n4 → n3 → n0

- B4: n1 → n5 → n4 → n2 → n0


## database.py: Database.check_ready

Source: [voicecart/database.py:140](../voicecart/database.py#L140), through line 170.

N=14, E=17, P=1. **E−N+2P = 17−14+2 = 5**. Predicate equivalents 4; **predicates+1 = 5**. Planar embedding has **5 regions** including the exterior.

Input/design bank: Migrated pgvector database versus missing schema/extension; real service tests and explicit startup checks. Missing-extension injection on maintained deployment is Not Run.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L141: context exit: normal"]

 n4["L141: context exit: explicit error"]

 n5["L168: raise DatabaseUnavailable('pgvector extension is unavailable; run explicit migrations')"]

 n6["L167: test extension"]

 n7["L164: extension = connection.execute('SELECT extversion FROM pg_extension WHERE extname='vector'').fetchone()"]

 n8["L161: connection.execute('SELECT revision FROM catalogue_state WHERE singleton=true').fetchone()"]

 n9["L148: loop next migration from resources.files('voicecart').joinpath('migrations').iterdir()"]

 n10["L158: raise DatabaseUnavailable('Schema requires explicit checksummed migrations; run init-db')"]

 n11["L153: test applied.get(migration.name) != hashlib.sha256(migration.read_text(encoding='utf-8').encode()).hexdigest()"]

 n12["L152: test migration.name.endswith('.sql')"]

 n13["L142: applied = {row['version']: row['sha256'] for row in connection.execute('SELECT version,sha256 FROM schema_migrations')}"]

 n14["L141: context enter self.connect()"]

 n1 -->|next| n14

 n2 -->|next| n0

 n4 -->|next| n0

 n5 -->|next| n4

 n6 -->|T| n2

 n6 -->|F| n5

 n7 -->|next| n6

 n8 -->|next| n7

 n9 -->|iteration| n12

 n9 -->|done| n8

 n10 -->|next| n4

 n11 -->|T| n10

 n11 -->|F| n9

 n12 -->|T| n11

 n12 -->|F| n9

 n13 -->|next| n9

 n14 -->|next| n13

```

Structural independent basis (execution status as above):

- B1: n1 → n14 → n13 → n9 → n12 → n11 → n10 → n4 → n0

- B2: n1 → n14 → n13 → n9 → n8 → n7 → n6 → n2 → n0

- B3: n1 → n14 → n13 → n9 → n8 → n7 → n6 → n5 → n4 → n0

- B4: n1 → n14 → n13 → n9 → n12 → n11 → n9 → n12 → n11 → n10 → n4 → n0

- B5: n1 → n14 → n13 → n9 → n12 → n9 → n12 → n11 → n10 → n4 → n0


## merchant.py: LocalMerchantAdapter.synchronize

Source: [voicecart/merchant.py:90](../voicecart/merchant.py#L90), through line 93.

N=3, E=2, P=1. **E−N+2P = 2−3+2 = 1**. Predicate equivalents 0; **predicates+1 = 1**. Planar embedding has **1 regions** including the exterior.

Input/design bank: Valid full snapshot versus stale expected revision; tests/test_admin.py and tests/test_persistence.py; one forwarding path delegates to tested publication.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n2["L91: return self.database.publish(snapshot, encoder=self.application.catalogue.encoder)"]

 n1 -->|next| n2

 n2 -->|next| n0

```

Structural independent basis (execution status as above):

- B1: n1 → n2 → n0


## http_security.py: RateLimiter.allow

Source: [voicecart/http_security.py:90](../voicecart/http_security.py#L90), through line 99.

N=15, E=17, P=1. **E−N+2P = 17−15+2 = 4**. Predicate equivalents 3; **predicates+1 = 4**. Planar embedding has **4 regions** including the exterior.

Input/design bank: Window counts 0/1/limit/limit+1, 59.999/60 seconds, 5000 distinct keys triggering storage eviction; tests/test_http_foundation.py.

```mermaid

flowchart TD

 n0["L0: Exit (return or propagated explicit error)"]

 n1["L0: Entry"]

 n3["L92: context exit: return"]

 n5["L99: return count &lt; limit"]

 n6["L97: loop len(self.windows) &gt; 4096"]

 n7["L98: self.windows.popitem(last=False)"]

 n8["L96: self.windows[key] = (start, count + 1)"]

 n9["L95: start, count = (now, 0)"]

 n10["L94: test now - start &gt;= 60"]

 n11["L93: start, count = self.windows.pop(key, (now, 0))"]

 n12["L92: context enter self.lock"]

 n13["L91: now = time.monotonic() if now is None else now"]

 n14["L91: evaluate time.monotonic()"]

 n15["L91: evaluate now"]

 n16["L91: test now is None"]

 n1 -->|next| n16

 n3 -->|next| n0

 n5 -->|next| n3

 n6 -->|iteration| n7

 n6 -->|done| n5

 n7 -->|next| n6

 n8 -->|next| n6

 n9 -->|next| n8

 n10 -->|T| n9

 n10 -->|F| n8

 n11 -->|next| n10

 n12 -->|next| n11

 n13 -->|next| n12

 n14 -->|next| n13

 n15 -->|next| n13

 n16 -->|T| n14

 n16 -->|F| n15

```

Structural independent basis (execution status as above):

- B1: n1 → n16 → n14 → n13 → n12 → n11 → n10 → n8 → n6 → n5 → n3 → n0

- B2: n1 → n16 → n14 → n13 → n12 → n11 → n10 → n8 → n6 → n7 → n6 → n5 → n3 → n0

- B3: n1 → n16 → n14 → n13 → n12 → n11 → n10 → n9 → n8 → n6 → n5 → n3 → n0

- B4: n1 → n16 → n15 → n13 → n12 → n11 → n10 → n8 → n6 → n5 → n3 → n0
