"""Persistent, fail-closed paid-call reservations. Standard library only.

All workers MUST share the same ledger path. Values passed to reserve/settle are
integer nanodollars, not floating point dollars. Reserve before network I/O;
settle only with complete, authoritative billable usage. A lost response keeps
its full reservation and blocks subsequent calls. Never delete/reset a ledger to
resume a run. This is not a provider-side account spending limit: the cost bound
and supplied rate card must cover every billable component, including reasoning.
"""

from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sqlite3
import time
import uuid

NANOS_PER_USD = 1_000_000_000
MAX_SQL_INT = 2**63 - 1


class BudgetError(RuntimeError):
    """Must propagate out of the experiment loop, not become a skipped trial."""


class BudgetExhausted(BudgetError):
    pass


class BudgetBlocked(BudgetError):
    pass


class BudgetConfigurationError(BudgetError):
    pass


def _decimal(value, name):
    if isinstance(value, bool):
        raise BudgetConfigurationError(f'{name} must be a decimal amount')
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise BudgetConfigurationError(f'{name} must be a decimal amount') from None
    if not number.is_finite() or number < 0:
        raise BudgetConfigurationError(f'{name} must be finite and nonnegative')
    return number


def _integer(value, name, positive=False):
    if (not isinstance(value, int) or isinstance(value, bool) or
            value < int(positive) or value > MAX_SQL_INT):
        raise BudgetConfigurationError(f'{name} must be a bounded nonnegative integer'
                                       + (' greater than zero' if positive else ''))
    return value


def _canonical_decimal(value):
    # Decimal.normalize() uses the ambient precision and could merge distinct
    # high-precision rate cards. Formatting preserves every supplied digit.
    text = format(value, 'f')
    return text.rstrip('0').rstrip('.') if '.' in text else text


class RateCard:
    """Explicit USD-per-million-token rates; there are no default prices.

    Input rate must be an upper bound for all input classes (e.g. use uncached
    rate for a conservative reservation). Output rate must cover billed reasoning
    tokens. Flat fees or other pricing dimensions are unsupported: do not use
    such an endpoint without extending and auditing the cost model first.
    """

    def __init__(self, provider, model, input_usd_per_million,
                 output_usd_per_million,
                 pricing_reference='explicit user-supplied rates'):
        for name, value in [('provider', provider), ('model', model),
                            ('pricing_reference', pricing_reference)]:
            if not isinstance(value, str) or not value.strip():
                raise BudgetConfigurationError(f'{name} is required')
        self.provider = provider
        self.model = model
        self.input_rate = _decimal(input_usd_per_million, 'input rate')
        self.output_rate = _decimal(output_usd_per_million, 'output rate')
        self.pricing_reference = pricing_reference

    def config(self):
        return {'provider': self.provider, 'model': self.model,
                'input_usd_per_million': _canonical_decimal(self.input_rate),
                'output_usd_per_million': _canonical_decimal(self.output_rate),
                'pricing_reference': self.pricing_reference,
                'currency': 'USD', 'unit': 'nanodollars', 'version': 1}

    def cost_nanos(self, input_tokens, output_tokens):
        """Round each charge upwards; caller supplies a conservative token bound."""
        _integer(input_tokens, 'input_tokens')
        _integer(output_tokens, 'output_tokens')
        cost = 0
        for rate, tokens in [(self.input_rate, input_tokens), (self.output_rate, output_tokens)]:
            numerator, denominator = rate.as_integer_ratio()
            # Exact integer arithmetic avoids ambient Decimal precision rounding
            # a tiny positive fractional nanodollar down to an integer boundary.
            cost += (numerator * tokens * 1000 + denominator - 1) // denominator
        return _integer(cost, 'cost_nanos')


