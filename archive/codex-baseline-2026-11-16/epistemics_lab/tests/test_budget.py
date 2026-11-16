import multiprocessing
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from budget import (BudgetLedger, RateCard, BudgetBlocked, BudgetExhausted,
                    BudgetConfigurationError)


def card():
    return RateCard('test-provider', 'test-model', '1.00', '2.00', 'test fixture rates')


def parallel_reserve(path, gate, result):
    ledger = BudgetLedger(path, '0.0000001', card())  # 100 nanodollars total
    gate.wait(10)
    try:
        ledger.reserve(10)
        result.put('reserved')
    except BudgetExhausted:
        result.put('exhausted')


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'spend.sqlite3'

    def tearDown(self):
        self.temp.cleanup()

    def test_decimal_rounding_is_conservative(self):
        rates = RateCard('p', 'm', '0.0000001', '0.0000001')
        self.assertEqual(rates.cost_nanos(1, 1), 2)
        self.assertEqual(card().cost_nanos(1000, 50), 1_100_000)
        with self.assertRaises(BudgetConfigurationError):
            rates.cost_nanos(True, 1)
        with self.assertRaises(BudgetConfigurationError):
            RateCard('p', 'm', 'NaN', '1')

    def test_arbitrary_precision_rates_are_not_rounded_down_or_merged(self):
        fine_rate = '1.' + '0' * 100 + '1'
        precise = RateCard('p', 'm', fine_rate, '0')
        self.assertEqual(precise.cost_nanos(1, 0), 1001)
        BudgetLedger(self.path, '1', precise)
        with self.assertRaises(BudgetConfigurationError):
            BudgetLedger(self.path, '1', RateCard('p', 'm', '1', '0'))

    def test_restart_preserves_pending_reservations(self):
        first = BudgetLedger(self.path, '0.0000001', card())
        rid = first.reserve(70)
        second = BudgetLedger(self.path, '0.0000001', card())
        self.assertEqual(second.snapshot()['reserved_nanos'], 70)
        with self.assertRaises(BudgetExhausted):
            second.reserve(31)
        second.settle(rid, 60)
        second.reserve(40)
        with self.assertRaises(BudgetExhausted):
            first.reserve(1)

    def test_no_reservation_over_budget_and_immutable_config(self):
        ledger = BudgetLedger(self.path, '0.0000001', card())
        with self.assertRaises(BudgetExhausted):
            ledger.reserve(101)
        self.assertEqual(ledger.snapshot()['reservations'], 0)
        with self.assertRaises(BudgetConfigurationError):
            BudgetLedger(self.path, '1', card())
        with self.assertRaises(BudgetConfigurationError):
            BudgetLedger(self.path, '0.0000001', RateCard('p', 'other', '1', '2'))
        with self.assertRaises(BudgetConfigurationError):
            BudgetLedger(Path(self.temp.name) / 'zero.sqlite3', '0', card())

    def test_missing_usage_fails_closed_across_restart(self):
        ledger = BudgetLedger(self.path, '1', card())
        rid = ledger.reserve(100)
        with self.assertRaises(BudgetBlocked):
            ledger.settle_usage(rid, None, 2)
        restarted = BudgetLedger(self.path, '1', card())
        self.assertEqual(restarted.snapshot()['reserved_nanos'], 100)
        self.assertEqual(restarted.snapshot()['spent_nanos'], 0)
        with self.assertRaises(BudgetBlocked):
            restarted.reserve(1)

    def test_uncertain_transport_outcome_keeps_full_reservation(self):
        ledger = BudgetLedger(self.path, '1', card())
        rid = ledger.reserve(100)
        with self.assertRaises(BudgetBlocked):
            ledger.abandon(rid, 'Timeout; provider may have charged')
        self.assertEqual(ledger.snapshot()['reserved_nanos'], 100)
        with self.assertRaises(BudgetBlocked):
            ledger.settle(rid, 0)
        self.assertEqual(ledger.snapshot()['reserved_nanos'], 100)

    def test_actual_excess_is_recorded_and_blocks(self):
        ledger = BudgetLedger(self.path, '0.0000001', card())
        rid = ledger.reserve(100)
        with self.assertRaises(BudgetBlocked):
            ledger.settle(rid, 120)
        self.assertEqual(ledger.snapshot()['spent_nanos'], 120)
        self.assertEqual(ledger.snapshot()['reserved_nanos'], 0)
        with self.assertRaises(BudgetBlocked):
            BudgetLedger(self.path, '0.0000001', card()).reserve(1)

    def test_repeat_settlement_is_idempotent_not_refundable(self):
        ledger = BudgetLedger(self.path, '1', card())
        rid = ledger.reserve(100)
        ledger.settle(rid, 75)
        ledger.settle(rid, 75)
        self.assertEqual(ledger.snapshot()['spent_nanos'], 75)
        with self.assertRaises(BudgetConfigurationError):
            ledger.settle(rid, 0)

    def test_parallel_processes_cannot_oversubscribe(self):
        BudgetLedger(self.path, '0.0000001', card())
        ctx = multiprocessing.get_context('spawn')
        gate, queue = ctx.Event(), ctx.Queue()
        workers = [ctx.Process(target=parallel_reserve, args=(str(self.path), gate, queue))
                   for _ in range(16)]
        for worker in workers:
            worker.start()
        gate.set()
        outcomes = [queue.get(timeout=30) for _ in workers]
        for worker in workers:
            worker.join(timeout=30)
            self.assertEqual(worker.exitcode, 0)
        self.assertEqual(outcomes.count('reserved'), 10)
        self.assertEqual(outcomes.count('exhausted'), 6)
        snapshot = BudgetLedger(self.path, '0.0000001', card()).snapshot()
        self.assertEqual(snapshot['reserved_nanos'], snapshot['cap_nanos'])
        self.assertEqual(snapshot['available_nanos'], 0)


if __name__ == '__main__':
    unittest.main()
