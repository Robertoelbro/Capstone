"""A preview flag cannot incorrectly certify the production DB for a load test."""
from unittest.mock import Mock, patch
import unittest

import test_flows as flows
from app.main import app
from app.database import get_db


class QualityMarkerTests(unittest.TestCase):
    setUp = flows.AccountFlows.setUp
    tearDown = flows.AccountFlows.tearDown

    def database(self, name):
        session = Mock()
        session.bind.dialect.name = 'postgresql'
        session.execute.return_value.scalar_one.return_value = name
        app.dependency_overrides[get_db] = lambda: session

    def test_flag_on_sqlite_never_claims_remote_postgresql_isolation(self):
        with patch.dict('os.environ', {'QA_LOAD_RUN_ID': 'a' * 32}):
            response = self.client.get('/health/ready')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('X-BranchIT-QA-Run', response.headers)

    def test_production_database_never_gets_marker_even_with_flag(self):
        self.database('neondb')
        with patch.dict('os.environ', {'QA_LOAD_RUN_ID': 'a' * 32}):
            response = self.client.get('/health/ready')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('X-BranchIT-QA-Run', response.headers)

    def test_only_disposable_postgresql_and_valid_run_id_get_marker(self):
        self.database('branchit_qa_example')
        with patch.dict('os.environ', {'QA_LOAD_RUN_ID': 'a' * 32}):
            response = self.client.get('/health/ready')
        self.assertEqual(response.headers['X-BranchIT-QA-Run'], 'a' * 32)
        with patch.dict('os.environ', {'QA_LOAD_RUN_ID': 'unvalidated-value'}):
            response = self.client.get('/health/ready')
        self.assertNotIn('X-BranchIT-QA-Run', response.headers)