class BudgetLedger:
    def __init__(self, path, cap_usd, rate_card):
        self.path = str(Path(path).expanduser().resolve())
        if not isinstance(rate_card, RateCard):
            raise BudgetConfigurationError('An explicit RateCard is required')
        self.rate_card = rate_card
        amount = _decimal(cap_usd, 'cap_usd')
        numerator, denominator = amount.as_integer_ratio()
        cap = numerator * NANOS_PER_USD // denominator
        self.cap_nanos = _integer(cap, 'cap_nanos', positive=True)
        self._config = json.dumps(rate_card.config(), sort_keys=True, separators=(',', ':'))
        # Never make an ephemeral in-memory ledger; a real parent directory is required.
        with self._transaction() as db:
            db.execute('CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY CHECK(id=1), '
                       'cap INTEGER NOT NULL, config TEXT NOT NULL, blocked TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS reservations ('
                       'id TEXT PRIMARY KEY, estimate INTEGER NOT NULL CHECK(estimate>0), '
                       'actual INTEGER, status TEXT NOT NULL, created_ns INTEGER NOT NULL, '
                       'usage TEXT, reason TEXT)')
            row = db.execute('SELECT cap,config FROM budget WHERE id=1').fetchone()
            if row is None:
                db.execute('INSERT INTO budget VALUES (1,?,?,NULL)', (self.cap_nanos, self._config))
            elif row != (self.cap_nanos, self._config):
                raise BudgetConfigurationError('Existing ledger cap/rate-card configuration differs; '
                                               'do not replace the ledger to bypass its cap')

    @contextmanager
    def _transaction(self):
        db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        try:
            db.execute('PRAGMA busy_timeout=30000')
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.execute('COMMIT')
        except BaseException:
            if db.in_transaction:
                db.execute('ROLLBACK')
            raise
        finally:
            db.close()

    @staticmethod
    def _totals(db):
        spent, held = db.execute(
            "SELECT COALESCE(SUM(CASE WHEN status='settled' THEN actual ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN status!='settled' THEN estimate ELSE 0 END),0) "
            'FROM reservations').fetchone()
        return spent, held

    def reserve(self, estimated_cost):
        """Durably reserve integer nanodollars BEFORE a paid request is dispatched."""
        _integer(estimated_cost, 'estimated_cost', positive=True)
        with self._transaction() as db:
            cap, config, blocked = db.execute('SELECT cap,config,blocked FROM budget WHERE id=1').fetchone()
            if (cap, config) != (self.cap_nanos, self._config):
                raise BudgetConfigurationError('Ledger configuration changed')
            if blocked:
                raise BudgetBlocked(blocked)
            spent, held = self._totals(db)
            if spent + held + estimated_cost > cap:
                raise BudgetExhausted('Persistent spending cap cannot cover this reservation')
            reservation = uuid.uuid4().hex
            db.execute('INSERT INTO reservations VALUES (?,?,NULL,?, ?,NULL,NULL)',
                       (reservation, estimated_cost, 'reserved', time.time_ns()))
        return reservation

    def settle(self, reservation_id, actual_cost, usage=None, reason=None):
        """Settle verified cost; None means unknown cost and blocks future calls.

        usage is optional aggregate accounting metadata only, never prompts or
        credentials. Repeating the exact same successful settlement is idempotent.
        A cost above the reservation is recorded but blocks all future requests.
        """
        if actual_cost is not None:
            _integer(actual_cost, 'actual_cost')
        encoded_usage = json.dumps(usage, sort_keys=True, allow_nan=False) if usage is not None else None
        deferred_error = None
        with self._transaction() as db:
            row = db.execute('SELECT estimate,actual,status FROM reservations WHERE id=?',
                             (reservation_id,)).fetchone()
            if row is None:
                raise BudgetConfigurationError('Unknown reservation')
            estimate, recorded_actual, status = row
            if status == 'settled':
                if actual_cost != recorded_actual:
                    raise BudgetConfigurationError('Conflicting repeat settlement')
                blocked = db.execute('SELECT blocked FROM budget WHERE id=1').fetchone()[0]
                if blocked:
                    deferred_error = blocked
            elif status == 'uncertain':
                deferred_error = 'Reservation remains uncertain; ledger requires external reconciliation'
            elif actual_cost is None:
                message = reason or 'Missing or untrusted billable usage; full reservation retained'
                db.execute("UPDATE reservations SET status='uncertain',usage=?,reason=? WHERE id=?",
                           (encoded_usage, message, reservation_id))
                db.execute('UPDATE budget SET blocked=COALESCE(blocked,?) WHERE id=1', (message,))
                deferred_error = message
            else:
                db.execute("UPDATE reservations SET status='settled',actual=?,usage=? WHERE id=?",
                           (actual_cost, encoded_usage, reservation_id))
                if actual_cost > estimate:
                    message = 'Actual cost exceeded its conservative reservation; cost model invalid'
                    db.execute('UPDATE budget SET blocked=COALESCE(blocked,?) WHERE id=1', (message,))
                    deferred_error = message
        if deferred_error:
            raise BudgetBlocked(deferred_error)

    def settle_usage(self, reservation_id, input_tokens, output_tokens):
        """Convenience settlement; incomplete/invalid token usage fails closed."""
        try:
            cost = self.rate_card.cost_nanos(input_tokens, output_tokens)
        except (BudgetConfigurationError, InvalidOperation, OverflowError):
            return self.settle(reservation_id, None, reason='Missing or invalid billable token usage')
        return self.settle(reservation_id, cost,
                           usage={'input_tokens': input_tokens, 'output_tokens': output_tokens})

    def abandon(self, reservation_id, reason='Uncertain request outcome; reservation retained'):
        """No refund on timeout/crash/unknown outcome; retain and block."""
        return self.settle(reservation_id, None, reason=reason)

    def snapshot(self):
        with self._transaction() as db:
            cap, config, blocked = db.execute('SELECT cap,config,blocked FROM budget WHERE id=1').fetchone()
            spent, held = self._totals(db)
            count = db.execute('SELECT COUNT(*) FROM reservations').fetchone()[0]
        return {'path': self.path, 'cap_nanos': cap, 'spent_nanos': spent,
                'reserved_nanos': held, 'available_nanos': max(0, cap-spent-held),
                'blocked': blocked, 'reservations': count, 'config': json.loads(config)}
