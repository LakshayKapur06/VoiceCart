"""Generate source-level CFGs, planar faces and structural independent paths.

Explicit Python decisions/loops/returns/raises and context exits are represented.
Implicit faults inside external calls and nested callable/comprehension frames are
outside the intraprocedural model, not claimed exception/path coverage.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import networkx as nx

TARGETS = {
    "application.py": ["money_text"],
    "nlu.py": ["rupees_to_minor"],
    "search.py": ["item_price"],
    "ranking.py": ["rank_qualified"],
    "cart.py": ["CartService.prepare"],
    "sessions.py": ["SessionStore.create"],
    "audio.py": ["_interval"],
    "voice.py": ["FileArtifact.verify"],
    "catalogue.py": ["qualify"],
    "ingestion.py": ["exact_keys"],
    "database.py": ["Database.check_ready"],
    "merchant.py": ["LocalMerchantAdapter.synchronize"],
    "http_security.py": ["RateLimiter.allow"],
}
INPUTS = {
    "rupees_to_minor": "0, 0.01, 1,000, 1,00,000.50, two thousand, malformed punctuation, negative/nonfinite and input longer than 100 characters; tests/test_nlu.py and tests/test_syllabus.py. Parser normal/handled failure paths are explicit; nested whole_number loop tests are separately documented.",
    "money_text": "INR 100, INR 101, USD 100; tests/test_application.py confirmation/system assertions.",
    "whole_number": "0; one; twenty one; one hundred and five; two thousand three hundred forty five; empty; and one; one one; hundred; one thousand thousand; one and one; twenty twenty. tests/test_syllabus.py and tests/test_nlu.py. Additional structurally infeasible combinations are not claimed executed.",
    "item_price": "Qualified priced fixture versus price=None; tests/test_persistence.py and tests/test_catalogue.py.",
    "rank_qualified": "Valid permutation, empty/non-string version, changed version, list output, non-string ID, duplicate/missing/injected IDs; tests/test_ranking.py.",
    "CartService.prepare": "New live command, same fingerprint replay, other session/fingerprint, superseded turn, another prepared operation, ID already used by adjustment; tests/test_cart.py, tests/test_web_customer.py. Structural path coverage beyond measured branches is Not Run.",
    "SessionStore.create": "ttl 0/59/60/86400/86401; tests/test_syllabus.py. DB failures separately injected in transaction tests.",
    "_interval": "missing/bool/nonfinite/huge integer endpoints, reversed endpoints, equal timestamps, ordered timestamps; tests/test_audio.py.",
    "FileArtifact.verify": "invalid digest, missing file, empty file, one byte, exactly one read chunk, two read chunks, hash mismatch; tests/test_syllabus.py and tests/test_voice_delivery.py.",
    "qualify": "Active/inactive, each matching/mismatching/unknown attribute, available/false/unknown, stock below/equal/above quantity, missing/stale/current price, currency mismatch and LT/LTE boundary; tests/test_catalogue.py and tests/test_syllabus.py.",
    "exact_keys": "Nonobject, missing required field, unsupported extra key, valid required-only, valid optional fields; tests/test_persistence.py and tests/test_dataset.py.",
    "Database.check_ready": "Migrated pgvector database versus missing schema/extension; real service tests and explicit startup checks. Missing-extension injection on maintained deployment is Not Run.",
    "LocalMerchantAdapter.synchronize": "Valid full snapshot versus stale expected revision; tests/test_admin.py and tests/test_persistence.py; one forwarding path delegates to tested publication.",
    "RateLimiter.allow": "Window counts 0/1/limit/limit+1, 59.999/60 seconds, 5000 distinct keys triggering storage eviction; tests/test_http_foundation.py.",
}


class CFG:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.exit = self.node("Exit (return or propagated explicit error)", 0)
        self.entry = self.node("Entry", 0)

    def node(self, label, line):
        identifier = len(self.graph)
        self.graph.add_node(identifier, label=label[:180], line=line)
        return identifier

    def edge(self, source, target, label=""):
        self.graph.add_edge(source, target, label=label)

    def predicate(self, test, yes, no):
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            return self.predicate(test.operand, no, yes)
        if isinstance(test, ast.BoolOp):
            following = yes if isinstance(test.op, ast.And) else no
            for value in reversed(test.values):
                following = (
                    self.predicate(value, following, no)
                    if isinstance(test.op, ast.And)
                    else self.predicate(value, yes, following)
                )
            return following
        if isinstance(test, ast.Compare) and len(test.ops) > 1:
            operands = [test.left, *test.comparators]
            following = yes
            for index in reversed(range(len(test.ops))):
                comparison = ast.copy_location(
                    ast.Compare(
                        left=operands[index],
                        ops=[test.ops[index]],
                        comparators=[operands[index + 1]],
                    ),
                    test,
                )
                following = self.predicate(comparison, following, no)
            return following
        node = self.node("test " + ast.unparse(test), test.lineno)
        self.edge(node, yes, "T")
        self.edge(node, no, "F")
        return node

    def block(self, statements, following, ret=None, error=None, brk=None, cont=None):
        ret = self.exit if ret is None else ret
        error = self.exit if error is None else error
        for statement in reversed(statements):
            line = getattr(statement, "lineno", 0)
            if isinstance(statement, ast.If):
                yes = self.block(statement.body, following, ret, error, brk, cont)
                no = self.block(statement.orelse, following, ret, error, brk, cont)
                following = self.predicate(statement.test, yes, no)
            elif isinstance(statement, (ast.For, ast.While)):
                loop = self.node(
                    "loop "
                    + (
                        ast.unparse(statement.test)
                        if isinstance(statement, ast.While)
                        else "next "
                        + ast.unparse(statement.target)
                        + " from "
                        + ast.unparse(statement.iter)
                    ),
                    line,
                )
                normal = self.block(statement.orelse, following, ret, error, brk, cont)
                body = self.block(statement.body, loop, ret, error, following, loop)
                self.edge(loop, body, "iteration")
                self.edge(loop, normal, "done")
                following = loop
            elif isinstance(statement, ast.With):
                normal = self.node("context exit: normal", line)
                self.edge(normal, following)
                returned = self.node("context exit: return", line)
                self.edge(returned, ret)
                raised = self.node("context exit: explicit error", line)
                self.edge(raised, error)
                body = self.block(statement.body, normal, returned, raised, brk, cont)
                opened = self.node(
                    "context enter "
                    + ", ".join(
                        ast.unparse(item.context_expr) for item in statement.items
                    ),
                    line,
                )
                self.edge(opened, body)
                following = opened
            elif isinstance(statement, ast.Try):
                # Selected target rank_qualified has one typed handler. Model its
                # explicit normal/handled completion, not all possible call faults.
                normal = self.block(statement.orelse, following, ret, error, brk, cont)
                handlers = [
                    self.block(handler.body, following, ret, error, brk, cont)
                    for handler in statement.handlers
                ]
                body = self.block(
                    statement.body,
                    normal,
                    ret,
                    handlers[0] if handlers else error,
                    brk,
                    cont,
                )
                guard = self.node("try: normal or declared handled exception", line)
                self.edge(guard, body, "normal")
                for index, handler in enumerate(handlers):
                    self.edge(guard, handler, "handler " + str(index))
                following = guard
            else:
                label = ast.unparse(statement).split("\n")[0]
                node = self.node(label, line)
                target = (
                    ret
                    if isinstance(statement, ast.Return)
                    else error
                    if isinstance(statement, ast.Raise)
                    else brk
                    if isinstance(statement, ast.Break)
                    else cont
                    if isinstance(statement, ast.Continue)
                    else following
                )
                self.edge(node, self.exit if target is None else target)
                # Conditional expressions within a return have actual alternatives.
                condition = next(
                    (
                        part
                        for part in ast.walk(statement)
                        if isinstance(part, ast.IfExp)
                    ),
                    None,
                )
                if condition is not None:
                    yes = self.node("evaluate " + ast.unparse(condition.body), line)
                    self.edge(yes, node)
                    no = self.node("evaluate " + ast.unparse(condition.orelse), line)
                    self.edge(no, node)
                    following = self.predicate(condition.test, yes, no)
                else:
                    following = node
        return following

    def finish(self, function):
        start = self.block(function.body, self.exit)
        self.edge(self.entry, start)
        keep = nx.descendants(self.graph, self.entry) | {self.entry}
        self.graph = self.graph.subgraph(keep).copy()
        return self.graph


def function(tree, name):
    node = tree
    for piece in name.split("."):
        node = next(
            item
            for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.ClassDef)) and item.name == piece
        )
    return node


def paths(graph, entry, exit_node):
    edges = list(graph.edges)
    positions = {edge: index for index, edge in enumerate(edges)}
    basis = {}
    selected = []
    candidates = [nx.shortest_path(graph, entry, exit_node)]
    for a, b in edges:
        try:
            candidates.append(
                nx.shortest_path(graph, entry, a)
                + [b]
                + nx.shortest_path(graph, b, exit_node)[1:]
            )
        except nx.NetworkXNoPath:
            continue
    for path in candidates:
        vector = 0
        for edge in zip(path, path[1:], strict=False):
            vector ^= 1 << positions[edge]
        remaining = vector
        while remaining:
            pivot = remaining.bit_length() - 1
            if pivot in basis:
                remaining ^= basis[pivot]
            else:
                basis[pivot] = remaining
                selected.append(path)
                break
    return selected


def main():
    output = [
        "# Source-level control-flow analysis",
        "Generated from actual current source. Nodes include explicit decisions, short-circuit Boolean tests, loops, returns/raises and context cleanup. Nested callable/comprehension frames and arbitrary implicit faults inside external calls are outside this intraprocedural convention. Declared try handlers are represented; this is not a claim of exhaustive exception/path coverage.",
        "Each listed basis is a structural GF(2) edge-independent entry/exit path set. Logical feasibility and concrete input execution are separate: refer to the input bank and measured branch report. Unexecuted/infeasible candidate paths are **Not Run**, never presented as achieved path coverage. Regions are actual faces enumerated from a planar embedding when available, including the exterior. Predicate equivalents sum outdegree−1 for multiway nodes.",
    ]
    results = []
    for filename, names in TARGETS.items():
        source = Path("voicecart") / filename
        tree = ast.parse(source.read_text())
        for name in names:
            selected = function(tree, name)
            cfg = CFG()
            graph = cfg.finish(selected)
            n = graph.number_of_nodes()
            e = graph.number_of_edges()
            complexity = e - n + 2
            predicates = sum(max(0, graph.out_degree(node) - 1) for node in graph)
            drawing = nx.Graph()
            drawing.add_nodes_from(graph.nodes)
            # Preserve opposite directed edges/self loops in the planar drawing.
            # Subdivision changes E and N equally, preserving the cycle rank/faces.
            for index, (a, b) in enumerate(graph.edges):
                first, second = f"edge-{index}-a", f"edge-{index}-b"
                drawing.add_edges_from([(a, first), (first, second), (second, b)])
            planar, embedding = nx.check_planarity(drawing)
            faces = []
            if planar:
                seen = set()
                for u, v in embedding.edges():
                    if (u, v) not in seen:
                        faces.append(embedding.traverse_face(u, v, seen))
            basis = paths(graph, cfg.entry, cfg.exit)
            result = {
                "file": str(source),
                "function": name,
                "start_line": selected.lineno,
                "end_line": selected.end_lineno,
                "nodes": n,
                "edges": e,
                "components": 1,
                "edge_node_complexity": complexity,
                "predicate_equivalents": predicates,
                "predicate_complexity": predicates + 1,
                "planar": planar,
                "region_count": len(faces) if planar else None,
                "basis_paths": basis,
                "basis_rank": len(basis),
                "basis_execution": "Not inferred; concrete source tests/coverage are separate",
                "nodes_detail": {
                    str(key): value for key, value in graph.nodes(data=True)
                },
                "edges_detail": [
                    [a, b, data.get("label", "")]
                    for a, b, data in graph.edges(data=True)
                ],
            }
            if complexity != predicates + 1 or len(basis) != complexity:
                raise RuntimeError("CFG algebra verification failed " + name)
            if planar and len(faces) != complexity:
                raise RuntimeError("Face count differs " + name)
            results.append(result)
            output += [
                f"\n## {filename}: {name}",
                f"Source: [{source}:{selected.lineno}](../{source}#L{selected.lineno}), through line {selected.end_lineno}.",
                f"N={n}, E={e}, P=1. **E−N+2P = {e}−{n}+2 = {complexity}**. Predicate equivalents {predicates}; **predicates+1 = {predicates + 1}**. "
                + (
                    f"Planar embedding has **{len(faces)} regions** including the exterior."
                    if planar
                    else "Graph is nonplanar; planar-region counting is not applicable and is not fabricated."
                ),
                "Input/design bank: " + INPUTS[name],
                "```mermaid",
                "flowchart TD",
            ]
            for key, data in graph.nodes(data=True):
                label = (
                    (f"L{data['line']}: " + data["label"])
                    .replace('"', "'")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", " ")
                )
                output.append(f' n{key}["{label}"]')
            for a, b, data in graph.edges(data=True):
                output.append(f" n{a} -->|{data.get('label') or 'next'}| n{b}")
            output += [
                "```",
                "Structural independent basis (execution status as above):",
            ] + [
                f"- B{index + 1}: " + " → ".join("n" + str(node) for node in path)
                for index, path in enumerate(basis)
            ]
    Path("docs/CFG_ANALYSIS.md").write_text("\n\n".join(output) + "\n")
    Path("docs/evidence/CFG_20261102.json").write_text(
        json.dumps(results, indent=2) + "\n"
    )
    print(
        "Verified",
        len(results),
        "actual-source CFGs; planar functions",
        sum(row["planar"] for row in results),
    )


if __name__ == "__main__":
    main()
