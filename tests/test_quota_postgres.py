"""Opt-in integration tests; creates and destroys its own socket-only cluster."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENABLED = os.environ.get('RUN_POSTGRES_TESTS') == '1'

@unittest.skipUnless(ENABLED, 'Set RUN_POSTGRES_TESTS=1 with initdb, pg_ctl and psql available')
class QuotaDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for binary in ('initdb', 'pg_ctl', 'psql', 'postgres'):
            if not shutil.which(binary): raise RuntimeError(f'Missing {binary}; install the complete PostgreSQL server tools')
        if hasattr(os, 'geteuid') and os.geteuid() == 0:
            raise RuntimeError('initdb requires a non-root user')
        cls.tmp = tempfile.TemporaryDirectory(prefix='msq-', dir='/tmp')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.directory = Path(cls.tmp.name)
        cls.cluster = cls.directory / 'data'
        cls.run_command(['initdb', '-D', str(cls.cluster), '-U', 'postgres', '-A', 'trust', '--no-locale'])
        cls.run_command(['pg_ctl', '-D', str(cls.cluster), '-l', str(cls.directory / 'server.log'),
                         '-o', f"-h '' -k {cls.directory} -p 56439", '-w', 'start'])
        cls.addClassCleanup(cls.stop)
        cls.query('''create role anon; create role authenticated; create role service_role bypassrls;
            create schema auth; create table auth.users(id uuid primary key);
            insert into auth.users values ('00000000-0000-0000-0000-000000000001'),
            ('00000000-0000-0000-0000-000000000002');''')
        sql = (ROOT / 'mobile-stack-toolkit/assets/sql/ai-quota.sql').read_text()
        cls.query(sql)
        cls.query(sql)  # repeat application does not reset counters or lose grants

    @classmethod
    def run_command(cls, args, **kwargs):
        return subprocess.run(args, check=True, capture_output=True, text=True, timeout=30, **kwargs).stdout

    @classmethod
    def stop(cls):
        cls.run_command(['pg_ctl', '-D', str(cls.cluster), '-m', 'fast', '-w', 'stop'])

    @classmethod
    def query(cls, sql):
        return cls.run_command(['psql', '-X', '-qAt', '-v', 'ON_ERROR_STOP=1',
                               '-h', str(cls.directory), '-p', '56439', '-U', 'postgres', '-d', 'postgres'], input=sql).strip()

    def setUp(self):
        self.query('truncate public.usage_counters;')

    def test_concurrent_admission_never_exceeds_limit(self):
        sql = "set role service_role; select public.increment_ai_usage('00000000-0000-0000-0000-000000000001',10);"
        with ThreadPoolExecutor(max_workers=16) as pool:
            responses = list(pool.map(lambda _: json.loads(self.query(sql)), range(48)))
        admitted = [r for r in responses if not r['over_limit']]
        self.assertEqual(len(admitted), 10)
        self.assertEqual(sorted(r['count'] for r in admitted), list(range(1, 11)))
        self.assertEqual(self.query('select ai_calls from public.usage_counters'), '10')

    def test_mobile_roles_cannot_spend_or_edit_quota(self):
        for role in ('anon', 'authenticated'):
            for operation in [
                "select public.increment_ai_usage('00000000-0000-0000-0000-000000000001',100)",
                'select * from public.usage_counters',
                'delete from public.usage_counters',
            ]:
                with self.subTest(role=role, operation=operation):
                    with self.assertRaises(subprocess.CalledProcessError) as raised:
                        self.query(f'set role {role}; {operation};')
                    self.assertIn('permission denied', raised.exception.stderr)

    def test_invalid_limits_fail_and_users_are_independent(self):
        for value in ('0', '-1', 'null'):
            with self.assertRaises(subprocess.CalledProcessError):
                self.query(f"select public.increment_ai_usage('00000000-0000-0000-0000-000000000001',{value});")
        for uid in ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002'):
            result = json.loads(self.query(f"select public.increment_ai_usage('{uid}',1);"))
            self.assertEqual(result, {'over_limit': False, 'count': 1})
        self.assertEqual(self.query('select count(*) from public.usage_counters'), '2')

    def test_quota_day_is_utc_and_existing_counts_survive_reapply(self):
        self.query("set timezone = 'Pacific/Kiritimati'; select public.increment_ai_usage('00000000-0000-0000-0000-000000000001',10);")
        self.query((ROOT / 'mobile-stack-toolkit/assets/sql/ai-quota.sql').read_text())
        self.assertEqual(self.query("select ai_calls = 1 and day = (now() at time zone 'UTC')::date from public.usage_counters"), 't')

    def test_all_policy_inherits_using_for_new_rows(self):
        # Regression for the old documentation's incorrect omitted-WITH-CHECK claim.
        self.query('''create table public.ownership_fixture(owner text);
          alter table public.ownership_fixture enable row level security;
          grant select, insert, update on public.ownership_fixture to authenticated;
          create policy owner_only on public.ownership_fixture for all to authenticated
            using (owner = current_setting('test.owner', true));''')
        self.addCleanup(lambda: self.query('drop table public.ownership_fixture'))
        self.query("set role authenticated; set test.owner='alice'; insert into public.ownership_fixture values ('alice');")
        with self.assertRaises(subprocess.CalledProcessError):
            self.query("set role authenticated; set test.owner='alice'; update public.ownership_fixture set owner='bob';")
