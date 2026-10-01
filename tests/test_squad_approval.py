"""Spec Squad review loop: a Reviewer approval and a round-limit approval
must be told apart in the state file, the turn log and the SSE stream.

The agents are replaced by a fake, so no model is called.
"""
import asyncio
import json
import queue
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from clawd_lobster import squad


def signal(data):
    return "```json\n" + json.dumps(data) + "\n```"


def fake_agents(approve_in_round=None):
    """A stand-in for squad._run_agent. The Reviewer approves in the given round."""
    rounds = {"n": 0}

    async def run_agent(role, system_prompt, prompt, workspace, allowed_tools=None):
        if role == "reviewer":
            rounds["n"] += 1
            if rounds["n"] == approve_in_round:
                return signal({"verdict": "APPROVED", "confidence": 0.9})
            return signal({"verdict": "NEEDS_REVISION", "issues": ["missing error handling"]})
        return signal({"status": "done"})

    return run_agent


def drain_sse():
    events = []
    q = squad.get_sse_queue()
    while True:
        try:
            events.append(json.loads(q.get_nowait()))
        except queue.Empty:
            return events


class TestReviewLoop(unittest.TestCase):

    def run_squad(self, approve_in_round):
        drain_sse()
        with tempfile.TemporaryDirectory() as ws, \
             patch.object(squad, "_run_agent", fake_agents(approve_in_round)):
            asyncio.run(squad._run_squad_async(Path(ws), "a small app", plan_only=True))
            state = squad.load_state(Path(ws))
        return state, drain_sse()

    def test_reviewer_approval_is_recorded_as_such(self):
        state, events = self.run_squad(approve_in_round=2)
        self.assertTrue(state["approved"])
        self.assertEqual(state["approval"], "reviewer")
        self.assertEqual(state["review_round"], 2)
        self.assertNotIn("system", [t["role"] for t in state["turns"]])
        self.assertNotIn("forced_approval", [e["event"] for e in events])
        self.assertEqual(squad.approval_source(state), "reviewer")
        self.assertEqual(squad.approval_label(state), "approved by the Reviewer")

    def test_round_limit_approval_is_recorded_as_forced(self):
        state, events = self.run_squad(approve_in_round=None)
        self.assertTrue(state["approved"])  # the pipeline still goes on
        self.assertEqual(state["approval"], "round_limit")
        self.assertEqual(state["review_round"], squad.MAX_REVIEW_ROUNDS)
        last = state["turns"][-1]
        self.assertEqual(last["role"], "system")
        self.assertEqual(last["signal"], {"verdict": "FORCED_APPROVAL", "reason": "round_limit",
                                          "rounds": squad.MAX_REVIEW_ROUNDS,
                                          "max_rounds": squad.MAX_REVIEW_ROUNDS})
        forced = [e for e in events if e["event"] == "forced_approval"]
        self.assertEqual(forced, [{"event": "forced_approval",
                                   "rounds": squad.MAX_REVIEW_ROUNDS,
                                   "max_rounds": squad.MAX_REVIEW_ROUNDS}])
        self.assertIn("round limit", squad.approval_label(state))

    def test_approval_in_the_last_round_is_still_the_reviewers(self):
        state, events = self.run_squad(approve_in_round=squad.MAX_REVIEW_ROUNDS)
        self.assertEqual(state["approval"], "reviewer")
        self.assertNotIn("forced_approval", [e["event"] for e in events])


class TestOlderStateFiles(unittest.TestCase):
    """State files written before the "approval" field existed."""

    def test_classified_from_the_last_reviewer_verdict(self):
        reviewer_said_yes = {"approved": True, "turns": [
            {"role": "reviewer", "signal": {"verdict": "NEEDS_REVISION"}},
            {"role": "architect", "signal": {"status": "done"}},
            {"role": "reviewer", "signal": {"verdict": "APPROVED"}}]}
        limit_hit = {"approved": True, "turns": [
            {"role": "reviewer", "signal": {"verdict": "NEEDS_REVISION"}},
            {"role": "architect", "signal": None}]}
        no_signal = {"approved": True, "turns": [{"role": "reviewer", "signal": None}]}
        self.assertEqual(squad.approval_source(reviewer_said_yes), "reviewer")
        self.assertEqual(squad.approval_source(limit_hit), "round_limit")
        self.assertEqual(squad.approval_source(no_signal), "round_limit")

    def test_not_approved(self):
        self.assertIsNone(squad.approval_source({}))
        self.assertIsNone(squad.approval_source({"approved": False, "approval": "reviewer"}))
        self.assertEqual(squad.approval_label({"approved": False}), "not approved")


if __name__ == "__main__":
    unittest.main(verbosity=2)
