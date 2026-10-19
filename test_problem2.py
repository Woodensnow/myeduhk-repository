"""Bank account state transitions and validation."""
import copy
import unittest
from problem2 import BankAccount

class TestBankAccount(unittest.TestCase):
    def setUp(self):
        self.account_empty = BankAccount('ACC001', 'Alice', 0, 100)
        self.account_funded = BankAccount('ACC002', 'Bob', 200, 50)

    def assert_state(self, account, balance, status, count):
        self.assertAlmostEqual(account.balance, balance)
        self.assertEqual(account.status, status)
        self.assertEqual(len(account.transaction_history), count)
        self.assertEqual(account.get_summary(), dict(account_id=account.account_id,
            owner=account.owner, balance=round(balance, 2), status=status,
            overdraft_limit=account.overdraft_limit, transaction_count=count))
        if count:
            self.assertAlmostEqual(account.transaction_history[-1]['balance_after'], balance)

    def test_initial_state_multi_attributes(self):
        self.assert_state(self.account_empty, 0, 'ACTIVE', 0)
        self.assert_state(self.account_funded, 200, 'ACTIVE', 1)
        self.assertEqual(self.account_empty.owner, 'Alice')
        self.assertEqual(self.account_empty.overdraft_limit, 100)
        self.assertEqual(self.account_funded.transaction_history[0], dict(
            type='INITIAL_DEPOSIT', amount=200.0, fee=0.0, balance_after=200.0,
            description='Initial account opening deposit'))

    def test_deposit_updates_multiple_attributes(self):
        self.assertTrue(self.account_empty.deposit(150))
        self.assert_state(self.account_empty, 150, 'ACTIVE', 1)
        self.assertEqual(self.account_empty.transaction_history[-1], dict(
            type='DEPOSIT', amount=150.0, fee=0.0, balance_after=150.0,
            description='Deposit of $150.00'))

    def test_withdrawal_within_balance_multi_attributes(self):
        self.assertTrue(self.account_funded.withdraw(50, 2.5))
        self.assert_state(self.account_funded, 147.5, 'ACTIVE', 2)
        transaction = self.account_funded.transaction_history[-1]
        self.assertEqual((transaction['type'], transaction['amount'], transaction['fee']),
                         ('WITHDRAWAL', 50.0, 2.5))

    def test_overdraft_withdrawal_and_status_transition(self):
        self.account_empty.withdraw(50)
        self.assert_state(self.account_empty, -50, 'OVERDRAWN', 1)
        self.account_empty.withdraw(49, 1)
        self.assert_state(self.account_empty, -100, 'OVERDRAWN', 2)
        with self.assertRaises(ValueError):
            self.account_empty.withdraw(0.01)
        self.assert_state(self.account_empty, -100, 'OVERDRAWN', 2)

    def test_deposit_recovering_from_overdrawn_status(self):
        self.account_empty.withdraw(50)
        self.account_empty.deposit(20)
        self.assert_state(self.account_empty, -30, 'OVERDRAWN', 2)
        self.account_empty.deposit(30)
        self.assert_state(self.account_empty, 0, 'ACTIVE', 3)

    def test_transfer_between_accounts_multi_attributes(self):
        self.assertTrue(self.account_funded.transfer_to(self.account_empty, 50, 5))
        self.assert_state(self.account_funded, 145, 'ACTIVE', 2)
        self.assert_state(self.account_empty, 50, 'ACTIVE', 1)
        self.assertEqual(self.account_funded.transaction_history[-1]['fee'], 5)
        self.assertEqual(self.account_empty.transaction_history[-1]['amount'], 50)

    def test_frozen_account_restrictions(self):
        self.account_empty.freeze()
        for operation in (lambda: self.account_empty.deposit(1),
                          lambda: self.account_empty.withdraw(1),
                          lambda: self.account_empty.transfer_to(self.account_funded, 1),
                          lambda: self.account_funded.transfer_to(self.account_empty, 1)):
            with self.assertRaises(RuntimeError):
                operation()
        self.assert_state(self.account_empty, 0, 'FROZEN', 0)
        self.assert_state(self.account_funded, 200, 'ACTIVE', 1)
        self.account_empty.unfreeze()
        self.assert_state(self.account_empty, 0, 'ACTIVE', 0)
        self.account_empty.withdraw(1)
        self.account_empty.freeze()
        self.account_empty.unfreeze()
        self.assert_state(self.account_empty, -1, 'OVERDRAWN', 1)

    def test_invalid_operations_raise_exceptions(self):
        for kwargs in ({'initial_balance': -1}, {'overdraft_limit': -1}):
            with self.assertRaises(ValueError):
                BankAccount('bad', 'Test', **kwargs)
        before = copy.deepcopy(self.account_funded.__dict__)
        for operation in (lambda: self.account_funded.deposit(0),
                          lambda: self.account_funded.deposit(-1),
                          lambda: self.account_funded.withdraw(0),
                          lambda: self.account_funded.withdraw(-1),
                          lambda: self.account_funded.withdraw(1, -1),
                          lambda: self.account_funded.withdraw(250, 0.01),
                          lambda: self.account_funded.transfer_to(self.account_empty, 0),
                          lambda: self.account_funded.transfer_to(self.account_empty, 1, -1),
                          lambda: self.account_funded.transfer_to(self.account_empty, 251)):
            with self.assertRaises(ValueError):
                operation()
            self.assertEqual(self.account_funded.__dict__, before)
            self.assert_state(self.account_empty, 0, 'ACTIVE', 0)
        with self.assertRaises(TypeError):
            self.account_funded.transfer_to('invalid', 1)
        self.assertEqual(self.account_funded.__dict__, before)

if __name__ == '__main__':
    unittest.main()
